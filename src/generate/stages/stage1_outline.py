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
from typing import Dict, Any, Optional

from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.utils.helpers import ensure_directory, format_timestamp
from src.utils.logging_setup import (
    log_section_header,
    log_parameters,
    log_validation_results,
)
from src.generate.stages.outline_quality import (
    validate_outline_quality
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
        
        Uses multiple strategies to find and extract valid JSON from LLM responses
        that may contain markdown, explanatory text, or other formatting.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        # Strategy 1: Try to find JSON in markdown code blocks (```json or ```)
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass  # Try next strategy
        
        # Strategy 2: Find the largest valid JSON object by matching braces
        # This handles cases where JSON is embedded in text without code fences
        brace_count = 0
        start_idx = -1
        best_match = None
        best_length = 0
        
        for i, char in enumerate(response):
            if char == '{':
                if brace_count == 0:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx >= 0:
                    # Found a complete JSON object
                    candidate = response[start_idx:i+1]
                    if len(candidate) > best_length:
                        try:
                            # Validate it's actually JSON
                            json.loads(candidate)
                            best_match = candidate
                            best_length = len(candidate)
                        except json.JSONDecodeError:
                            pass
                    start_idx = -1
        
        if best_match:
            try:
                return json.loads(best_match)
            except json.JSONDecodeError:
                pass  # Try next strategy
        
        # Strategy 3: Try to find JSON starting from "course_metadata" or "modules"
        # Look for common JSON structure indicators
        for pattern in [r'\{[\s\n]*"course_metadata"', r'\{[\s\n]*"modules"']:
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                start_idx = match.start()
                # Find matching closing brace
                brace_count = 0
                for i in range(start_idx, len(response)):
                    if response[i] == '{':
                        brace_count += 1
                    elif response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            candidate = response[start_idx:i+1]
                            try:
                                return json.loads(candidate)
                            except json.JSONDecodeError:
                                break
        
        # Strategy 4: Try the entire response (in case it's pure JSON)
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 5: Try to find JSON after common prefixes
        # Look for JSON after phrases like "Here's the outline:", "JSON:", etc.
        prefix_patterns = [
            r'(?:Here\'?s?|Here is|The outline|JSON|Output|Response)[\s:]*\n*(\{)',
            r'```(?:json|text)?[\s\n]*(\{)',
            r'\{[\s\n]*"course_metadata"',
        ]
        for pattern in prefix_patterns:
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                start_idx = match.start(1) if match.groups() else match.start()
                # Find matching closing brace
                brace_count = 0
                for i in range(start_idx, len(response)):
                    if response[i] == '{':
                        brace_count += 1
                    elif response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            candidate = response[start_idx:i+1]
                            try:
                                parsed = json.loads(candidate)
                                logger.debug("Found JSON using prefix pattern strategy")
                                return parsed
                            except json.JSONDecodeError:
                                break
        
        # Strategy 6: Extract JSON from lines that look like JSON (start with {, end with })
        # Find all lines that start with { and try to find matching }
        lines = response.split('\n')
        json_candidates = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('{'):
                # Try to find complete JSON object starting from this line
                brace_count = 0
                json_text = ""
                for j in range(i, len(lines)):
                    json_text += lines[j] + '\n'
                    for char in lines[j]:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                try:
                                    parsed = json.loads(json_text.strip())
                                    json_candidates.append((len(json_text), parsed))
                                except json.JSONDecodeError:
                                    pass
                                break
                    if brace_count == 0:
                        break
        
        # Use the largest valid JSON candidate
        if json_candidates:
            json_candidates.sort(key=lambda x: x[0], reverse=True)
            logger.debug("Found JSON using line-based strategy")
            return json_candidates[0][1]
        
        # All strategies failed - provide detailed error message
        logger.error("Failed to extract valid JSON from LLM response")
        logger.error(f"Response length: {len(response)} characters")
        logger.error(f"Response preview (first 500 chars): {response[:500]}")
        logger.error(f"Response preview (last 500 chars): {response[-500:]}")
        
        # Check if response contains any JSON-like structures
        has_braces = '{' in response and '}' in response
        has_quotes = '"' in response
        has_brackets = '[' in response and ']' in response
        
        logger.error(f"Response analysis: braces={has_braces}, quotes={has_quotes}, brackets={has_brackets}")
        
        if not has_braces:
            logger.error("Response does not contain any JSON-like structures (no braces found)")
        elif not has_quotes:
            logger.error("Response contains braces but no quotes - may not be valid JSON")
        
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
        
        # Debug: Log template before formatting
        logger.debug(f"Raw template length: {len(template)} characters")
        logger.debug(f"Raw template preview (first 200 chars): {template[:200]}...")
        logger.debug(f"Template variables needed: {self.llm_client._extract_template_variables(template)}")
        
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
        
        # Log actual prompt preview for debugging (first 500 chars)
        if len(formatted_prompt) < 100:
            logger.warning(f"⚠️  Prompt is suspiciously short ({len(formatted_prompt)} chars). Preview: {repr(formatted_prompt)}")
            logger.warning("This may indicate template formatting issues. Check template variables.")
        else:
            logger.debug(f"Prompt preview (first 200 chars): {formatted_prompt[:200]}...")
        
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
        # - format: "json" - enforce JSON output format (Ollama supports this, but may cause issues with some models)
        # These optimizations significantly improve generation speed
        outline_params = {
            "num_ctx": 32000,
            "num_predict": 4000
            # Note: format: "json" removed - some models (like gemma3:4b) may stop early with this parameter
            # We'll rely on prompt instructions instead
        }
        logger.info("Using optimized parameters for outline generation: num_ctx=32000, num_predict=4000 (reduced from default 128K/64K for faster generation, format:json removed for compatibility)")
        
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
            
            # Validate response length - outline JSON should be at least 200 characters
            min_expected_length = 200
            if len(raw_response) < min_expected_length:
                logger.error(f"Response too short: {len(raw_response)} characters (expected at least {min_expected_length})")
                logger.error(f"Response content: {repr(raw_response)}")
                logger.error("This suggests the LLM stopped early or the prompt was not formatted correctly.")
                raise ValueError(
                    f"LLM response too short ({len(raw_response)} chars, expected {min_expected_length}+). "
                    f"Response: {repr(raw_response[:100])}. Check prompt formatting and LLM model behavior."
                )
            
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
        
        # Parse JSON from response with enhanced retry logic
        logger.info("-" * 80)
        logger.info("Parsing JSON response...")
        outline_data = self._extract_json_from_response(raw_response)
        
        # Multi-strategy retry if extraction or validation fails
        max_retries = 3
        retry_attempt = 0
        
        while (outline_data is None or 
               (outline_data is not None and not self._validate_outline_json(outline_data, expected_module_count))) and \
              retry_attempt < max_retries:
            
            retry_attempt += 1
            logger.warning(f"Attempt {retry_attempt}/{max_retries}: {'JSON extraction' if outline_data is None else 'JSON validation'} failed. Retrying...")
            
            # Strategy 1: Retry with more explicit prompt (same params)
            if retry_attempt == 1:
                retry_system_prompt = "You are a JSON generator. Output ONLY valid JSON. No markdown, no code fences, no explanations. Start with { and end with }."
                retry_params = outline_params.copy()
            # Strategy 2: Retry with increased num_predict (maybe model stopped early)
            elif retry_attempt == 2:
                retry_system_prompt = system_prompt
                retry_params = outline_params.copy()
                retry_params["num_predict"] = 6000  # Increase prediction limit
                logger.info("Retry strategy 2: Increased num_predict to 6000")
            # Strategy 3: Retry with simplified prompt
            else:
                retry_system_prompt = "You are a JSON generator. Output ONLY valid JSON starting with { and ending with }."
                retry_params = outline_params.copy()
                retry_params["num_predict"] = 8000  # Further increase
                logger.info("Retry strategy 3: Simplified prompt and increased num_predict to 8000")
            
            try:
                # Add exponential backoff
                if retry_attempt > 1:
                    backoff_time = 2 ** (retry_attempt - 1)  # 2s, 4s, 8s
                    logger.info(f"Waiting {backoff_time}s before retry...")
                    time.sleep(backoff_time)
                
                retry_response = self.llm_client.generate_with_template(
                    template,
                    variables,
                    system_prompt=retry_system_prompt,
                    params=retry_params,
                    operation="outline",
                    timeout_override=operation_timeout
                )
                
                # Validate retry response length
                if len(retry_response) < 200:
                    logger.error(f"Retry {retry_attempt} also returned short response: {len(retry_response)} chars")
                    logger.error(f"Response: {repr(retry_response)}")
                    continue
                
                outline_data = self._extract_json_from_response(retry_response)
                
                if outline_data is not None:
                    # Validate structure
                    if self._validate_outline_json(outline_data, expected_module_count):
                        logger.info(f"JSON extraction and validation successful on retry attempt {retry_attempt}")
                        break
                    else:
                        logger.warning(f"Retry {retry_attempt}: JSON extracted but validation failed")
                        outline_data = None  # Continue to next retry
                else:
                    logger.warning(f"Retry {retry_attempt}: JSON extraction failed")
                    
            except Exception as retry_error:
                logger.error(f"Retry attempt {retry_attempt} failed: {retry_error}")
                outline_data = None
        
        if outline_data is None:
            logger.error("Failed to extract valid JSON from LLM response after all retries")
            logger.error(f"Raw response preview: {raw_response[:500]}...")
            raise ValueError("LLM did not return valid JSON after multiple retry attempts. Check logs for details.")
        
        if not self._validate_outline_json(outline_data, expected_module_count):
            logger.error("JSON validation failed after all retries")
            raise ValueError("Generated outline JSON failed validation. Check logs for details.")
        
        logger.info("JSON parsed and validated successfully")
        
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
                logger.warning("     ⚠️  Quality score below 75 - consider reviewing outline")
        
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

