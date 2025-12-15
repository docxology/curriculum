"""LLM client for Ollama integration.

This module provides a client to interact with the Ollama API for text generation.
"""

import json
import logging
import re
import time
import uuid
from typing import Any, Dict, Optional, Set, Tuple
import requests

from src.llm.health import OllamaHealthMonitor
from src.llm.request_handler import RequestHandler

logger = logging.getLogger(__name__)

# Operation name abbreviations for compact request IDs
OPERATION_ABBREVIATIONS = {
    "outline": "out",
    "lecture": "lec",
    "lab": "lab",
    "study_notes": "stu",
    "diagram": "dia",
    "questions": "qst",
    "application": "app",
    "extension": "ext",
    "visualization": "viz",
    "integration": "int",
    "investigation": "inv",
    "open_questions": "opq",
}


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


class OllamaClient:
    """Client for interacting with Ollama API.
    
    This class handles communication with a local Ollama instance,
    including request formatting, response parsing, and error handling.
    
    Attributes:
        api_url: URL of the Ollama API endpoint
        model: Name of the LLM model to use
        timeout: Request timeout in seconds
        default_params: Default generation parameters
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        logging_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the Ollama client.
        
        Args:
            config: LLM configuration dictionary
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            logging_config: Optional logging configuration dictionary with:
                - heartbeat_interval: Interval for heartbeat logs (seconds, default: 5.0)
                - progress_log_interval: Interval for stream progress logs (seconds, default: 2.0)
        """
        self.api_url = config.get("api_url", "http://localhost:11434/api/generate")
        self.model = config["model"]
        self.timeout = config.get("timeout", 120)
        self.default_params = config.get("parameters", {})
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Get logging intervals from config (with defaults)
        if logging_config:
            self.progress_log_interval = logging_config.get("progress_log_interval", 2.0)
            heartbeat_interval = logging_config.get("heartbeat_interval", 5.0)
        else:
            self.progress_log_interval = 2.0
            heartbeat_interval = 5.0
        
        # Initialize health monitor and request handler
        base_url = self.api_url.replace('/api/generate', '')
        self.health_monitor = OllamaHealthMonitor(base_url)
        self.request_handler = RequestHandler(base_url, heartbeat_interval=heartbeat_interval)
        
        logger.info(
            f"Initialized OllamaClient: model={self.model}, url={self.api_url}"
        )
    
    def _format_request_id(self, operation: Optional[str]) -> str:
        """Format request ID with operation abbreviation.
        
        Args:
            operation: Optional operation name (e.g., "lecture", "lab")
            
        Returns:
            Formatted request ID in format [op:uuid] or [req:uuid]
        """
        uuid_short = uuid.uuid4().hex[:6]
        if operation:
            abbrev = OPERATION_ABBREVIATIONS.get(operation, operation[:3])
            return f"{abbrev}:{uuid_short}"
        return f"req:{uuid_short}"
    
    def check_connection(self, timeout: int = 5) -> Tuple[bool, Optional[float]]:
        """Check if Ollama service is reachable and responding.
        
        Args:
            timeout: Timeout for health check in seconds (default: 5)
            
        Returns:
            Tuple of (is_connected: bool, response_time: Optional[float])
            - is_connected: True if Ollama is reachable, False otherwise
            - response_time: Response time in seconds if successful, None otherwise
        """
        try:
            # Use the version endpoint for a lightweight health check
            version_url = self.api_url.replace('/api/generate', '/api/version')
            import time
            start_time = time.time()
            response = requests.get(version_url, timeout=timeout)
            response_time = time.time() - start_time
            response.raise_for_status()
            
            # Log performance warning if response is slow
            if response_time > 1.0:
                logger.warning(
                    f"Ollama connection check successful but slow: {response_time:.2f}s "
                    f"(expected <1s). Ollama may be under heavy load or system resources constrained."
                )
            else:
                logger.debug(f"Ollama connection check successful: {version_url} (response time: {response_time:.3f}s)")
            
            return True, response_time
        except requests.RequestException as e:
            logger.warning(f"Ollama connection check failed: {e}")
            return False, None
    
    def check_gpu_usage(self) -> Dict[str, Any]:
        """Check if Ollama is currently using GPU acceleration.
        
        Returns:
            Dict with GPU usage information containing:
            - using_gpu: bool (True if any model using GPU)
            - processor_info: str (e.g., "100% GPU", "100% CPU", "48%/52% CPU/GPU")
            - models_loaded: List[str] (list of loaded model names)
            - details: List[Dict] (per-model processor info)
        """
        from src.utils.helpers import check_ollama_gpu_usage
        return check_ollama_gpu_usage()
        
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        timeout_override: Optional[int] = None
    ) -> str:
        """Generate text using the Ollama API.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to guide generation
            params: Optional parameters to override defaults
            operation: Optional operation name for logging context (e.g., "lecture", "lab")
            timeout_override: Optional timeout override in seconds (overrides instance timeout)
            
        Returns:
            Generated text
            
        Raises:
            LLMError: If generation fails
        """
        # Use timeout override if provided, otherwise use instance timeout
        effective_timeout = timeout_override if timeout_override is not None else self.timeout
        
        # Generate unique request ID with operation abbreviation
        request_id = self._format_request_id(operation)
        request_start_time = time.time()
        
        # Merge parameters
        generation_params = {**self.default_params}
        if params:
            generation_params.update(params)
            
        # Build request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,  # Use streaming for better responsiveness
            **generation_params
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        # Consolidated INFO message with key details (compact format)
        op_abbrev = OPERATION_ABBREVIATIONS.get(operation, operation[:3] if operation else "req")
        timeout_info = f" | t={effective_timeout}s" if timeout_override else ""
        logger.info(
            f"[{request_id}] 🚀 {op_abbrev} | m={self.model} | p={len(prompt)}c{timeout_info}"
        )
        
        # Detailed information at DEBUG level
        logger.debug(f"[{request_id}] System prompt: {len(system_prompt) if system_prompt else 0} chars")
        logger.debug(f"[{request_id}] Timeout: {effective_timeout}s" + (f" (overridden from {self.timeout}s)" if timeout_override else ""))
        
        # Log payload summary (truncate large prompts for readability)
        prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
        logger.debug(f"[{request_id}] Prompt preview: {prompt_preview}")
        
        if system_prompt:
            system_preview = system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt
            logger.debug(f"[{request_id}] System prompt preview: {system_preview}")
        
        # Log generation parameters
        params_summary = {k: v for k, v in generation_params.items() if k not in ['prompt', 'system']}
        logger.debug(f"[{request_id}] Generation parameters: {params_summary}")
        
        # Calculate payload size for logging
        payload_size = len(json.dumps(payload))
        
        # Attempt generation with retries
        for attempt in range(self.max_retries + 1):
            attempt_start_time = time.time()
            try:
                logger.debug(f"[{request_id}] Attempt {attempt + 1}/{self.max_retries + 1}: Sending request to {self.api_url}")
                
                # Use separate connection and read timeouts for streaming
                # Connection timeout: short (5s) to fail fast if Ollama is down
                # Read timeout: longer (effective_timeout) to wait for Ollama to start generating
                # For streaming, we need to wait for Ollama to process and start sending chunks
                connect_timeout = 5  # Fast failure if Ollama is unreachable
                read_timeout = effective_timeout  # Allow time for model to start generating
                
                # Log timeout configuration at INFO level for visibility
                logger.info(
                    f"[{request_id}] Timeout configuration: connect={connect_timeout}s, "
                    f"read={read_timeout}s (total limit: {effective_timeout}s)"
                )
                if effective_timeout > 300:
                    logger.warning(
                        f"[{request_id}] Very long timeout ({effective_timeout}s) - "
                        f"this may indicate a slow model or system. Consider using a faster model."
                    )
                
                # Pre-flight connection check before blocking request
                logger.info(f"[{request_id}] Pre-flight check: Verifying Ollama service is reachable...")
                preflight_start = time.time()
                is_connected, conn_time = self.check_connection(timeout=3)
                preflight_elapsed = time.time() - preflight_start
                if not is_connected:
                    error_msg = (
                        f"[{request_id}] Pre-flight check failed after {preflight_elapsed:.2f}s: "
                        f"Ollama service unreachable. "
                        f"Check if Ollama is running: curl {self.api_url.replace('/api/generate', '/api/version')}"
                    )
                    logger.error(error_msg)
                    raise LLMError(error_msg)
                elif conn_time > 2.0:
                    logger.warning(
                        f"[{request_id}] Pre-flight check slow: {conn_time:.2f}s "
                        f"(Ollama may be under heavy load or system resources constrained)"
                    )
                else:
                    logger.debug(f"[{request_id}] Pre-flight check passed: Ollama reachable ({conn_time:.3f}s)")
                
                # Log request context at INFO level
                logger.info(
                    f"[{request_id}] Sending request to Ollama: "
                    f"model={self.model}, operation={operation or 'unknown'}, "
                    f"payload={payload_size} bytes, prompt={len(prompt)} chars"
                )
                
                request_send_time = time.time()
                logger.info(f"[{request_id}] Waiting for HTTP response (connect timeout: {connect_timeout}s, read timeout: {read_timeout}s)...")
                
                try:
                    # Use request handler for better timeout monitoring and health checks
                    def make_request():
                        return requests.post(
                            self.api_url,
                            json=payload,
                            timeout=(connect_timeout, read_timeout),  # (connect, read) tuple
                            stream=True
                        )
                    
                    response = self.request_handler.execute_with_monitoring(
                        request_func=make_request,
                        timeout=read_timeout,
                        request_id=request_id,
                        model=self.model,
                        connect_timeout=connect_timeout,
                        read_timeout=read_timeout
                    )
                    
                    http_response_time = time.time() - request_send_time
                    logger.info(f"[{request_id}] ✅ HTTP {response.status_code} in {http_response_time:.2f}s")
                except requests.Timeout as e:
                    elapsed = time.time() - request_send_time
                    if elapsed < connect_timeout + 1:
                        # Connection timeout: Ollama unreachable
                        error_msg = (
                            f"[{request_id}] Connection timeout after {elapsed:.2f}s "
                            f"(limit: {connect_timeout}s) - Ollama service unreachable. "
                            f"Operation: {operation or 'unknown'}. "
                            f"Diagnostics: Check if Ollama is running: "
                            f"curl {self.api_url.replace('/api/generate', '/api/version')}. "
                            f"If Ollama is running, check network connectivity and firewall settings."
                        )
                    else:
                        # Read timeout: Ollama received request but didn't respond
                        error_msg = (
                            f"[{request_id}] Read timeout after {elapsed:.2f}s "
                            f"(limit: {read_timeout}s) - Ollama received request but didn't start generating. "
                            f"Operation: {operation or 'unknown'}. "
                            f"Model: {self.model}. "
                            f"This may indicate: (1) Model is too slow for this timeout, "
                            f"(2) System resources are constrained, (3) Model is hung. "
                            f"Solutions: (1) Increase timeout in config/llm_config.yaml "
                            f"(current: {effective_timeout}s), (2) Use a faster model, "
                            f"(3) Check Ollama logs: ollama logs, (4) Restart Ollama service."
                        )
                    logger.error(error_msg)
                    raise LLMError(error_msg) from e
                
                # Log response status
                logger.debug(f"[{request_id}] Response status: {response.status_code}")
                response.raise_for_status()
                
                # Log that we got a response and are starting to parse the stream
                logger.info(f"[{request_id}] 📡 Stream active ({response.status_code})")
                
                # Verify response has content-type and headers
                content_type = response.headers.get('Content-Type', 'unknown')
                logger.debug(f"[{request_id}] Response Content-Type: {content_type}")
                
                # Check if response is actually streaming (chunked transfer)
                transfer_encoding = response.headers.get('Transfer-Encoding', '')
                if 'chunked' in transfer_encoding.lower():
                    logger.debug(f"[{request_id}] Chunked transfer encoding detected - stream should start immediately")
                else:
                    logger.debug(f"[{request_id}] Transfer encoding: {transfer_encoding or 'none'} (may buffer before streaming)")
                
                # Parse streaming response with timeout tracking
                # Allow empty responses if prompt was empty
                is_empty_prompt = not prompt.strip()
                logger.debug(f"[{request_id}] Starting stream parsing (timeout: {effective_timeout}s)")
                generated_text = self._parse_streaming_response(response, request_id, effective_timeout, allow_empty=is_empty_prompt)
                
                # Calculate statistics
                request_duration = time.time() - request_start_time
                word_count_est = len(generated_text.split())
                chars_per_sec = len(generated_text) / request_duration if request_duration > 0 else 0
                
                # Single consolidated completion message at INFO level
                logger.info(
                    f"[{request_id}] ✓ Done {request_duration:.2f}s: {len(generated_text)}c "
                    f"(~{word_count_est}w @{chars_per_sec:.0f}c/s)"
                )
                return generated_text
                
            except requests.ConnectionError as e:
                attempt_duration = time.time() - attempt_start_time
                if attempt < self.max_retries:
                    logger.warning(
                        f"[{request_id}] Connection error (attempt {attempt + 1}/{self.max_retries + 1}, "
                        f"elapsed: {attempt_duration:.2f}s): {e}"
                    )
                    logger.info(f"[{request_id}] Retrying in {self.retry_delay * (2 ** attempt):.1f}s...")
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                total_duration = time.time() - request_start_time
                error_msg = (
                    f"[{request_id}] Connection error after {total_duration:.2f}s: {e}. "
                    f"Check if Ollama is running: curl {self.api_url.replace('/api/generate', '/api/version')}"
                )
                logger.error(error_msg)
                raise LLMError(error_msg)
                
            except requests.Timeout as e:
                attempt_duration = time.time() - attempt_start_time
                total_duration = time.time() - request_start_time
                
                if attempt < self.max_retries:
                    logger.warning(
                        f"[{request_id}] Timeout (attempt {attempt + 1}/{self.max_retries + 1}, "
                        f"elapsed: {attempt_duration:.2f}s, limit: {effective_timeout}s): {e}"
                    )
                    logger.info(f"[{request_id}] Retrying in {self.retry_delay * (2 ** attempt):.1f}s...")
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                # Final timeout after all retries - provide comprehensive error message
                error_msg = (
                    f"[{request_id}] Request timeout after {total_duration:.2f}s elapsed "
                    f"(limit: {effective_timeout}s) across {self.max_retries + 1} attempts. "
                    f"Received 0 chunks, 0 bytes before timeout. "
                    f"Operation: {operation or 'unknown'}. Model: {self.model}. "
                    f"Diagnostics: (1) Check Ollama service: curl {self.api_url.replace('/api/generate', '/api/version')}, "
                    f"(2) Check Ollama logs: ollama logs, (3) Consider increasing timeout in config/llm_config.yaml "
                    f"(current: {effective_timeout}s), (4) Use a faster model, (5) Check system resources (CPU/memory). "
                    f"Error: {e}"
                )
                logger.error(error_msg)
                raise LLMError(error_msg)
                
            except requests.HTTPError as e:
                total_duration = time.time() - request_start_time
                error_msg = f"[{request_id}] HTTP error after {total_duration:.2f}s: {e}"
                logger.error(error_msg)
                raise LLMError(error_msg)
                
            except LLMError:
                # Re-raise LLMError as-is (it already has request_id)
                raise
                
            except Exception as e:
                total_duration = time.time() - request_start_time
                error_msg = f"[{request_id}] Unexpected error after {total_duration:.2f}s: {e}"
                logger.error(error_msg, exc_info=True)
                raise LLMError(error_msg)
                
    def _parse_streaming_response(
        self, 
        response: requests.Response, 
        request_id: str,
        timeout: int,
        allow_empty: bool = False
    ) -> str:
        """Parse streaming JSON response from Ollama with adaptive timeout handling.
        
        This method implements adaptive timeout logic:
        - Initial stream timeout: `timeout * 1.5` (e.g., 180s → 270s)
        - Adaptive extension: If stream is making progress (chunks arriving or text growing),
          timeout extends up to `timeout * 3.5` (e.g., 180s → 630s max)
        - Stuck detection: Streams without progress for 30s are detected early and fail fast
        - Progress monitoring: Logs stream progress every 2s with chunk rate, text growth, speed
        
        Args:
            response: Streaming HTTP response from Ollama API
            request_id: Unique request ID for logging and tracing
            timeout: Base timeout in seconds (used to calculate stream timeout limits)
            allow_empty: If True, allow empty responses (e.g., for empty prompts).
                        If False, empty responses raise LLMError.
            
        Returns:
            Complete generated text from streamed response
            
        Raises:
            LLMError: If response parsing fails, times out, or stream is stuck.
                     Error messages include actionable guidance and recommendations.
        
        Example:
            >>> response = requests.post(url, json=payload, stream=True)
            >>> text = client._parse_streaming_response(response, "req-123", timeout=180)
            >>> # Returns complete generated text, or raises LLMError with guidance
        """
        generated_text = ""
        stream_start_time = time.time()
        last_progress_log = stream_start_time
        last_waiting_log = stream_start_time
        last_chunk_time = stream_start_time
        chunk_count = 0
        bytes_received = 0
        base_stream_timeout = timeout * 1.5  # Base stream timeout: 1.5x connection timeout
        max_stream_time = base_stream_timeout  # Current effective timeout (may be extended adaptively)
        max_adaptive_extension = timeout * 2.0  # Maximum total timeout (3.5x base timeout)
        progress_log_interval = self.progress_log_interval  # Use configurable interval (default: 2.0s)
        waiting_log_interval = 10.0  # Log waiting status every 10 seconds if no chunks
        stuck_detection_interval = 30.0  # Detect stuck streams after 30s without progress
        chunks_without_text = 0  # Track consecutive chunks without text extraction
        max_chunks_without_text = 100  # Fail fast if no text after 100 chunks
        first_chunk_received = False
        first_chunk_time = None
        last_text_length = 0  # Track text growth for progress detection
        last_text_check_time = stream_start_time
        adaptive_extension_applied = False  # Track if we've extended timeout
        
        logger.info(f"[{request_id}] Starting stream parsing, waiting for first chunk...")
        logger.debug(f"[{request_id}] Entering iter_lines() loop - this will block until first line arrives or timeout")
        logger.debug(f"[{request_id}] Stream timeout limit: {max_stream_time:.1f}s (base: {base_stream_timeout:.1f}s, max: {max_adaptive_extension:.1f}s)")
        
        try:
            # Use iter_lines with decode_unicode=True and chunk_size=1 to get immediate feedback
            # chunk_size=1 ensures we get data as soon as it arrives (not buffered)
            for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                current_time = time.time()
                elapsed = current_time - stream_start_time
                
                # Adaptive timeout extension: if stream is making progress, extend timeout
                if first_chunk_received and chunk_count > 0:
                    # Check if we're making progress (text is growing or chunks arriving)
                    time_since_last_chunk = current_time - last_chunk_time
                    text_growth = len(generated_text) - last_text_length
                    time_since_text_check = current_time - last_text_check_time
                    
                    # If we're receiving chunks regularly (within 15s) or text is growing, extend timeout
                    is_making_progress = (
                        time_since_last_chunk < 15.0 or  # Recent chunks
                        (time_since_text_check > 5.0 and text_growth > 0)  # Text growing
                    )
                    
                    # Extend timeout if making progress and haven't exceeded max
                    if is_making_progress and elapsed > max_stream_time * 0.8 and max_stream_time < max_adaptive_extension:
                        extension = min(timeout * 0.5, max_adaptive_extension - max_stream_time)
                        if extension > 0:
                            max_stream_time += extension
                            if not adaptive_extension_applied:
                                logger.info(
                                    f"[{request_id}] Stream making progress - extending timeout by {extension:.1f}s "
                                    f"(new limit: {max_stream_time:.1f}s, max: {max_adaptive_extension:.1f}s)"
                                )
                                adaptive_extension_applied = True
                    
                    # Update text tracking
                    if time_since_text_check > 5.0:
                        last_text_length = len(generated_text)
                        last_text_check_time = current_time
                
                # Early stuck stream detection: no progress for extended period
                if first_chunk_received and chunk_count > 0:
                    time_since_last_chunk = current_time - last_chunk_time
                    if time_since_last_chunk > stuck_detection_interval:
                        # Check if we have meaningful text
                        if len(generated_text) > 0:
                            # We have text but stream stalled - might be done, but check for 'done' flag
                            logger.warning(
                                f"[{request_id}] Stream appears stalled: no chunks for {time_since_last_chunk:.1f}s "
                                f"(received {chunk_count} chunks, {len(generated_text)} chars). "
                                f"Stream may have completed without 'done' flag or may be stuck."
                            )
                        else:
                            # No text and stalled - likely stuck
                            error_msg = (
                                f"[{request_id}] Stream stuck: no progress for {time_since_last_chunk:.1f}s "
                                f"(received {chunk_count} chunks but no text extracted). "
                                f"Stream may be stuck. Consider increasing timeout or checking model status."
                            )
                            logger.error(error_msg)
                            raise LLMError(error_msg)
                
                # Check for stream timeout
                if elapsed > max_stream_time:
                    # Extract operation from request_id (format: "op:uuid" or "req:uuid")
                    operation = None
                    if ':' in request_id:
                        abbrev = request_id.split(':')[0]
                        # Reverse lookup operation from abbreviation
                        for op_name, op_abbrev in OPERATION_ABBREVIATIONS.items():
                            if op_abbrev == abbrev:
                                operation = op_name
                                break
                        if not operation:
                            operation = abbrev  # Fallback to abbreviation if not found
                    
                    # Calculate performance metrics
                    chars_per_sec = len(generated_text) / elapsed if elapsed > 0 else 0
                    tokens_est = len(generated_text) / 4  # Rough estimate: ~4 chars per token
                    tokens_per_sec = tokens_est / elapsed if elapsed > 0 else 0
                    
                    # Build operation-specific recommendations
                    operation_context = f"Operation: {operation}" if operation else "Operation: unknown"
                    
                    # Determine recommendation based on operation type and performance
                    recommendation_parts = []
                    
                    if chunk_count == 0:
                        recommendation_parts.append("No chunks received. Check: (1) Ollama service status, (2) Model availability, (3) Network connectivity.")
                    elif len(generated_text) == 0:
                        recommendation_parts.append("Chunks received but no text extracted. Check: (1) Model output format, (2) Response parsing logic.")
                    elif chars_per_sec < 10:
                        recommendation_parts.append(f"Very slow generation ({chars_per_sec:.1f} chars/s, ~{tokens_per_sec:.1f} tok/s).")
                    else:
                        recommendation_parts.append(f"Generation was slow ({chars_per_sec:.1f} chars/s, ~{tokens_per_sec:.1f} tok/s) but making progress.")
                    
                    # Add operation-specific timeout recommendations
                    if operation:
                        operation_timeout_suggestions = {
                            'outline': "For outline generation, consider: (1) Increasing timeout to 600s+, (2) Using a faster model, (3) Reducing prompt complexity.",
                            'lecture': "For lecture generation, consider: (1) Increasing timeout to 480s+, (2) Breaking into smaller sections, (3) Using a faster model.",
                            'lab': "For lab generation, consider: (1) Increasing timeout to 360s+, (2) Simplifying procedures, (3) Using a faster model.",
                            'application': "For application generation, consider: (1) Increasing timeout to 300s+, (2) Reducing number of examples, (3) Using a faster model.",
                            'extension': "For extension generation, consider: (1) Increasing timeout to 300s+, (2) Reducing topic count, (3) Using a faster model.",
                        }
                        if operation in operation_timeout_suggestions:
                            recommendation_parts.append(operation_timeout_suggestions[operation])
                    
                    # General recommendations
                    recommendation_parts.append("General solutions: (1) Increase timeout in config/llm_config.yaml, (2) Use a faster model, (3) Check system resources (CPU/memory/GPU), (4) See docs/TROUBLESHOOTING.md for detailed guidance.")
                    
                    recommendation = " ".join(recommendation_parts)
                    
                    error_msg = (
                        f"[{request_id}] Stream timeout: {elapsed:.2f}s elapsed "
                        f"(limit: {max_stream_time:.2f}s, base timeout: {timeout:.2f}s). "
                        f"{operation_context}. "
                        f"Received {chunk_count} chunks, {bytes_received} bytes, "
                        f"{len(generated_text)} chars (~{tokens_est:.0f} tokens) before timeout. "
                        f"Performance: {chars_per_sec:.1f} chars/s, ~{tokens_per_sec:.1f} tok/s. "
                        f"{recommendation}"
                    )
                    logger.error(error_msg)
                    raise LLMError(error_msg)
                
                # Log waiting status if no chunks received - use INFO level for better visibility
                if chunk_count == 0 and elapsed >= waiting_log_interval:
                    if current_time - last_waiting_log >= waiting_log_interval:
                        logger.info(
                            f"[{request_id}] Still waiting for first chunk after {elapsed:.1f}s... "
                            f"(timeout limit: {max_stream_time:.1f}s). "
                            f"Ollama may be processing the request. Check Ollama service status if this continues."
                        )
                        last_waiting_log = current_time
                elif chunk_count > 0 and current_time - last_chunk_time >= waiting_log_interval:
                    # Log if we haven't received chunks for a while (stream may have stalled)
                    if current_time - last_waiting_log >= waiting_log_interval:
                        logger.info(
                            f"[{request_id}] No new chunks for {current_time - last_chunk_time:.1f}s "
                            f"(received {chunk_count} chunks so far, {len(generated_text)} chars, "
                            f"elapsed: {elapsed:.1f}s). Stream may have stalled - checking..."
                        )
                        last_waiting_log = current_time
                
                # Log progress periodically at INFO level (compact format)
                if current_time - last_progress_log >= progress_log_interval:
                    chars_per_sec = len(generated_text) / elapsed if elapsed > 0 else 0
                    chunks_per_sec = chunk_count / elapsed if elapsed > 0 else 0
                    tokens_est = len(generated_text) / 4  # Rough estimate: ~4 chars per token
                    tokens_per_sec = tokens_est / elapsed if elapsed > 0 else 0
                    
                    logger.info(
                        f"[{request_id}] 📊 {elapsed:.1f}s: {len(generated_text)}c @{chars_per_sec:.0f}c/s "
                        f"({chunk_count}ch, ~{tokens_est:.0f}t @{tokens_per_sec:.0f}t/s)"
                    )
                    last_progress_log = current_time
                
                if line:
                    bytes_received += len(line)
                    chunk_count += 1
                    last_chunk_time = current_time
                    text_extracted_this_chunk = False
                    
                    # Log when first chunk is received
                    if not first_chunk_received:
                        first_chunk_time = elapsed
                        logger.debug(
                            f"[{request_id}] First chunk after {first_chunk_time:.2f}s ({bytes_received}b)"
                        )
                        first_chunk_received = True
                    
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"[{request_id}] Failed to parse JSON chunk {chunk_count}: {e}. "
                            f"Line preview: {line[:100] if isinstance(line, (str, bytes)) else str(line)[:100]}"
                        )
                        chunks_without_text += 1
                        # Check for early termination if too many parsing failures
                        if chunks_without_text >= max_chunks_without_text:
                            error_msg = (
                                f"[{request_id}] Too many parsing failures: {chunks_without_text} chunks "
                                f"failed to parse. No text extracted. Stream may be malformed. "
                                f"Sample line: {str(line)[:200]}"
                            )
                            logger.error(error_msg)
                            raise LLMError(error_msg)
                        continue
                    
                    # Try multiple field names for response text
                    # Note: Some models (like qwen3-vl) use 'thinking' field, but most use 'response'
                    response_text = None
                    has_response_field = False
                    
                    # Check 'response' field first (standard for most Ollama models including ministral-3:3b)
                    if "response" in data:
                        has_response_field = True
                        if data["response"] is not None:
                            response_text = data["response"]
                    # Also check 'thinking' field for compatibility with models that use it
                    elif "thinking" in data and data["thinking"] is not None:
                        response_text = data["thinking"]
                        has_response_field = True
                        has_response_field = True
                        if data["response"] is not None:
                            response_text = data["response"]
                    elif "content" in data and data["content"] is not None:
                        response_text = data["content"]
                        has_response_field = True
                    elif "text" in data and data["text"] is not None:
                        response_text = data["text"]
                        has_response_field = True
                    elif "message" in data:
                        # Handle nested message structure
                        message = data["message"]
                        if isinstance(message, dict):
                            response_text = message.get("content") or message.get("text") or message.get("response")
                            has_response_field = True
                        elif isinstance(message, str):
                            response_text = message
                            has_response_field = True
                    
                    # Extract text if we have a non-empty string
                    if response_text is not None and isinstance(response_text, str):
                        if response_text:  # Non-empty string
                            generated_text += response_text
                            text_extracted_this_chunk = True
                            chunks_without_text = 0  # Reset counter on successful extraction
                        # Empty string is normal in streaming (keep-alive chunks)
                        # Don't count empty strings as failures - they're expected in streaming
                        # The response field exists, so the stream is working correctly
                    elif has_response_field:
                        # Response field exists but is None (not a string)
                        if chunk_count <= 5 or chunk_count % 100 == 0:
                            logger.debug(
                                f"[{request_id}] Chunk {chunk_count} has response field but value is None. "
                                f"Data keys: {list(data.keys())}"
                            )
                        if not generated_text:
                            chunks_without_text += 1
                    else:
                        # No text field found - log structure for debugging
                        if chunk_count <= 5 or chunk_count % 100 == 0:  # Log first 5 and every 100th
                            logger.debug(
                                f"[{request_id}] Chunk {chunk_count} has no text field. "
                                f"Available keys: {list(data.keys())}. "
                                f"Sample data: {str(data)[:200]}"
                            )
                        if not generated_text:
                            chunks_without_text += 1
                    
                    # Early termination check: if we've received many chunks but no text
                    # Only check if we haven't extracted any text yet
                    # Check if response field exists (even if empty) vs missing
                    # Check for any response field (response is standard, thinking is for some models)
                    has_response_field_in_chunk = (
                        "response" in data or 
                        "thinking" in data or 
                        "content" in data or 
                        "text" in data
                    )
                    
                    if not generated_text:
                        # Check if response field exists but is empty (normal in streaming) vs missing (problem)
                        if has_response_field_in_chunk:
                            # Response field exists - model might be slow or thinking
                            # Allow many more chunks before failing (empty response strings are normal)
                            # Only fail if we've received a LOT of chunks with no text
                            if chunk_count >= max_chunks_without_text * 10:  # 1000 chunks = likely stuck
                                sample_data = {}
                                if 'data' in locals():
                                    sample_data = {k: (str(v)[:100] if not isinstance(v, (str, int, float, bool, type(None))) else v) 
                                                 for k, v in list(data.items())[:5]}
                                error_msg = (
                                    f"[{request_id}] Early termination: {chunk_count} chunks received "
                                    f"but no text extracted. Bytes: {bytes_received}. "
                                    f"Response field exists but appears empty. Stream may be stuck. "
                                    f"Sample chunk keys: {list(data.keys()) if 'data' in locals() else 'N/A'}. "
                                    f"Sample data: {sample_data}"
                                )
                                logger.error(error_msg)
                                raise LLMError(error_msg)
                        else:
                            # No response field at all - this is a problem, fail faster
                            if chunks_without_text >= max_chunks_without_text:
                                sample_data = {}
                                if 'data' in locals():
                                    sample_data = {k: (str(v)[:100] if not isinstance(v, (str, int, float, bool, type(None))) else v) 
                                                 for k, v in list(data.items())[:5]}
                                error_msg = (
                                    f"[{request_id}] Early termination: {chunks_without_text} consecutive chunks "
                                    f"without response field. Total chunks: {chunk_count}, bytes: {bytes_received}. "
                                    f"Stream may be using unexpected format. "
                                    f"Sample chunk keys: {list(data.keys()) if 'data' in locals() else 'N/A'}. "
                                    f"Sample data: {sample_data}"
                                )
                                logger.error(error_msg)
                                raise LLMError(error_msg)
                        
                    if data.get("done", False):
                        stream_duration = time.time() - stream_start_time
                        chars_per_sec = len(generated_text) / stream_duration if stream_duration > 0 else 0
                        logger.debug(
                            f"[{request_id}] Stream complete: {stream_duration:.2f}s, "
                            f"{chunk_count} chunks, {bytes_received} bytes, "
                            f"{len(generated_text)} chars ({chars_per_sec:.1f} chars/s)"
                        )
                        break
                        
        except LLMError:
            # Re-raise LLMError as-is
            raise
        except json.JSONDecodeError as e:
            # Log detailed error with sample data
            error_msg = (
                f"[{request_id}] JSON decode error in stream parsing: {e}. "
                f"Processed {chunk_count} chunks, {bytes_received} bytes, "
                f"extracted {len(generated_text)} chars. "
                f"Last chunk preview: {str(line)[:500] if 'line' in locals() else 'N/A'}"
            )
            logger.error(error_msg)
            raise LLMError(error_msg)
        except Exception as e:
            error_msg = (
                f"[{request_id}] Error parsing stream: {e}. "
                f"Processed {chunk_count} chunks, {bytes_received} bytes, "
                f"extracted {len(generated_text)} chars."
            )
            logger.error(error_msg, exc_info=True)
            raise LLMError(error_msg)
        
        # Final validation: check if we got any text
        if not generated_text:
            if allow_empty:
                # Empty response is acceptable for empty prompts
                logger.debug(f"[{request_id}] Empty response received (allowed for empty prompt)")
                return ""
            error_msg = (
                f"[{request_id}] LLM returned empty response. "
                f"Processed {chunk_count} chunks, {bytes_received} bytes. "
                f"This suggests the response format may be unexpected. "
                f"Check Ollama model output format or increase logging level for details."
            )
            logger.error(error_msg)
            # If we got chunks but no text, log a sample of what we received
            if chunk_count > 0:
                logger.error(
                    f"[{request_id}] Debug: Received {chunk_count} chunks but extracted 0 characters. "
                    f"This may indicate a response format mismatch."
                )
            raise LLMError(error_msg)
        
        return generated_text
        
    def _extract_template_variables(self, template: str) -> Set[str]:
        """Extract all variable names from a template.
        
        Args:
            template: Template string with {variable} placeholders
            
        Returns:
            Set of variable names found in template
        """
        # Find all {variable_name} patterns, but exclude {{ (escaped braces)
        # Match single { followed by non-brace characters, then }
        pattern = r'(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})'
        matches = re.findall(pattern, template)
        return set(matches)
    
    def _validate_template_variables(
        self, 
        template: str, 
        variables: Dict[str, str]
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """Validate template variables against provided values.
        
        Args:
            template: Template string
            variables: Provided variables dictionary
            
        Returns:
            Tuple of (required_vars, missing_vars, extra_vars)
        """
        required_vars = self._extract_template_variables(template)
        provided_vars = set(variables.keys())
        missing_vars = required_vars - provided_vars
        extra_vars = provided_vars - required_vars
        
        return required_vars, missing_vars, extra_vars
    
    def format_prompt(
        self,
        template: str,
        variables: Dict[str, str]
    ) -> str:
        """Format a prompt template with variables.
        
        Args:
            template: Prompt template with {placeholders}
            variables: Dictionary of variable values
            
        Returns:
            Formatted prompt string
            
        Raises:
            LLMError: If required variables are missing
        """
        # Validate template variables
        required_vars, missing_vars, extra_vars = self._validate_template_variables(
            template, variables
        )
        
        # Log validation results
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Template requires {len(required_vars)} variables")
            logger.debug(f"Provided {len(variables)} variables")
            
            if missing_vars:
                logger.error(f"Missing required variables: {', '.join(sorted(missing_vars))}")
            
            if extra_vars:
                logger.warning(f"Extra variables provided (will be ignored): {', '.join(sorted(extra_vars))}")
        
        # Raise error if variables are missing
        if missing_vars:
            raise LLMError(
                f"Missing required template variables: {', '.join(sorted(missing_vars))}"
            )
        
        # Format the template
        try:
            formatted = template.format(**variables)
            
            # Log formatted prompt at debug level (truncated)
            if logger.isEnabledFor(logging.DEBUG):
                preview = formatted[:2000] + "..." if len(formatted) > 2000 else formatted
                logger.debug(f"Formatted prompt ({len(formatted)} chars):\n{preview}")
            
            return formatted
            
        except KeyError as e:
            raise LLMError(f"Error formatting template: {e}")
            
    def generate_with_template(
        self,
        template: str,
        variables: Dict[str, str],
        system_prompt: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        timeout_override: Optional[int] = None
    ) -> str:
        """Generate text using a template and variables.
        
        Args:
            template: Prompt template with {placeholders}
            variables: Dictionary of variable values
            system_prompt: Optional system prompt
            params: Optional generation parameters
            operation: Optional operation name for logging context (e.g., "lecture", "lab")
            timeout_override: Optional timeout override in seconds (overrides instance timeout)
            
        Returns:
            Generated text
        """
        # Log template information at debug level
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Template length: {len(template)} characters")
            logger.debug(f"System prompt: {system_prompt[:100]}..." if system_prompt else "No system prompt")
            logger.debug(f"Variables provided: {len(variables)}")
            if timeout_override:
                logger.debug(f"Timeout override: {timeout_override}s (base: {self.timeout}s)")
        
        # Format and validate prompt
        formatted_prompt = self.format_prompt(template, variables)
        
        # Generate with formatted prompt and operation context
        return self.generate(formatted_prompt, system_prompt, params, operation=operation, timeout_override=timeout_override)

