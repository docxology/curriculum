"""Outline generator for educational courses.

This module generates comprehensive course outlines using an LLM based on
configuration files. Generates JSON-structured outlines and formats them
as markdown for human consumption.
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.utils.helpers import ensure_directory, format_timestamp
from src.utils.logging_setup import (
    log_section_header,
    log_parameters,
    log_validation_results,
)
from src.generate.stages.outline_quality import (
    validate_outline_quality,
    detect_topic_overlap,
    validate_learning_progression,
    validate_balance,
    calculate_quality_score
)


logger = logging.getLogger(__name__)


class OutlineGenerator:
    """Generates course outlines using LLM.
    
    This class takes course configuration and uses an LLM to generate
    detailed, structured course outlines.
    
    Attributes:
        config_loader: Configuration loader instance
        llm_client: LLM client for text generation
    """
    
    def __init__(self, config_loader: ConfigLoader, llm_client: OllamaClient):
        """Initialize the outline generator.
        
        Args:
            config_loader: Configuration loader instance
            llm_client: LLM client instance
        """
        self.config_loader = config_loader
        self.llm_client = llm_client
        
        logger.info("Initialized OutlineGenerator")
        
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response, handling potential markdown wrapping.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        # Try to find JSON in markdown code blocks first
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            json_str = match.group(1)
        else:
            # Try to find raw JSON (look for { ... } pattern)
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response, re.DOTALL)
            if match:
                json_str = match.group(0)
            else:
                json_str = response.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            logger.debug(f"Attempted to parse: {json_str[:500]}...")
            return None
    
    def _normalize_session_numbering(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure session numbers are sequential and global (1-N) across all modules.
        
        Args:
            data: Parsed JSON outline data
            
        Returns:
            Updated data with corrected session numbering
        """
        session_counter = 1
        modules = data['modules']
        
        for module in modules:
            for session in module['sessions']:
                session['session_number'] = session_counter
                session_counter += 1
        
        logger.info(f"Normalized session numbering: 1-{session_counter - 1} across {len(modules)} modules")
        return data
    
    def _validate_outline_json(self, data: Dict[str, Any], expected_modules: int) -> bool:
        """Validate the structure and completeness of outline JSON.
        
        Args:
            data: Parsed JSON data
            expected_modules: Expected number of modules
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            logger.error("Outline data is not a dictionary")
            return False
        
        # Check for required top-level keys
        if 'course_metadata' not in data or 'modules' not in data:
            logger.error("Missing required top-level keys: course_metadata or modules")
            return False
        
        # Validate course metadata
        metadata = data['course_metadata']
        required_metadata = ['name', 'level', 'duration_weeks', 'total_sessions', 'total_modules']
        for field in required_metadata:
            if field not in metadata:
                logger.error(f"Missing metadata field: {field}")
                return False
        
        # Validate module count
        modules = data['modules']
        if not isinstance(modules, list):
            logger.error("Modules is not a list")
            return False
        
        # Validate that all modules are dictionaries before accessing them
        for i, module in enumerate(modules):
            if not isinstance(module, dict):
                logger.error(f"Module {i} is not a dictionary")
                return False
        
        actual_count = len(modules)
        if actual_count != expected_modules:
            logger.warning(f"Module count mismatch: expected {expected_modules}, got {actual_count}")
            # Update metadata to reflect actual count
            metadata['total_modules'] = actual_count
            logger.info(f"Updated course_metadata.total_modules to {actual_count}")
        
        # Validate and update session count in metadata
        # Now safe to access .get() since we've validated all modules are dicts
        actual_sessions = sum(len(m.get('sessions', [])) for m in modules)
        metadata_sessions = metadata.get('total_sessions', 0)
        if actual_sessions != metadata_sessions:
            logger.warning(f"Session count mismatch in metadata: metadata says {metadata_sessions}, actual is {actual_sessions}")
            metadata['total_sessions'] = actual_sessions
            logger.info(f"Updated course_metadata.total_sessions to {actual_sessions}")
        
        # Validate each module structure (already checked types above, but validate required fields)
        for i, module in enumerate(modules):
            
            required_fields = ['module_id', 'module_name', 'sessions']
            for field in required_fields:
                if field not in module:
                    logger.error(f"Module {i} missing field: {field}")
                    return False
            
            # Validate sessions
            if not isinstance(module['sessions'], list) or len(module['sessions']) == 0:
                logger.error(f"Module {i} has no sessions or sessions is not a list")
                return False
            
            for j, session in enumerate(module['sessions']):
                if not isinstance(session, dict):
                    logger.error(f"Module {i}, Session {j} is not a dictionary")
                    return False
                
                required_session_fields = ['session_number', 'session_title', 'subtopics', 
                                          'learning_objectives', 'key_concepts', 'rationale']
                for field in required_session_fields:
                    if field not in session:
                        logger.error(f"Module {i}, Session {j} missing field: {field}")
                        return False
        
        logger.info("Outline JSON validation successful")
        return True
    
    def _format_json_as_markdown(self, data: Dict[str, Any]) -> str:
        """Convert JSON outline to formatted markdown.
        
        Args:
            data: Parsed JSON outline data
            
        Returns:
            Formatted markdown string
        """
        lines = []
        metadata = data['course_metadata']
        modules = data['modules']
        
        # Course overview
        lines.append(f"# {metadata['name']} - Course Outline")
        lines.append("")
        lines.append(f"**Level**: {metadata['level']}")
        if metadata.get('duration_weeks'):
            lines.append(f"**Duration**: {metadata['duration_weeks']} weeks")
        lines.append(f"**Total Class Sessions**: {metadata['total_sessions']}")
        lines.append(f"**Total Modules**: {metadata['total_modules']}")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Module and session details
        for module in modules:
            module_id = module['module_id']
            module_name = module['module_name']
            sessions = module['sessions']
            
            lines.append(f"## Module {module_id}: {module_name}")
            lines.append("")
            lines.append(f"**Sessions**: {len(sessions)}")
            lines.append("")
            
            for session in sessions:
                session_num = session['session_number']
                session_title = session['session_title']
                
                lines.append(f"### Session {session_num}: {session_title}")
                lines.append("")
                
                # Subtopics
                if session.get('subtopics'):
                    lines.append("**Subtopics:**")
                    for subtopic in session['subtopics']:
                        lines.append(f"- {subtopic}")
                    lines.append("")
                
                # Learning objectives
                if session.get('learning_objectives'):
                    lines.append("**Learning Objectives:**")
                    for i, objective in enumerate(session['learning_objectives'], 1):
                        lines.append(f"{i}. {objective}")
                    lines.append("")
                
                # Key concepts
                if session.get('key_concepts'):
                    lines.append("**Key Concepts:**")
                    for concept in session['key_concepts']:
                        lines.append(f"- {concept}")
                    lines.append("")
                
                # Rationale
                if session.get('rationale'):
                    lines.append(f"**Rationale:** {session['rationale']}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        return "\n".join(lines)
    
    def _calculate_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics from outline JSON.
        
        Args:
            data: Parsed JSON outline data
            
        Returns:
            Dictionary of statistics
        """
        modules = data['modules']
        total_sessions = 0
        total_objectives = 0
        total_concepts = 0
        session_numbers = []
        
        for module in modules:
            for session in module['sessions']:
                total_sessions += 1
                session_numbers.append(session['session_number'])
                total_objectives += len(session.get('learning_objectives', []))
                total_concepts += len(session.get('key_concepts', []))
        
        return {
            'total_modules': len(modules),
            'total_sessions': total_sessions,
            'total_objectives': total_objectives,
            'total_concepts': total_concepts,
            'avg_objectives_per_session': total_objectives / total_sessions if total_sessions > 0 else 0,
            'avg_concepts_per_session': total_concepts / total_sessions if total_sessions > 0 else 0,
            'avg_sessions_per_module': total_sessions / len(modules) if len(modules) > 0 else 0,
            'session_numbers_range': f"{min(session_numbers)}-{max(session_numbers)}" if session_numbers else "N/A"
        }
        
    def generate_outline(
        self,
        num_modules: Optional[int] = None,
        total_sessions: Optional[int] = None,
        bounds_override: Optional[Dict[str, Dict[str, int]]] = None
    ) -> str:
        """Generate course outline using LLM with JSON structure.
        
        Args:
            num_modules: Number of modules to generate (default: from config)
            total_sessions: Total class sessions (default: from config or calculated)
            bounds_override: Override min/max for fields (default: from config)
        
        Returns:
            Generated outline as markdown string (converted from JSON)
        """
        log_section_header(logger, "OUTLINE GENERATION PROCESS (JSON-STRUCTURED)", major=True)
        
        # Get course information
        course_info = self.config_loader.get_course_info()
        
        # Get number of modules from parameter or config
        if num_modules is not None:
            expected_module_count = num_modules
        else:
            defaults = self.config_loader.get_course_defaults()
            expected_module_count = defaults.get('num_modules', 5)
        
        # Log comprehensive course information
        logger.info(f"Course Title: '{course_info['name']}'")
        logger.info(f"Course Level: '{course_info.get('level', 'Not specified')}'")
        if course_info.get('estimated_duration_weeks'):
            logger.info(f"Duration: {course_info['estimated_duration_weeks']} weeks")
        logger.info(f"Description: {len(course_info.get('description', ''))} characters")
        logger.info(f"Modules to Generate: {expected_module_count}")
        logger.info("Topic Areas: LLM will generate based on course description and constraints")
        
        if course_info.get('additional_constraints'):
            logger.info(f"Additional Constraints: {course_info['additional_constraints'][:100]}...")
        
        # Determine session count - use parameter or get from config
        if total_sessions is not None:
            requested_sessions = total_sessions
        else:
            defaults = self.config_loader.get_course_defaults()
            requested_sessions = defaults.get('total_sessions', expected_module_count * 3)
        
        try:
            requested_sessions = int(requested_sessions)
        except (ValueError, TypeError):
            logger.warning(f"Invalid total_class_sessions value: {requested_sessions}, calculating from modules")
            defaults = self.config_loader.get_course_defaults()
            sessions_per_module = defaults.get('sessions_per_module', 1)
            requested_sessions = int(expected_module_count * sessions_per_module)
        
        # Validate session/module configuration
        log_section_header(logger, "SESSION/MODULE CONFIGURATION", major=True)
        logger.info(f"Modules: {expected_module_count}")
        logger.info(f"Total Sessions: {requested_sessions}")
        logger.info(f"Average: {requested_sessions / expected_module_count:.2f} sessions per module")
        
        if requested_sessions < expected_module_count:
            logger.warning(f"⚠️  Sessions < module count (avg {requested_sessions/expected_module_count:.2f}/module)")
            logger.warning("⚠️  Some modules may be combined or abbreviated")
        elif requested_sessions > expected_module_count * 2:
            logger.info(f"✓ Multiple sessions per module (avg {requested_sessions/expected_module_count:.1f})")
        else:
            logger.info("✓ Balanced distribution")
        
        logger.info("═" * 80)
        
        # Use requested sessions directly (no adjustment)
        final_sessions = requested_sessions
        
        # Get prompt template
        prompt_config = self.config_loader.get_prompt_template("outline")
        system_prompt = prompt_config['system']
        template = prompt_config['template']
        
        # Get bounds (use override or config defaults)
        if bounds_override:
            bounds = bounds_override
        else:
            bounds = self.config_loader.get_outline_bounds()
        
        # Extract min/max for each field
        min_subtopics = bounds['subtopics'].get('min', 3)
        max_subtopics = bounds['subtopics'].get('max', 7)
        min_objectives = bounds['learning_objectives'].get('min', 3)
        max_objectives = bounds['learning_objectives'].get('max', 7)
        min_concepts = bounds['key_concepts'].get('min', 3)
        max_concepts = bounds['key_concepts'].get('max', 7)
        
        log_section_header(logger, "OUTLINE GENERATION ITEM BOUNDS", major=True)
        logger.info(f"  • Subtopics per session: {min_subtopics}-{max_subtopics}")
        logger.info(f"  • Learning objectives per session: {min_objectives}-{max_objectives}")
        logger.info(f"  • Key concepts per session: {min_concepts}-{max_concepts}")
        logger.info("═" * 80)
        
        # Calculate average sessions per module
        avg_sessions_per_module = final_sessions / expected_module_count
        
        # Get language from config
        language = self.config_loader.get_language()
        
        # Format prompt with ALL available variables
        variables = {
            "course_name": course_info['name'],
            "course_level": course_info.get('level', 'Not specified'),
            "course_description": course_info.get('description', ''),
            "course_duration": course_info.get('estimated_duration_weeks', 'Not specified'),
            "subject": course_info.get('subject', 'general education'),
            "total_sessions": final_sessions,
            "additional_constraints": course_info.get('additional_constraints', 'None specified'),
            "num_modules": expected_module_count,
            "avg_sessions_per_module": f"{avg_sessions_per_module:.1f}",
            "min_subtopics": min_subtopics,
            "max_subtopics": max_subtopics,
            "min_objectives": min_objectives,
            "max_objectives": max_objectives,
            "min_concepts": min_concepts,
            "max_concepts": max_concepts,
            "language": language
        }
        
        # Log generation parameters
        log_section_header(logger, "LLM GENERATION PARAMETERS", major=True)
        
        logger.info("Model Configuration:")
        logger.info(f"  • Model: {self.llm_client.model}")
        logger.info("  • Format: JSON structured")
        logger.info(f"  • Prompt: '{system_prompt[:80]}...'")
        logger.info("")
        
        # Log template variables
        log_parameters(logger, variables, "Template Variables")
        
        # Validate template variables
        required_vars, missing_vars, extra_vars = self.llm_client._validate_template_variables(
            template, variables
        )
        logger.info("")
        log_validation_results(logger, required_vars, set(variables.keys()), missing_vars, extra_vars)
        
        logger.info("═" * 80)
        
        # Generate using LLM
        logger.info("Sending JSON generation request to LLM...")
        logger.info(f"Requesting structured outline for: '{course_info['name']}'")
        logger.info(f"Generating {expected_module_count} modules with {final_sessions} total sessions")
        
        # Log prompt details before generation
        formatted_prompt = self.llm_client.format_prompt(template, variables)
        logger.info(f"Formatted prompt size: {len(formatted_prompt)} characters")
        logger.info(f"System prompt size: {len(system_prompt)} characters" if system_prompt else "No system prompt")
        logger.info(f"Template variables: {len(variables)} variables provided")
        
        # Log generation parameters
        llm_params = self.config_loader.get_llm_parameters()
        logger.info(f"LLM model: {llm_params.get('model', 'unknown')}")
        
        # Get operation-specific timeout for outline generation
        operation_timeout = self.config_loader.get_operation_timeout("outline")
        base_timeout = llm_params.get('timeout', 180)
        if operation_timeout != base_timeout:
            logger.info(f"LLM timeout: {operation_timeout}s (operation-specific, base: {base_timeout}s)")
        else:
            logger.info(f"LLM timeout: {operation_timeout}s")
        logger.info(f"LLM API URL: {llm_params.get('api_url', 'unknown')}")
        
        # Optimize parameters for outline generation to improve performance
        # - num_ctx: 32000 (reduced from 128K) - outline prompts are ~400-500 tokens, 32K is sufficient
        # - num_predict: 4000 (reduced from 64K) - typical outline JSON is 2-4K tokens
        # These optimizations significantly improve generation speed
        outline_params = {
            "num_ctx": 32000,
            "num_predict": 4000
        }
        logger.info(f"Using optimized parameters for outline generation: num_ctx=32000, num_predict=4000 (reduced from default 128K/64K for faster generation)")
        
        # Check Ollama connection and performance before generation
        logger.info("Checking Ollama service connection and performance...")
        is_connected, response_time = self.llm_client.check_connection(timeout=5)
        if not is_connected:
            error_msg = (
                "Ollama service is not reachable. Please check: "
                "1. Ollama is running: 'ollama serve' or check service status\n"
                "2. Service is accessible: curl http://localhost:11434/api/version\n"
                "3. Model is available: ollama list"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        
        if response_time is not None:
            if response_time > 1.0:
                logger.warning(
                    f"Ollama connection check completed but response time is slow: {response_time:.2f}s "
                    f"(expected <1s). This may indicate system resource constraints or Ollama performance issues. "
                    f"Generation may be slower than expected."
                )
            else:
                logger.info(f"Ollama connection check successful (response time: {response_time:.3f}s)")
        
        # Check GPU usage for performance diagnostics
        logger.info("Checking GPU acceleration status...")
        gpu_info = self.llm_client.check_gpu_usage()
        if gpu_info["models_loaded"]:
            if gpu_info["using_gpu"]:
                logger.info(f"GPU acceleration active: {gpu_info['processor_info']}")
            else:
                logger.warning(
                    f"CPU-only mode detected: {gpu_info['processor_info']}. "
                    f"Generation will be significantly slower. "
                    f"Consider checking Ollama Metal support or restarting Ollama."
                )
        else:
            logger.debug("No models currently loaded (GPU will be used when model loads)")
        
        # Track generation time
        generation_start = time.time()
        
        try:
            raw_response = self.llm_client.generate_with_template(
                template,
                variables,
                system_prompt=system_prompt,
                params=outline_params,
                operation="outline",
                timeout_override=operation_timeout
            )
            
            generation_time = time.time() - generation_start
            
            logger.info(f"LLM generation completed (received {len(raw_response)} characters)")
            logger.info(f"Generation took {generation_time:.2f} seconds")
            
            # Performance diagnostics
            chars_per_sec = len(raw_response) / generation_time if generation_time > 0 else 0
            logger.info(f"Generation rate: {chars_per_sec:.1f} chars/s")
            
            # Log performance assessment
            if generation_time > 120:
                logger.warning(
                    f"Generation took {generation_time:.2f}s (expected 30-60s for outlines). "
                    f"This may indicate Ollama performance issues or system resource constraints. "
                    f"Consider checking Ollama logs or system resources."
                )
            elif generation_time > 60:
                logger.info(
                    f"Generation took {generation_time:.2f}s (slightly longer than expected 30-60s, but acceptable)"
                )
            else:
                logger.info(f"Generation performance: {generation_time:.2f}s (within expected range)")
            
        except Exception as e:
            generation_time = time.time() - generation_start
            logger.error(f"LLM generation failed after {generation_time:.2f} seconds: {e}")
            
            # Performance diagnostics for failures
            if generation_time >= operation_timeout * 0.9:  # Within 90% of timeout
                logger.error(
                    f"Generation timed out after {generation_time:.2f}s (timeout limit: {operation_timeout}s). "
                    f"This suggests Ollama is not responding or model is too slow. "
                    f"Diagnostics:\n"
                    f"  1. Check Ollama service: curl http://localhost:11434/api/version\n"
                    f"  2. Check system resources (CPU/memory): top or htop\n"
                    f"  3. Try restarting Ollama: pkill ollama && ollama serve\n"
                    f"  4. Consider using a faster model or reducing prompt complexity"
                )
            else:
                logger.error(
                    "Check Ollama service status and model availability. "
                    f"Generation failed after {generation_time:.2f}s (timeout: {operation_timeout}s)"
                )
            raise
        
        # Parse JSON from response
        logger.info("-" * 80)
        logger.info("Parsing JSON response...")
        outline_data = self._extract_json_from_response(raw_response)
        
        if outline_data is None:
            logger.error("Failed to extract valid JSON from LLM response")
            logger.error(f"Raw response preview: {raw_response[:500]}...")
            raise ValueError("LLM did not return valid JSON. Check logs for details.")
        
        logger.info("JSON parsed successfully")
        
        # Validate outline structure
        logger.info("Validating outline structure...")
        if not self._validate_outline_json(outline_data, expected_module_count):
            raise ValueError("Generated outline JSON failed validation. Check logs for details.")
        
        # Normalize session numbering to be global (1-N)
        logger.info("Normalizing session numbering to global sequence...")
        outline_data = self._normalize_session_numbering(outline_data)
        
        # Add course_template to course_metadata if available
        course_template = self.config_loader.get_current_course_template()
        if course_template:
            if 'course_metadata' not in outline_data:
                outline_data['course_metadata'] = {}
            outline_data['course_metadata']['course_template'] = course_template
            logger.debug(f"Added course_template '{course_template}' to course_metadata")
        
        # Run quality validation
        logger.info("Running outline quality validation...")
        quality_result = validate_outline_quality(outline_data, final_sessions)
        
        # Log quality results
        quality_score = quality_result['quality_score']
        logger.info(f"Outline quality score: {quality_score['overall_score']:.1f}/100 ({quality_score['quality_level']})")
        
        if quality_result['issues']:
            logger.warning(f"Found {len(quality_result['issues'])} quality issues:")
            for issue in quality_result['issues'][:5]:  # Log top 5 issues
                logger.warning(f"  - {issue.get('message', issue.get('type', 'Unknown issue'))}")
        
        if quality_result['recommendations']:
            logger.info("Quality recommendations:")
            for rec in quality_result['recommendations']:
                logger.info(f"  [{rec['priority'].upper()}] {rec['message']}")
        
        # Store quality results in outline data
        if 'course_metadata' not in outline_data:
            outline_data['course_metadata'] = {}
        outline_data['course_metadata']['quality_score'] = quality_score['overall_score']
        outline_data['course_metadata']['quality_level'] = quality_score['quality_level']
        outline_data['course_metadata']['quality_validation'] = {
            'overlap_count': quality_result['overlap_count'],
            'progression_issue_count': quality_result['progression_issue_count'],
            'balance_issue_count': quality_result['balance_issue_count']
        }
        
        # Store JSON for later saving
        self._last_json_outline = outline_data
        self._last_quality_result = quality_result
        
        # Calculate statistics
        stats = self._calculate_statistics(outline_data)
        
        # Validation summary
        log_section_header(logger, "GENERATION & VALIDATION SUMMARY", major=True)
        logger.info("")
        logger.info("Generated Output:")
        logger.info(f"  • Modules: {stats['total_modules']}/{expected_module_count}")
        logger.info(f"  • Sessions: {stats['total_sessions']}/{final_sessions} (range: {stats['session_numbers_range']})")
        logger.info(f"  • Avg Sessions/Module: {stats['avg_sessions_per_module']:.2f}")
        logger.info(f"  • Learning Objectives: {stats['total_objectives']} total ({stats['avg_objectives_per_session']:.2f}/session)")
        logger.info(f"  • Key Concepts: {stats['total_concepts']} total ({stats['avg_concepts_per_session']:.2f}/session)")
        logger.info("")
        
        # Validation status
        validation_passed = True
        if stats['total_modules'] < expected_module_count:
            logger.warning(f"  ⚠️  Only {stats['total_modules']}/{expected_module_count} modules generated - may require regeneration")
            validation_passed = False
        elif stats['total_modules'] > expected_module_count:
            logger.warning(f"  ⚠️  {stats['total_modules']} modules generated (expected {expected_module_count})")
            validation_passed = False
        else:
            logger.info(f"  ✓ Module count: {expected_module_count}")
        
        if stats['total_sessions'] != final_sessions:
            logger.warning(f"  ⚠️  Session count: {stats['total_sessions']} (expected {final_sessions})")
            validation_passed = False
        else:
            logger.info(f"  ✓ Session count: {final_sessions}")
        
        logger.info("")
        if validation_passed:
            logger.info("  ✅ Validation Passed")
        else:
            logger.warning("  ⚠️  Validation Warning (see above)")
        
        # Log quality validation summary
        if hasattr(self, '_last_quality_result'):
            quality_result = self._last_quality_result
            quality_score = quality_result['quality_score']
            logger.info("")
            logger.info("  📊 Quality Validation:")
            logger.info(f"     • Overall Score: {quality_score['overall_score']:.1f}/100 ({quality_score['quality_level']})")
            logger.info(f"     • Topic Overlaps: {quality_result['overlap_count']}")
            logger.info(f"     • Progression Issues: {quality_result['progression_issue_count']}")
            logger.info(f"     • Balance Issues: {quality_result['balance_issue_count']}")
            
            if quality_score['overall_score'] < 75:
                logger.warning(f"     ⚠️  Quality score below 75 - consider reviewing outline")
        
        logger.info("═" * 80)
        
        # Store metadata for later saving
        self._last_generation_metadata = {
            'generation_params': {
                'num_modules': expected_module_count,
                'total_sessions': final_sessions,
                'min_subtopics': min_subtopics,
                'max_subtopics': max_subtopics,
                'min_objectives': min_objectives,
                'max_objectives': max_objectives,
                'min_concepts': min_concepts,
                'max_concepts': max_concepts,
                'course_name': course_info['name'],
                'course_level': course_info.get('level', 'Not specified'),
                'course_description': course_info.get('description', ''),
                'additional_constraints': course_info.get('additional_constraints', ''),
            },
            'generation_time': generation_time,
            'validation_results': {
                'modules_generated': stats['total_modules'],
                'modules_expected': expected_module_count,
                'sessions_generated': stats['total_sessions'],
                'sessions_expected': final_sessions,
                'validation_passed': validation_passed,
            }
        }
        
        # Convert JSON to markdown
        logger.info("Converting JSON to markdown format...")
        markdown_outline = self._format_json_as_markdown(outline_data)
        
        # Add course description at top
        course_desc_header = f"""## Course Description

{course_info.get('description', 'No description provided')}
"""
        
        # Add constraints if provided
        if course_info.get('additional_constraints', '').strip():
            course_desc_header += f"""
## Additional Constraints

{course_info['additional_constraints']}
"""
        
        course_desc_header += "\n"
        
        # Insert after the first section (metadata header)
        lines = markdown_outline.split('\n')
        insert_pos = None
        for i, line in enumerate(lines):
            if line.startswith('---'):
                insert_pos = i + 1
                break
        
        if insert_pos:
            lines.insert(insert_pos, course_desc_header)
            markdown_outline = '\n'.join(lines)
        
        # Calculate word count
        word_count = len(markdown_outline.split())
        
        # Log completion summary
        log_section_header(logger, "OUTLINE GENERATION COMPLETE", major=True)
        logger.info(f"  • Modules: {stats['total_modules']}/{expected_module_count}")
        logger.info(f"  • Sessions: {stats['total_sessions']}")
        logger.info(f"  • Size: {word_count:,} words, {len(markdown_outline.splitlines())} lines")
        logger.info("═" * 80)
        
        return markdown_outline
        
    def _save_generation_metadata(
        self,
        output_dir: Path,
        filename_base: str,
        generation_params: Dict[str, Any],
        generation_time: float,
        validation_results: Dict[str, Any]
    ) -> Path:
        """Save generation metadata to JSON file.
        
        Args:
            output_dir: Output directory
            filename_base: Base filename (without extension)
            generation_params: Parameters used for generation
            generation_time: Time taken to generate (seconds)
            validation_results: Validation results
            
        Returns:
            Path to saved metadata file
        """
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "generation_time_seconds": round(generation_time, 2),
            "model": self.llm_client.model,
            "api_url": self.llm_client.api_url,
            "generation_parameters": generation_params,
            "validation_results": validation_results,
            "outline_filename": f"{filename_base}.md",
            "json_filename": f"{filename_base}.json"
        }
        
        metadata_path = output_dir / f"{filename_base}_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        
        return metadata_path
    
    def save_outline(
        self,
        outline: str,
        output_dir: Path,
        filename: str = None,
        json_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Save outline to file (both markdown and JSON).
        
        Args:
            outline: Outline content (markdown)
            output_dir: Output directory
            filename: Optional custom filename
            json_data: Optional JSON data to save alongside markdown
            metadata: Optional metadata dictionary to save
            
        Returns:
            Path to saved markdown file
        """
        # Ensure output directory exists
        output_dir = Path(output_dir)
        ensure_directory(output_dir)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = format_timestamp()
            filename = f"course_outline_{timestamp}.md"
            
        filepath = output_dir / filename
        filename_base = filepath.stem
        
        # Write markdown file
        filepath.write_text(outline, encoding='utf-8')
        abs_filepath = filepath.resolve()
        logger.info(f"Saved outline (markdown) to: {abs_filepath}")
        
        # Also save JSON if provided
        saved_files = [abs_filepath]
        if json_data:
            json_filepath = filepath.with_suffix('.json')
            json_filepath.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
            abs_json_filepath = json_filepath.resolve()
            logger.info(f"Saved outline (JSON) to: {abs_json_filepath}")
            saved_files.append(abs_json_filepath)
        
        # Save metadata if provided
        if metadata:
            metadata_filepath = self._save_generation_metadata(
                output_dir,
                filename_base,
                metadata.get('generation_params', {}),
                metadata.get('generation_time', 0),
                metadata.get('validation_results', {})
            )
            logger.info(f"Saved metadata to: {metadata_filepath.resolve()}")
            saved_files.append(metadata_filepath.resolve())
        
        # Calculate statistics for saved outline
        word_count = len(outline.split())
        modules_count = json_data.get('course_metadata', {}).get('total_modules', 'N/A') if json_data else 'N/A'
        sessions_count = json_data.get('course_metadata', {}).get('total_sessions', 'N/A') if json_data else 'N/A'
        
        # Log summary box with all saved files and statistics
        log_section_header(logger, "✅ FILES SAVED", major=True)
        for saved_file in saved_files:
            logger.info(f"  📄 {saved_file}")
        logger.info("")
        logger.info("📊 OUTLINE STATISTICS:")
        logger.info(f"  • Modules: {modules_count}")
        logger.info(f"  • Sessions: {sessions_count}")
        logger.info(f"  • Words: {word_count:,}")
        logger.info("═" * 80)
        
        return filepath
        
    def validate_outline(self, outline: str) -> bool:
        """Validate that outline has content.
        
        Args:
            outline: Outline text to validate
            
        Returns:
            True if outline is valid, False otherwise
        """
        if not outline or not outline.strip():
            logger.warning("Outline is empty")
            return False
            
        if len(outline.strip()) < 50:
            logger.warning("Outline is too short")
            return False
            
        logger.debug("Outline validated successfully")
        return True
        
    def generate_and_save(self, output_dir: Path = None) -> Path:
        """Generate outline and save to file.
        
        Args:
            output_dir: Optional output directory (uses config default if None)
            
        Returns:
            Path to saved outline file
        """
        # Determine output directory first
        if output_dir is None:
            output_paths = self.config_loader.get_output_paths()
            base_dir = output_paths.get('base_directory', 'output')
            outlines_dir = output_paths.get('directories', {}).get('outlines', 'outlines')
            output_dir = Path(base_dir) / outlines_dir
        
        # Log output directory at the start
        abs_output_dir = Path(output_dir).resolve()
        logger.info("=" * 80)
        logger.info("📁 OUTPUT DIRECTORY")
        logger.info("=" * 80)
        logger.info(f"Files will be saved to: {abs_output_dir}")
        logger.info("=" * 80)
        
        # Generate outline (returns markdown, but we need to regenerate to get JSON)
        # This is not ideal - let's store the JSON during generation
        outline = self.generate_outline()
        
        # Validate
        if not self.validate_outline(outline):
            raise ValueError("Generated outline is invalid")
            
        # Save and return path (JSON and metadata will be saved if available)
        json_data = getattr(self, '_last_json_outline', None)
        metadata = getattr(self, '_last_generation_metadata', None)
        return self.save_outline(outline, output_dir, json_data=json_data, metadata=metadata)

