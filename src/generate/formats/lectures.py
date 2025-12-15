"""Lecture content generator."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.generate.formats import ContentGenerator
from src.utils.helpers import ensure_directory, format_module_filename
from src.utils.error_collector import ErrorCollector
from src.utils.smart_retry import get_retry_system


logger = logging.getLogger(__name__)


class LectureGenerator(ContentGenerator):
    """Generate lecture content for modules."""
    
    def generate_lecture(
        self, 
        module_info: Dict[str, Any],
        outline_context: str = "",
        session_number: int = 1,
        total_sessions: int = 1,
        session_title: str = "",
        max_retries: int = 1,
        error_collector: Optional[ErrorCollector] = None
    ) -> str:
        """Generate lecture content for a module with automatic retry on validation failures.
        
        Args:
            module_info: Module information dictionary
            outline_context: Course outline context for broader perspective
            session_number: Current session number
            total_sessions: Total number of sessions in course
            session_title: Title of this specific session
            max_retries: Maximum number of retry attempts (default: 1, total attempts = 2)
            
        Returns:
            Generated lecture content as markdown
        """
        module_name = module_info['name']
        logger.info(f"Generating lecture for: {module_name} (Session {session_number}/{total_sessions})")
        
        # Get prompt template
        prompt_config = self.config_loader.get_prompt_template("lecture")
        system_prompt = prompt_config['system']
        base_template = prompt_config['template']
        
        # Format subtopics, objectives, and key concepts as strings
        subtopics = module_info.get('subtopics', [])
        objectives = module_info.get('learning_objectives', [])
        key_concepts = module_info.get('key_concepts', [])
        
        subtopics_str = "\n".join(f"- {s}" for s in subtopics)
        objectives_str = "\n".join(f"- {o}" for o in objectives)
        key_concepts_str = "\n".join(f"- {c}" for c in key_concepts) if key_concepts else "Not specified"
        
        # Get content requirements from config
        content_reqs = self.config_loader.get_content_requirements()
        lecture_reqs = content_reqs.get('lecture', {})
        
        # Get subject and language from config
        subject = self.config_loader.get_course_subject()
        language = self.config_loader.get_language()
        
        # Prepare base variables
        base_variables = {
            "module_name": module_name,
            "subtopics": subtopics_str,
            "objectives": objectives_str,
            "key_concepts": key_concepts_str,
            "subject": subject,
            "content_length": str(module_info.get('content_length', 2000)),
            "outline_context": outline_context[:50000] if outline_context else "Not provided",  # 128K context window allows full context
            "session_number": str(session_number),
            "total_sessions": str(total_sessions),
            "session_title": session_title or module_name,
            "min_examples": str(lecture_reqs.get('min_examples', 5)),
            "max_examples": str(lecture_reqs.get('max_examples', 15)),
            "min_sections": str(lecture_reqs.get('min_sections', 4)),
            "max_sections": str(lecture_reqs.get('max_sections', 8)),
            "min_word_count": str(lecture_reqs.get('min_word_count', 1000)),
            "max_word_count": str(lecture_reqs.get('max_word_count', 1500)),
            "language": language
        }
        
        # Import analysis functions
        from src.utils.content_analysis import (
            analyze_lecture, 
            log_content_metrics,
            validate_prompt_quality,
            calculate_quality_score
        )
        
        # Get smart retry system
        retry_system = get_retry_system()
        
        # Retry loop
        for attempt in range(max_retries + 1):
            # Validate prompt quality before generation (proactive validation) - only on first attempt
            if attempt == 0:
                prompt_validation = validate_prompt_quality(
                    base_template,
                    base_variables,
                    "lecture",
                    requirements=lecture_reqs
                )
                if not prompt_validation['is_valid']:
                    logger.warning(f"Prompt quality issues detected (score: {prompt_validation['quality_score']}/100):")
                    for issue in prompt_validation['issues']:
                        logger.warning(f"  [{issue['severity']}] {issue['message']}")
                    if prompt_validation['suggestions']:
                        logger.info("Suggestions:")
                        for suggestion in prompt_validation['suggestions']:
                            logger.info(f"  - {suggestion}")
            if attempt > 0:
                logger.warning(f"  Retry attempt {attempt}/{max_retries} for lecture: {module_name} (Session {session_number})")
            
            # Prepare template (enhanced on retry)
            template = base_template
            variables = base_variables.copy()
            
            # On retry, use smart retry system for feedback
            if attempt > 0 and 'previous_warnings' in locals():
                # Analyze error pattern
                if previous_warnings:
                    primary_error = previous_warnings[0] if previous_warnings else ""
                    pattern_analysis = retry_system.analyze_error_pattern(primary_error, "lecture")
                    
                    # Check if we should retry
                    should_retry, strategy = retry_system.should_retry(
                        primary_error,
                        "lecture",
                        attempt,
                        max_retries
                    )
                    
                    if not should_retry:
                        logger.warning(f"  Smart retry system suggests skipping retry (low success rate)")
                        break
                    
                    # Generate targeted feedback using smart retry system
                    feedback = retry_system.get_retry_feedback(
                        primary_error,
                        "lecture",
                        previous_warnings,
                        requirements=lecture_reqs
                    )
                    
                    if feedback:
                        template = f"{base_template}\n{feedback}"
                
                # Also categorize warnings for additional targeted feedback
                word_count_issues = [w for w in previous_warnings if 'word count' in w.lower()]
                example_issues = [w for w in previous_warnings if 'examples' in w.lower()]
                section_issues = [w for w in previous_warnings if 'sections' in w.lower() or 'section' in w.lower()]
                
                # Generate targeted feedback
                feedback_parts = []
                if word_count_issues:
                    feedback_parts.append("WORD COUNT ISSUES:\n" + "\n".join(f"  - {w}" for w in word_count_issues[:2]))
                if example_issues:
                    feedback_parts.append("EXAMPLE ISSUES:\n" + "\n".join(f"  - {w}" for w in example_issues[:2]))
                if section_issues:
                    feedback_parts.append("SECTION ISSUES:\n" + "\n".join(f"  - {w}" for w in section_issues[:2]))
                
                if feedback_parts:
                    feedback = "\n\n".join(feedback_parts)
                    separator = "═" * 63
                    specific_guidance = []
                    if word_count_issues:
                        specific_guidance.append(f"- Ensure word count is {lecture_reqs.get('min_word_count', 1000)}-{lecture_reqs.get('max_word_count', 1500)} words")
                    if example_issues:
                        specific_guidance.append(f"- Include {lecture_reqs.get('min_examples', 5)}-{lecture_reqs.get('max_examples', 15)} examples using phrases: 'for example', 'for instance', 'such as', 'consider', 'imagine'")
                        specific_guidance.append("- Make examples specific and concrete (e.g., 'ATP hydrolysis releases 7.3 kcal/mol' not 'energy is released')")
                    if section_issues:
                        specific_guidance.append(f"- Create {lecture_reqs.get('min_sections', 4)}-{lecture_reqs.get('max_sections', 8)} major sections using ## headings (### subsections don't count)")
                    
                    guidance_text = "\n".join(specific_guidance) if specific_guidance else ""
                    template = f"{base_template}\n\n{separator}\nVALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:\n{separator}\n\nThe previous attempt had these issues:\n{feedback}\n\nCRITICAL FIXES REQUIRED:\n{guidance_text}"
            
            # Get operation-specific timeout for lecture generation
            operation_timeout = self.config_loader.get_operation_timeout("lecture")
            
            # Generate lecture
            content = self.llm_client.generate_with_template(
                template,
                variables,
                system_prompt=system_prompt,
                operation="lecture",
                timeout_override=operation_timeout
            )
            
            # Add header
            header = f"""# {module_name}

## Learning Objectives

{objectives_str}

---

"""
            
            lecture = header + content
            
            # Analyze and validate
            metrics = analyze_lecture(lecture, requirements=lecture_reqs)
            all_warnings = metrics.get('warnings', [])
            
            # Check for critical issues that warrant retry
            # Exclude word count exceedances (they're warnings, not critical)
            critical_issues = [
                w for w in all_warnings if any(
                    keyword in w.lower() for keyword in [
                        'missing', 'no examples', 'no sections', 'only', 'require', 'need',
                        'too few', 'below minimum'
                    ]
                ) and not any(
                    exclude_keyword in w.lower() for exclude_keyword in [
                        'word count', 'exceeds maximum'
                    ]
                )
            ]
            
            # Enhanced logging with format detection details
            logger.debug(f"Lecture analysis for {module_name} (Session {session_number}):")
            logger.debug(f"  - Raw content length: {len(content)} chars")
            logger.debug(f"  - Word count: {metrics['word_count']}")
            logger.debug(f"  - Sections: {metrics['sections']}")
            logger.debug(f"  - Examples: {metrics['examples']}")
            logger.debug(f"  - Terms defined: {metrics['terms']}")
            
            # Calculate quality score
            quality_score_result = calculate_quality_score(metrics, lecture_reqs, "lecture")
            
            # Record attempt in retry system
            success = not critical_issues
            primary_error = critical_issues[0] if critical_issues else ""
            retry_system.record_attempt(
                error_type="validation" if critical_issues else "success",
                error_message=primary_error,
                content_type="lecture",
                attempt_count=attempt + 1,
                success=success,
                strategy_used="enhanced" if attempt > 0 else "immediate",
                fix_applied=None
            )
            
            # If no critical issues or max retries reached, return
            if not critical_issues or attempt >= max_retries:
                # Standard metrics logging
                log_content_metrics("lecture", metrics, logger)
                
                # Log quality score
                logger.info(f"Quality score: {quality_score_result['overall_score']:.1f}/100 ({quality_score_result['quality_level']})")
                
                # Add warnings to error collector if provided
                if error_collector and all_warnings:
                    module_id = module_info.get('id')
                    context = f"Module {module_id} Session {session_number}" if module_id else f"Session {session_number}"
                    for warning in all_warnings:
                        severity = 'CRITICAL' if warning in critical_issues else 'WARNING'
                        error_collector.add_warning(
                            type='validation',
                            message=warning,
                            context=context,
                            content_type='lecture',
                            module_id=module_id,
                            session_num=session_number
                        )
                
                return lecture
            
            # Store warnings for next retry
            previous_warnings = all_warnings
            logger.warning(f"  Critical issues detected, will retry: {len(critical_issues)} issues")
            # Log full names of critical issues
            for i, issue in enumerate(critical_issues, 1):
                logger.warning(f"    [CRITICAL] Issue {i}: {issue}")
        
        # Should not reach here, but return last attempt
        return lecture
        
    def save_lecture(
        self,
        lecture: str,
        module_info: Dict[str, Any],
        output_dir: Path
    ) -> Path:
        """Save lecture to file.
        
        Args:
            lecture: Lecture content
            module_info: Module information
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
            '_lecture'
        )
        
        filepath = output_dir / filename
        filepath.write_text(lecture, encoding='utf-8')
        
        logger.info(f"Saved lecture to: {filepath}")
        return filepath

