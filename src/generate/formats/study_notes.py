"""Study notes generator."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.generate.formats import ContentGenerator
from src.utils.helpers import ensure_directory, format_module_filename
from src.utils.content_analysis import (
    analyze_study_notes, 
    log_content_metrics,
    calculate_quality_score,
    validate_prompt_quality
)
from src.utils.error_collector import ErrorCollector
from src.utils.smart_retry import get_retry_system


logger = logging.getLogger(__name__)


class StudyNotesGenerator(ContentGenerator):
    """Generate study notes/summary for modules."""
    
    def generate_study_notes(
        self,
        module_info: Dict[str, Any],
        lecture_context: str = "",
        max_retries: int = 1,
        error_collector: Optional[ErrorCollector] = None
    ) -> str:
        """Generate concise study notes for a module with automatic retry on validation failures.
        
        Args:
            module_info: Module information dictionary
            lecture_context: Related lecture content for reference
            max_retries: Maximum number of retry attempts (default: 1, total attempts = 2)
            
        Returns:
            Generated study notes as markdown
        """
        module_name = module_info['name']
        session_num = module_info.get('session_number', '?')
        context = f"{module_name} (Session {session_num})"
        logger.info(f"Generating study notes for: {context}")
        
        # Get prompt template
        prompt_config = self.config_loader.get_prompt_template("study_notes")
        system_prompt = prompt_config['system']
        base_template = prompt_config['template']
        
        # Format subtopics, objectives, and key concepts
        subtopics = module_info.get('subtopics', [])
        objectives = module_info.get('learning_objectives', [])
        key_concepts = module_info.get('key_concepts', [])
        
        subtopics_str = "\n".join(f"- {s}" for s in subtopics)
        objectives_str = "\n".join(f"- {o}" for o in objectives)
        key_concepts_str = "\n".join(f"- {c}" for c in key_concepts) if key_concepts else "Not specified"
        
        # Get content requirements from config
        content_reqs = self.config_loader.get_content_requirements()
        notes_reqs = content_reqs.get('study_notes', {})
        
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
            "lecture_summary": lecture_context[:2000] if lecture_context else "Not provided",
            "min_key_concepts": str(notes_reqs.get('min_key_concepts', 3)),
            "max_key_concepts": str(notes_reqs.get('max_key_concepts', 10)),
            "max_word_count": str(notes_reqs.get('max_word_count', 1200)),
            "language": language
        }
        
        # Get smart retry system
        retry_system = get_retry_system()
        
        # Retry loop
        for attempt in range(max_retries + 1):
            if attempt > 0:
                logger.warning(f"  Retry attempt {attempt}/{max_retries} for study notes: {context}")
            
            # Validate prompt quality before generation (proactive validation) - only on first attempt
            if attempt == 0:
                prompt_validation = validate_prompt_quality(
                    base_template,
                    base_variables,
                    "study_notes",
                    requirements=notes_reqs
                )
                if not prompt_validation['is_valid']:
                    logger.warning(f"Prompt quality issues detected (score: {prompt_validation['quality_score']}/100):")
                    for issue in prompt_validation['issues']:
                        logger.warning(f"  [{issue['severity']}] {issue['message']}")
            
            # Prepare template (enhanced on retry)
            template = base_template
            variables = base_variables.copy()
            
            # On retry, use smart retry system for feedback
            if attempt > 0 and 'previous_warnings' in locals():
                # Analyze error pattern
                if previous_warnings:
                    primary_error = previous_warnings[0] if previous_warnings else ""
                    pattern_analysis = retry_system.analyze_error_pattern(primary_error, "study_notes")
                    
                    # Check if we should retry
                    should_retry, strategy = retry_system.should_retry(
                        primary_error,
                        "study_notes",
                        attempt,
                        max_retries
                    )
                    
                    if not should_retry:
                        logger.warning(f"  Smart retry system suggests skipping retry (low success rate)")
                        break
                    
                    # Generate targeted feedback using smart retry system
                    feedback = retry_system.get_retry_feedback(
                        primary_error,
                        "study_notes",
                        previous_warnings,
                        requirements=notes_reqs
                    )
                    
                    if feedback:
                        template = f"{base_template}\n{feedback}"
                
                # Also categorize warnings for additional targeted feedback
                concept_issues = [w for w in previous_warnings if 'key concepts' in w.lower()]
                word_count_issues = [w for w in previous_warnings if 'word count' in w.lower() or 'exceeds maximum' in w.lower()]
                
                # Generate targeted feedback
                feedback_parts = []
                if concept_issues:
                    feedback_parts.append("KEY CONCEPT ISSUES:\n" + "\n".join(f"  - {w}" for w in concept_issues[:3]))
                if word_count_issues:
                    feedback_parts.append("WORD COUNT ISSUES:\n" + "\n".join(f"  - {w}" for w in word_count_issues[:2]))
                
                if feedback_parts:
                    feedback = "\n\n".join(feedback_parts)
                    separator = "═" * 63
                    specific_guidance = []
                    if concept_issues:
                        min_concepts = notes_reqs.get('min_key_concepts', 3)
                        max_concepts = notes_reqs.get('max_key_concepts', 10)
                        specific_guidance.append(f"- Include EXACTLY {min_concepts} to {max_concepts} key concepts using **Concept Name**: format (colon after bold name)")
                        specific_guidance.append("- Format example: - **ATP**: definition (not 'ATP is...' or 'ATP - definition')")
                        # Note: "too many" issues don't trigger retries, but if we're retrying for other reasons,
                        # we can still provide guidance (though this code path won't execute for "too many" alone)
                        too_many_warnings = [w for w in concept_issues if 'too many' in w.lower() or 'excess' in w.lower()]
                        if too_many_warnings:
                            specific_guidance.append(f"- Note: You generated too many key concepts. Consider reducing to {max_concepts} or fewer by:")
                            specific_guidance.append("  • Consolidating related concepts into broader terms")
                            specific_guidance.append("  • Removing less critical or redundant concepts")
                            specific_guidance.append("  • Combining sub-concepts under their parent concept")
                    if word_count_issues:
                        specific_guidance.append(f"- Keep total word count under {notes_reqs.get('max_word_count', 1200)} words")
                    
                    guidance_text = "\n".join(specific_guidance) if specific_guidance else ""
                    template = f"{base_template}\n\n{separator}\nVALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:\n{separator}\n\nThe previous attempt had these issues:\n{feedback}\n\nCRITICAL FIXES REQUIRED:\n{guidance_text}"
            
            # Get operation-specific timeout for study notes generation
            operation_timeout = self.config_loader.get_operation_timeout("study_notes")
            
            # Generate study notes
            content = self.llm_client.generate_with_template(
                template,
                variables,
                system_prompt=system_prompt,
                operation="study_notes",
                timeout_override=operation_timeout
            )
            
            # Add header
            header = f"""# {module_name} - Study Notes

## Key Concepts

"""
            
            notes = header + content
            
            # Analyze and validate
            metrics = analyze_study_notes(notes, requirements=notes_reqs)
            all_warnings = metrics.get('warnings', [])
            
            # Check for critical issues that warrant retry
            # Exclude word count exceedances and "too many" issues (they're warnings, not critical)
            # Only "too few", "missing", or "below minimum" issues should trigger retries
            critical_issues = [
                w for w in all_warnings if any(
                    keyword in w.lower() for keyword in [
                        'missing', 'no key concepts', 'only', 'require', 'need',
                        'too few', 'below minimum'
                    ]
                ) and not any(
                    exclude_keyword in w.lower() for exclude_keyword in [
                        'word count', 'exceeds maximum', 'too many'
                    ]
                )
            ]
            
            # Enhanced logging with format detection details
            logger.debug(f"Study notes analysis for {context}:")
            logger.debug(f"  - Raw content length: {len(content)} chars")
            logger.debug(f"  - Word count: {metrics['word_count']}")
            logger.debug(f"  - Key concepts: {metrics['key_concepts']}")
            logger.debug(f"  - Sections: {metrics['sections']}")
            
            # Calculate quality score
            quality_score_result = calculate_quality_score(metrics, notes_reqs, "study_notes")
            
            # Record attempt in retry system
            success = not critical_issues
            primary_error = critical_issues[0] if critical_issues else ""
            retry_system.record_attempt(
                error_type="validation" if critical_issues else "success",
                error_message=primary_error,
                content_type="study_notes",
                attempt_count=attempt + 1,
                success=success,
                strategy_used="enhanced" if attempt > 0 else "immediate",
                fix_applied=None
            )
            
            # If no critical issues or max retries reached, return
            if not critical_issues or attempt >= max_retries:
                # Standard metrics logging
                log_content_metrics("study_notes", metrics, logger)
                
                # Log quality score
                logger.info(f"Quality score: {quality_score_result['overall_score']:.1f}/100 ({quality_score_result['quality_level']})")
                
                # Add warnings to error collector if provided
                if error_collector and all_warnings:
                    module_id = module_info.get('id')
                    session_num = module_info.get('session_number')
                    context = f"Module {module_id} Session {session_num}" if module_id and session_num else context
                    for warning in all_warnings:
                        severity = 'CRITICAL' if warning in critical_issues else 'WARNING'
                        error_collector.add_warning(
                            type='validation',
                            message=warning,
                            context=context,
                            content_type='study_notes',
                            module_id=module_id,
                            session_num=session_num
                        )
                
                return notes
            
            # Store warnings for next retry
            previous_warnings = all_warnings
            logger.warning(f"  Critical issues detected, will retry: {len(critical_issues)} issues")
            # Log full names of critical issues
            for i, issue in enumerate(critical_issues, 1):
                logger.warning(f"    [CRITICAL] Issue {i}: {issue}")
        
        # Should not reach here, but return last attempt
        return notes
        
    def save_study_notes(
        self,
        notes: str,
        module_info: Dict[str, Any],
        output_dir: Path
    ) -> Path:
        """Save study notes to file.
        
        Args:
            notes: Study notes content
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
            '_study_notes'
        )
        
        filepath = output_dir / filename
        filepath.write_text(notes, encoding='utf-8')
        
        logger.info(f"Saved study notes to: {filepath}")
        return filepath
