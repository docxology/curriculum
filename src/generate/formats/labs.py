"""Laboratory exercise generator."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.generate.formats import ContentGenerator
from src.utils.helpers import ensure_directory, format_module_filename
from src.utils.error_collector import ErrorCollector
from src.utils.smart_retry import get_retry_system


logger = logging.getLogger(__name__)


class LabGenerator(ContentGenerator):
    """Generate laboratory exercises for modules."""
    
    def generate_lab(
        self,
        module_info: Dict[str, Any],
        lab_number: int = 1,
        lecture_context: str = "",
        max_retries: int = 1,
        error_collector: Optional[ErrorCollector] = None
    ) -> str:
        """Generate a laboratory exercise for a module with automatic retry on validation failures.
        
        Args:
            module_info: Module information dictionary
            lab_number: Lab number (1, 2, etc.)
            lecture_context: Related lecture content for context
            max_retries: Maximum number of retry attempts (default: 1, total attempts = 2)
            
        Returns:
            Generated lab content as markdown
        """
        module_name = module_info['name']
        session_num = module_info.get('session_number', lab_number)
        context = f"{module_name} (Session {session_num})"
        logger.info(f"Generating lab {lab_number} for: {context}")
        
        # Get prompt template
        prompt_config = self.config_loader.get_prompt_template("lab")
        system_prompt = prompt_config['system']
        template = prompt_config['template']
        
        # Format subtopics and objectives
        subtopics = module_info.get('subtopics', [])
        objectives = module_info.get('learning_objectives', [])
        
        # Use specific subtopic for this lab if available
        lab_focus = subtopics[(lab_number - 1) % len(subtopics)] if subtopics else module_name
        
        subtopics_str = "\n".join(f"- {s}" for s in subtopics)
        objectives_str = "\n".join(f"- {o}" for o in objectives)
        
        # Get subject and language from config
        subject = self.config_loader.get_course_subject()
        language = self.config_loader.get_language()
        
        # Prepare variables with lecture context
        variables = {
            "module_name": module_name,
            "lab_number": str(lab_number),
            "lab_focus": lab_focus,
            "subtopics": subtopics_str,
            "objectives": objectives_str,
            "subject": subject,
            "lecture_summary": lecture_context[:2000] if lecture_context else "Not provided",
            "language": language
        }
        
        # Get smart retry system
        retry_system = get_retry_system()
        
        # Get content requirements
        content_reqs = self.config_loader.get_content_requirements()
        lab_reqs = content_reqs.get('lab', {})
        
        # Retry loop
        for attempt in range(max_retries + 1):
            if attempt > 0:
                logger.warning(f"  Retry attempt {attempt}/{max_retries} for lab: {context}")
            
            # Prepare template (enhanced on retry)
            current_template = template
            current_variables = variables.copy()
            
            # On retry, use smart retry system for feedback
            if attempt > 0 and 'previous_warnings' in locals():
                # Analyze error pattern
                if previous_warnings:
                    primary_error = previous_warnings[0] if previous_warnings else ""
                    pattern_analysis = retry_system.analyze_error_pattern(primary_error, "lab")
                    
                    # Check if we should retry
                    should_retry, strategy = retry_system.should_retry(
                        primary_error,
                        "lab",
                        attempt,
                        max_retries
                    )
                    
                    if not should_retry:
                        logger.warning(f"  Smart retry system suggests skipping retry (low success rate)")
                        break
                    
                    # Generate targeted feedback using smart retry system
                    feedback = retry_system.get_retry_feedback(
                        primary_error,
                        "lab",
                        previous_warnings,
                        requirements=lab_reqs
                    )
                    
                    if feedback:
                        current_template = f"{template}\n{feedback}"
            
            # Get operation-specific timeout for lab generation
            operation_timeout = self.config_loader.get_operation_timeout("lab")
            
            # Generate lab
            content = self.llm_client.generate_with_template(
                current_template,
                current_variables,
                system_prompt=system_prompt,
                operation="lab",
                timeout_override=operation_timeout
            )
            
            # Add header (objectives already in content from prompt)
            header = f"""# {module_name} - Laboratory Exercise {lab_number}

## Lab Focus: {lab_focus}

---

"""
            
            lab = header + content
            
            # Analyze and log with detailed information
            from src.utils.content_analysis import analyze_lab, log_content_metrics
            metrics = analyze_lab(lab)
            
            # Enhanced logging with format detection details
            logger.debug(f"Lab analysis for {context} (Lab {lab_number}):")
            logger.debug(f"  - Raw content length: {len(content)} chars")
            logger.debug(f"  - Word count: {metrics['word_count']}")
            logger.debug(f"  - Procedure steps: {metrics['procedure_steps']}")
            logger.debug(f"  - Safety warnings: {metrics['safety_warnings']}")
            logger.debug(f"  - Materials: {metrics['materials_count']}")
            logger.debug(f"  - Tables: {metrics['tables']}")
            
            # Standard metrics logging
            log_content_metrics("lab", metrics, logger)
            
            # Check for critical issues that warrant retry
            all_warnings = metrics.get('warnings', [])
            critical_issues = [
                w for w in all_warnings if any(
                    keyword in w.lower() for keyword in [
                        'missing', 'no procedure', 'no materials', 'only', 'require', 'need',
                        'too few', 'below minimum'
                    ]
                )
            ]
            
            # Record attempt in retry system
            success = not critical_issues
            primary_error = critical_issues[0] if critical_issues else ""
            retry_system.record_attempt(
                error_type="validation" if critical_issues else "success",
                error_message=primary_error,
                content_type="lab",
                attempt_count=attempt + 1,
                success=success,
                strategy_used="enhanced" if attempt > 0 else "immediate",
                fix_applied=None
            )
            
            # If no critical issues or max retries reached, return
            if not critical_issues or attempt >= max_retries:
                # Add warnings to error collector if provided
                if error_collector and all_warnings:
                    module_id = module_info.get('id')
                    session_num = module_info.get('session_number', lab_number)
                    context_str = f"Module {module_id} Session {session_num}" if module_id else f"Session {session_num}"
                    for warning in all_warnings:
                        severity = 'CRITICAL' if warning in critical_issues else 'WARNING'
                        error_collector.add_warning(
                            type='validation',
                            message=warning,
                            context=context_str,
                            content_type='lab',
                            module_id=module_id,
                            session_num=session_num
                        )
                
                return lab
            
            # Store warnings for next retry
            previous_warnings = all_warnings
            logger.warning(f"  Critical issues detected, will retry: {len(critical_issues)} issues")
            for i, issue in enumerate(critical_issues, 1):
                logger.warning(f"    [CRITICAL] Issue {i}: {issue}")
        
        # Should not reach here, but return last attempt if we do
        return lab
        
    def save_lab(
        self,
        lab: str,
        module_info: Dict[str, Any],
        lab_number: int,
        output_dir: Path
    ) -> Path:
        """Save lab to file.
        
        Args:
            lab: Lab content
            module_info: Module information
            lab_number: Lab number
            output_dir: Output directory
            
        Returns:
            Path to saved file
        """
        output_dir = Path(output_dir)
        ensure_directory(output_dir)
        
        # Generate filename
        filename = format_module_filename(
            module_info['id'],
            module_info['name'],
            f'_lab{lab_number}'
        )
        
        filepath = output_dir / filename
        filepath.write_text(lab, encoding='utf-8')
        
        logger.info(f"Saved lab {lab_number} to: {filepath}")
        return filepath

