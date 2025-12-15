"""Diagram generator for Mermaid diagrams."""

import logging
from pathlib import Path
from typing import Optional

from src.generate.formats import ContentGenerator
from src.utils.helpers import ensure_directory, slugify
from src.utils.error_collector import ErrorCollector
from src.utils.logging_setup import log_status_with_text
from src.utils.smart_retry import get_retry_system


logger = logging.getLogger(__name__)


class DiagramGenerator(ContentGenerator):
    """Generate Mermaid diagrams for concepts."""
    
    def generate_diagram(
        self,
        topic: str,
        context: str,
        max_retries: int = 1,
        error_collector: Optional[ErrorCollector] = None,
        module_id: Optional[int] = None,
        session_num: Optional[int] = None
    ) -> str:
        """Generate a Mermaid diagram with automatic retry on validation failures.
        
        Args:
            topic: Topic for the diagram
            context: Context or description
            max_retries: Maximum number of retry attempts (default: 1, total attempts = 2)
            
        Returns:
            Mermaid diagram code
        """
        # Extract module/session context if available in context string
        context_parts = context.split(" - ") if " - " in context else [context]
        logger.info(f"Generating diagram for: {topic} ({context_parts[0] if context_parts else context})")
        
        # Get prompt template
        prompt_config = self.config_loader.get_prompt_template("diagram")
        system_prompt = prompt_config['system']
        base_template = prompt_config['template']
        
        # Get language from config
        language = self.config_loader.get_language()
        
        # Prepare base variables
        base_variables = {
            "topic": topic,
            "context": context,
            "language": language
        }
        
        # Clean up and validation imports
        from src.utils.content_analysis import validate_mermaid_syntax, analyze_visualization, log_content_metrics
        
        # Get content requirements
        content_reqs = self.config_loader.get_content_requirements()
        diagram_reqs = content_reqs.get('diagram', {})
        
        # Get smart retry system
        retry_system = get_retry_system()
        
        # Retry loop
        for attempt in range(max_retries + 1):
            if attempt > 0:
                context_info = context_parts[0] if context_parts else context
                logger.warning(f"  Retry attempt {attempt}/{max_retries} for diagram: {topic} ({context_info})")
            
            # Prepare template (enhanced on retry)
            template = base_template
            variables = base_variables.copy()
            
            # On retry, use smart retry system for feedback
            if attempt > 0 and 'previous_warnings' in locals():
                # Analyze error pattern
                if previous_warnings:
                    primary_error = previous_warnings[0] if previous_warnings else ""
                    pattern_analysis = retry_system.analyze_error_pattern(primary_error, "diagram")
                    
                    # Check if we should retry
                    should_retry, strategy = retry_system.should_retry(
                        primary_error,
                        "diagram",
                        attempt,
                        max_retries
                    )
                    
                    if not should_retry:
                        logger.warning(f"  Smart retry system suggests skipping retry (low success rate)")
                        break
                    
                    # Generate targeted feedback using smart retry system
                    feedback = retry_system.get_retry_feedback(
                        primary_error,
                        "diagram",
                        previous_warnings,
                        requirements=diagram_reqs
                    )
                    
                    if feedback:
                        template = f"{base_template}\n{feedback}"
                
                # Also categorize warnings for additional targeted feedback
                critical_warnings = [w for w in previous_warnings if any(
                    keyword in w.lower() for keyword in [
                        'missing diagram type', 'no connections', 'no nodes',
                        'only', 'require', 'need'
                    ]
                )]
                node_length_warnings = [w for w in previous_warnings if 'exceeds 40 characters' in w.lower() or 'node text exceeds' in w.lower()]
                
                feedback_parts = []
                if critical_warnings:
                    feedback_parts.append("\n\n".join(f"⚠️ ISSUE: {w}" for w in critical_warnings[:3]))
                if node_length_warnings:
                    feedback_parts.append("\n\n".join(f"⚠️ ISSUE: {w}" for w in node_length_warnings[:2]))
                
                if feedback_parts:
                    feedback = "\n\n".join(feedback_parts)
                    separator = "═" * 63
                    guidance_parts = []
                    if node_length_warnings:
                        guidance_parts.append("- CRITICAL: Some node labels exceed 40 characters. You MUST shorten all node labels to 40 characters or less.")
                        guidance_parts.append("  • Use abbreviations where appropriate (e.g., 'ATP Synthase' → 'ATP Synth')")
                        guidance_parts.append("  • Break long concepts into shorter phrases (e.g., 'Mitochondrial Matrix' → 'Mito Matrix')")
                        guidance_parts.append("  • Remove unnecessary words while keeping meaning clear")
                    
                    guidance_text = "\n".join(guidance_parts) if guidance_parts else ""
                    guidance_section = f"\n\nCRITICAL FIXES REQUIRED:\n{guidance_text}" if guidance_text else ""
                    template = f"{base_template}\n\n{separator}\nVALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:\n{separator}\n\nThe previous attempt had these issues that MUST be fixed:\n{feedback}{guidance_section}\n\nPlease fix these issues and regenerate the diagram."
            
            # Get operation-specific timeout for diagram generation
            operation_timeout = self.config_loader.get_operation_timeout("diagram")
            
            # Generate diagram
            diagram = self.llm_client.generate_with_template(
                template,
                variables,
                system_prompt=system_prompt,
                operation="diagram",
                timeout_override=operation_timeout
            )
            
            # Get content requirements for validation
            content_reqs = self.config_loader.get_content_requirements()
            diagram_reqs = content_reqs.get('diagram', {})
            min_nodes = diagram_reqs.get('min_nodes', 10)
            min_connections = diagram_reqs.get('min_connections', 8)
            
            # Clean up and validate
            diagram, cleanup_warnings = validate_mermaid_syntax(diagram, min_nodes=min_nodes, min_connections=min_connections)
            
            # Log cleanup warnings prominently with text labels
            if cleanup_warnings:
                context_info = context_parts[0] if context_parts else context
                logger.warning(f"  Diagram cleanup for {topic} ({context_info}):")
                for warning in cleanup_warnings:
                    # Determine if this is a fix or a warning
                    if 'removed' in warning.lower() or 'fixed' in warning.lower():
                        log_status_with_text(logger, "FIXED", warning, emoji="✓", level="INFO")
                    else:
                        log_status_with_text(logger, "WARNING", warning, emoji="⚠️", level="WARNING")
            
            # Analyze diagram structure
            metrics = analyze_visualization(diagram, requirements=diagram_reqs)
            all_warnings = cleanup_warnings + metrics.get('warnings', [])
            
            # Check for critical issues that warrant retry
            critical_issues = [
                w for w in all_warnings if any(
                    keyword in w.lower() for keyword in [
                        'missing diagram type', 'no connections found', 'no nodes found',
                        'only', 'require at least', 'need'
                    ]
                )
            ]
            
            # Enhanced critical error logging with structured format
            if critical_issues:
                context_info = context_parts[0] if context_parts else context
                context_str = f"Module {module_id} Session {session_num}" if module_id and session_num else context_info
                
                for issue in critical_issues[:3]:  # Log top 3 critical issues
                    # Categorize issue
                    if 'missing diagram type' in issue.lower():
                        category = "Structure Issue"
                        impact = "Diagram may not render correctly without type declaration"
                        recommendation = "Ensure diagram starts with proper Mermaid diagram type (graph, flowchart, etc.)"
                    elif 'no nodes found' in issue.lower() or 'only' in issue.lower() and 'nodes' in issue.lower():
                        category = "Content Issue"
                        impact = "Diagram lacks sufficient nodes for meaningful visualization"
                        recommendation = "Add more nodes to the diagram (minimum 10 nodes required)"
                    elif 'no connections found' in issue.lower():
                        category = "Relationship Issue"
                        impact = "Diagram lacks connections between elements"
                        recommendation = "Add connections/edges between nodes (minimum 8 connections required)"
                    else:
                        category = "Validation Issue"
                        impact = "Diagram may not meet quality standards"
                        recommendation = "Review generated diagram and regenerate if needed"
                    
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
                            content_type='diagram',
                            module_id=module_id,
                            session_num=session_num,
                            metadata={'category': category, 'impact': impact, 'recommendation': recommendation, 'topic': topic}
                        )
            
            # Record attempt in retry system
            success = not critical_issues
            primary_error = critical_issues[0] if critical_issues else ""
            retry_system.record_attempt(
                error_type="validation" if critical_issues else "success",
                error_message=primary_error,
                content_type="diagram",
                attempt_count=attempt + 1,
                success=success,
                strategy_used="enhanced" if attempt > 0 else "immediate",
                fix_applied=None
            )
            
            # If no critical issues or max retries reached, return
            if not critical_issues or attempt >= max_retries:
                # Enhanced logging with format detection details
                context_info = context_parts[0] if context_parts else context
                logger.debug(f"Diagram analysis for {topic} ({context_info}):")
                logger.debug(f"  - Raw diagram length: {len(diagram)} chars")
                logger.debug(f"  - Nodes: {metrics['nodes']}")
                logger.debug(f"  - Connections: {metrics['connections']}")
                logger.debug(f"  - Total elements: {metrics['total_elements']}")
                if metrics.get('mermaid_warnings'):
                    logger.debug(f"  - Mermaid warnings: {len(metrics['mermaid_warnings'])}")
                
                # Standard metrics logging
                log_content_metrics("diagram", metrics, logger)
                
                # Summary of cleanup
                if cleanup_warnings:
                    logger.info(f"  Cleanup summary: {len(cleanup_warnings)} issues fixed (code fences, style commands, etc.)")
                
                logger.info(f"Generated diagram: {len(diagram)} characters")
                
                # Add warnings to error collector if provided
                if error_collector and all_warnings:
                    context_str = f"Module {module_id} Session {session_num}" if module_id and session_num else context_info
                    for warning in all_warnings:
                        severity = 'CRITICAL' if warning in critical_issues else 'WARNING'
                        error_collector.add_warning(
                            type='validation',
                            message=warning,
                            context=context_str,
                            content_type='diagram',
                            module_id=module_id,
                            session_num=session_num,
                            metadata={'topic': topic}
                        )
                
                return diagram
            
            # Store warnings for next retry
            previous_warnings = all_warnings
            logger.warning(f"  Critical issues detected, will retry: {len(critical_issues)} issues")
        
        # Should not reach here, but return last attempt
        return diagram
        
    def save_diagram(
        self,
        diagram: str,
        topic: str,
        module_id: int,
        diagram_num: int,
        output_dir: Path
    ) -> Path:
        """Save diagram to file.
        
        Args:
            diagram: Diagram code
            topic: Topic of the diagram
            module_id: Module ID
            diagram_num: Diagram number within module
            output_dir: Output directory
            
        Returns:
            Path to saved file
        """
        output_dir = Path(output_dir)
        ensure_directory(output_dir)
        
        # Generate filename
        topic_slug = slugify(topic)
        filename = f"diagram_{module_id:02d}_{diagram_num}_{topic_slug}.mmd"
        
        filepath = output_dir / filename
        filepath.write_text(diagram, encoding='utf-8')
        
        logger.info(f"Saved diagram to: {filepath}")
        return filepath


