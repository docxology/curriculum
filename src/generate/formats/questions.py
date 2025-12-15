"""Question generator for comprehension questions."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.generate.formats import ContentGenerator
from src.utils.helpers import ensure_directory, format_module_filename
from src.utils.error_collector import ErrorCollector
from src.utils.logging_setup import log_status_with_text
from src.utils.content_analysis.question_fixes import auto_fix_questions
from src.utils.smart_retry import get_retry_system, RetryStrategy


logger = logging.getLogger(__name__)


class QuestionGenerator(ContentGenerator):
    """Generate comprehension questions for modules."""
    
    def generate_questions(
        self,
        module_info: Dict[str, Any],
        lecture_context: str = "",
        lab_context: str = "",
        max_retries: int = 1,
        error_collector: Optional[ErrorCollector] = None
    ) -> str:
        """Generate comprehension questions for a module with automatic retry on validation failures.
        
        Args:
            module_info: Module information dictionary
            lecture_context: Related lecture content for context
            lab_context: Related lab content for context
            max_retries: Maximum number of retry attempts (default: 1, total attempts = 2)
            
        Returns:
            Generated questions as markdown
        """
        module_name = module_info['name']
        session_num = module_info.get('session_number', '?')
        context = f"{module_name} (Session {session_num})"
        num_questions = module_info.get('num_questions', 10)
        
        # Pre-generation validation
        if not isinstance(num_questions, int) or num_questions < 1:
            logger.warning(f"Invalid num_questions value: {num_questions}, using default 10")
            num_questions = 10
        
        if not module_info.get('subtopics'):
            logger.warning(f"No subtopics provided for {context}, generation may be less focused")
        
        if not lecture_context and not lab_context:
            logger.warning(f"No lecture or lab context provided for {context}, questions may be less contextual")
        
        logger.info(f"Generating {num_questions} questions for: {context}")
        
        # Get prompt template
        prompt_config = self.config_loader.get_prompt_template("questions")
        system_prompt = prompt_config['system']
        base_template = prompt_config['template']
        
        # Format subtopics and objectives
        subtopics = module_info.get('subtopics', [])
        objectives = module_info.get('learning_objectives', [])
        
        subtopics_str = "\n".join(f"- {s}" for s in subtopics)
        objectives_str = "\n".join(f"- {o}" for o in objectives)
        
        # Distribute questions across types
        mc_count = int(num_questions * 0.5)  # 50% multiple choice
        sa_count = int(num_questions * 0.3)  # 30% short answer
        essay_count = num_questions - mc_count - sa_count  # Rest essay
        
        # Get subject and language from config
        subject = self.config_loader.get_course_subject()
        language = self.config_loader.get_language()
        
        # Prepare base variables
        base_variables = {
            "module_name": module_name,
            "num_questions": str(num_questions),
            "subtopics": subtopics_str,
            "objectives": objectives_str,
            "subject": subject,
            "mc_count": str(mc_count),
            "sa_count": str(sa_count),
            "essay_count": str(essay_count),
            "lecture_summary": lecture_context[:2000] if lecture_context else "Not provided",
            "lab_summary": lab_context[:2000] if lab_context else "Not provided",
            "language": language
        }
        
        # Import analysis functions
        from src.utils.content_analysis import analyze_questions, log_content_metrics
        
        # Get smart retry system
        retry_system = get_retry_system()
        
        # Retry loop
        for attempt in range(max_retries + 1):
            if attempt > 0:
                logger.warning(f"  Retry attempt {attempt}/{max_retries} for questions: {context}")
            
            # Prepare template (enhanced on retry)
            template = base_template
            variables = base_variables.copy()
            
            # On retry, use smart retry system for feedback
            if attempt > 0 and 'previous_warnings' in locals():
                # Analyze error pattern
                if previous_warnings:
                    primary_error = previous_warnings[0] if previous_warnings else ""
                    pattern_analysis = retry_system.analyze_error_pattern(primary_error, "questions")
                    
                    # Check if we should retry
                    should_retry, strategy = retry_system.should_retry(
                        primary_error,
                        "questions",
                        attempt,
                        max_retries
                    )
                    
                    if not should_retry:
                        logger.warning(f"  Smart retry system suggests skipping retry (low success rate)")
                        break
                    
                    # Generate targeted feedback using smart retry system
                    feedback = retry_system.get_retry_feedback(
                        primary_error,
                        "questions",
                        previous_warnings,
                        requirements=None
                    )
                    
                    if feedback:
                        template = f"{base_template}\n{feedback}"
                # Categorize warnings for targeted feedback
                format_issues = [w for w in previous_warnings if any(
                    k in w.lower() for k in ['missing question marks', 'no questions detected', 'format']
                )]
                mc_issues = [w for w in previous_warnings if any(
                    k in w.lower() for k in ['do not have exactly 4 options', 'mc option', 'missing explanations']
                )]
                count_issues = [w for w in previous_warnings if any(
                    k in w.lower() for k in ['only', 'require', 'need', 'missing answers']
                )]
                
                # Generate targeted feedback
                feedback_parts = []
                if format_issues:
                    feedback_parts.append("FORMAT ISSUES:\n" + "\n".join(f"  - {w}" for w in format_issues[:3]))
                if mc_issues:
                    feedback_parts.append("MULTIPLE CHOICE ISSUES:\n" + "\n".join(f"  - {w}" for w in mc_issues[:3]))
                if count_issues:
                    feedback_parts.append("COUNT/COMPLETENESS ISSUES:\n" + "\n".join(f"  - {w}" for w in count_issues[:3]))
                
                if feedback_parts:
                    feedback = "\n\n".join(feedback_parts)
                    separator = "═" * 63
                    specific_guidance = []
                    if format_issues:
                        specific_guidance.append("- Ensure ALL questions use **Question N:** format and end with '?'")
                    if mc_issues:
                        specific_guidance.append("- Ensure ALL MC questions have exactly 4 options (A, B, C, D) and include **Explanation:** sections")
                    if count_issues:
                        specific_guidance.append("- Ensure you generate exactly {num_questions} questions with all required components")
                    
                    guidance_text = "\n".join(specific_guidance) if specific_guidance else ""
                    template = f"{base_template}\n\n{separator}\nVALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:\n{separator}\n\nThe previous attempt had these issues:\n{feedback}\n\nCRITICAL FIXES REQUIRED:\n{guidance_text}"
            
            # Get operation-specific timeout for question generation
            operation_timeout = self.config_loader.get_operation_timeout("questions")
            
            # Generate questions
            content = self.llm_client.generate_with_template(
                template,
                variables,
                system_prompt=system_prompt,
                operation="questions",
                timeout_override=operation_timeout
            )
            
            # Add header
            header = f"""# {module_name} - Comprehension Questions

**Total Questions**: {num_questions}  
**Multiple Choice**: {mc_count} | **Short Answer**: {sa_count} | **Essay**: {essay_count}

---

"""
            
            questions = header + content
            
            # Apply auto-fixes for format issues (only on first attempt)
            fix_summary = {'total_fixes': 0}
            if attempt == 0:
                fixed_questions, fix_summary = auto_fix_questions(questions)
                if fix_summary.get('total_fixes', 0) > 0:
                    logger.info(f"Applied {fix_summary['total_fixes']} auto-fixes to questions")
                    questions = fixed_questions
            
            # Analyze and validate
            metrics = analyze_questions(questions)
            all_warnings = metrics.get('warnings', [])
            
            # Check for critical issues that warrant retry
            critical_issues = [
                w for w in all_warnings if any(
                    keyword in w.lower() for keyword in [
                        'missing question marks', 'missing explanations', 'missing answers',
                        'no questions detected', 'only', 'require', 'need',
                        'do not have exactly 4 options'
                    ]
                )
            ]
            
            # Enhanced critical error logging with structured format
            if critical_issues:
                module_id = module_info.get('id')
                session_num = module_info.get('session_number')
                context_str = f"Module {module_id} Session {session_num}" if module_id and session_num else context
                
                for issue in critical_issues[:3]:  # Log top 3 critical issues
                    # Categorize issue
                    if 'missing question marks' in issue.lower():
                        category = "Format Issue"
                        impact = "Questions may not be properly formatted for parsing"
                        recommendation = "Ensure all questions end with '?' and use **Question N:** format"
                    elif 'missing explanations' in issue.lower():
                        category = "Content Completeness"
                        impact = "Multiple choice questions lack explanations for answers"
                        recommendation = "Add **Explanation:** sections for all MC questions"
                    elif 'do not have exactly 4 options' in issue.lower():
                        category = "Structure Issue"
                        impact = "MC questions may not have standard format"
                        recommendation = "Ensure each MC question has exactly 4 options (A, B, C, D)"
                    else:
                        category = "Validation Issue"
                        impact = "Content may not meet quality standards"
                        recommendation = "Review generated content and regenerate if needed"
                    
                    log_status_with_text(
                        logger,
                        "CRITICAL",
                        f"{category}: {issue}",
                        emoji="🔴",
                        level="WARNING"
                    )
                    logger.warning(f"    Context: {context_str}")
                    logger.warning(f"    Impact: {impact}")
                    logger.warning(f"    Recommendation: {recommendation}")
                    
                    # Add to error collector if provided
                    if error_collector:
                        error_collector.add_error(
                            type='validation',
                            message=issue,
                            severity='CRITICAL',
                            context=context_str,
                            content_type='questions',
                            module_id=module_id,
                            session_num=session_num,
                            metadata={'category': category, 'impact': impact, 'recommendation': recommendation}
                        )
            
            # Enhanced logging with format detection details
            logger.debug(f"Question format analysis for {context}:")
            logger.debug(f"  - Raw content length: {len(content)} chars")
            logger.debug(f"  - Total questions detected: {metrics['total_questions']}")
            logger.debug(f"  - Multiple choice: {metrics['mc_questions']}")
            logger.debug(f"  - Answers found: {metrics['answers_provided']}")
            logger.debug(f"  - Explanations found: {metrics['explanations_provided']}")
            
            # Log format detection issues
            if metrics['total_questions'] == 0:
                logger.warning(f"No questions detected in generated content for {context}")
                logger.debug(f"Content sample (first 500 chars): {content[:500]}")
                logger.info("Expected format: **Question N:** (colon inside bold markers)")
                logger.info("Example: **Question 1:** What is DNA?")
            elif metrics['total_questions'] < num_questions:
                logger.warning(
                    f"Only {metrics['total_questions']} questions detected (expected {num_questions}) "
                    f"for {context}"
                )
                logger.debug(f"Content sample (first 500 chars): {content[:500]}")
            
            # Log format detection success
            if metrics['total_questions'] > 0:
                logger.debug(f"Question format detected successfully: **Question N:** format")
            
            
            # Record attempt in retry system
            success = not critical_issues
            primary_error = critical_issues[0] if critical_issues else ""
            retry_system.record_attempt(
                error_type="validation" if critical_issues else "success",
                error_message=primary_error,
                content_type="questions",
                attempt_count=attempt + 1,
                success=success,
                strategy_used="enhanced" if attempt > 0 else "immediate",
                fix_applied="auto_fix" if attempt == 0 and fix_summary.get('total_fixes', 0) > 0 else None
            )
            
            # If no critical issues or max retries reached, return
            if not critical_issues or attempt >= max_retries:
                # Standard metrics logging
                log_content_metrics("questions", metrics, logger)
                
                # Add all warnings to error collector if provided
                if error_collector and all_warnings:
                    module_id = module_info.get('id')
                    session_num = module_info.get('session_number')
                    context_str = f"Module {module_id} Session {session_num}" if module_id and session_num else context
                    for warning in all_warnings:
                        severity = 'CRITICAL' if warning in critical_issues else 'WARNING'
                        error_collector.add_warning(
                            type='validation',
                            message=warning,
                            context=context_str,
                            content_type='questions',
                            module_id=module_id,
                            session_num=session_num
                        )
                
                return questions
            
            # Store warnings for next retry
            previous_warnings = all_warnings
            logger.warning(f"  Critical issues detected, will retry: {len(critical_issues)} issues")
        
        # Should not reach here, but return last attempt
        return questions
        
    def save_questions(
        self,
        questions: str,
        module_info: Dict[str, Any],
        output_dir: Path
    ) -> Path:
        """Save questions to file.
        
        Args:
            questions: Questions content
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
            '_questions'
        )
        
        filepath = output_dir / filename
        filepath.write_text(questions, encoding='utf-8')
        
        logger.info(f"Saved questions to: {filepath}")
        return filepath

