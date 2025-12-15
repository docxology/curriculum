"""Request handler with timeout monitoring and health checks.

This module provides non-blocking request handling with comprehensive
timeout monitoring, progress tracking, and health checks.
"""

import logging
import threading
import time
from typing import Any, Callable, Dict, Optional

import requests

from src.llm.health import OllamaHealthMonitor

logger = logging.getLogger(__name__)


class RequestHandler:
    """Handle HTTP requests with timeout monitoring and health checks.
    
    Provides non-blocking request execution with:
    - Thread-based timeout monitoring
    - Periodic health checks during long requests
    - Progress heartbeat logging
    - Request cancellation capability
    """
    
    def __init__(
        self,
        api_url: str = "http://localhost:11434",
        health_check_interval: int = 10,
        heartbeat_interval: float = 5.0
    ):
        """Initialize request handler.
        
        Args:
            api_url: Base Ollama API URL
            health_check_interval: Interval between health checks in seconds
            heartbeat_interval: Interval for heartbeat logging in seconds (default: 5.0)
        """
        self.api_url = api_url
        self.health_monitor = OllamaHealthMonitor(api_url)
        self.health_check_interval = health_check_interval
        self.heartbeat_interval = heartbeat_interval
        self._active_requests: Dict[str, threading.Thread] = {}
        self._request_cancelled: Dict[str, bool] = {}
    
    def execute_with_monitoring(
        self,
        request_func: Callable[[], requests.Response],
        timeout: int,
        request_id: str,
        model: str,
        connect_timeout: int = 5,
        read_timeout: Optional[int] = None
    ) -> requests.Response:
        """Execute request with timeout monitoring and health checks.
        
        Args:
            request_func: Function that returns requests.Response
            timeout: Total timeout in seconds
            request_id: Request ID for logging
            model: Model name being used
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds (defaults to timeout)
            
        Returns:
            requests.Response object
            
        Raises:
            requests.Timeout: If request times out
            requests.RequestException: For other request errors
        """
        if read_timeout is None:
            read_timeout = timeout
        
        request_start_time = time.time()
        self._request_cancelled[request_id] = False
        
        # Start health monitoring thread
        health_thread = threading.Thread(
            target=self._monitor_health,
            args=(request_id, model, request_start_time, timeout),
            daemon=True
        )
        health_thread.start()
        
        # Start heartbeat logging thread
        heartbeat_thread = threading.Thread(
            target=self._heartbeat_logging,
            args=(request_id, request_start_time, timeout),
            daemon=True
        )
        heartbeat_thread.start()
        
        try:
            # Execute request with proper timeouts
            logger.debug(
                f"[{request_id}] Executing request with timeouts: "
                f"connect={connect_timeout}s, read={read_timeout}s"
            )
            
            response = request_func()
            
            # Request completed successfully
            elapsed = time.time() - request_start_time
            logger.info(
                f"[{request_id}] ✓ Done {elapsed:.2f}s"
            )
            
            return response
            
        except requests.Timeout as e:
            elapsed = time.time() - request_start_time
            self._request_cancelled[request_id] = True
            
            # Determine timeout type
            if elapsed < connect_timeout + 1:
                timeout_type = "connection"
                timeout_limit = connect_timeout
            else:
                timeout_type = "read"
                timeout_limit = read_timeout
            
            logger.error(
                f"[{request_id}] ⏱️ {timeout_type.capitalize()} timeout {elapsed:.2f}s (limit: {timeout_limit}s)"
            )
            
            # Get diagnostics
            diagnostics = self.health_monitor.get_diagnostics()
            suggestions = self.health_monitor.get_troubleshooting_suggestions(
                diagnostics, error_type="timeout"
            )
            
            if suggestions:
                logger.info(f"[{request_id}] Troubleshooting suggestions:")
                for suggestion in suggestions:
                    logger.info(f"[{request_id}]   - {suggestion}")
            
            raise
            
        except requests.RequestException as e:
            elapsed = time.time() - request_start_time
            self._request_cancelled[request_id] = True
            logger.error(
                f"[{request_id}] ❌ Failed {elapsed:.2f}s: {e}"
            )
            raise
            
        finally:
            # Clean up
            self._request_cancelled.pop(request_id, None)
    
    def _monitor_health(
        self,
        request_id: str,
        model: str,
        start_time: float,
        timeout: int
    ) -> None:
        """Monitor health during request execution.
        
        Args:
            request_id: Request ID
            model: Model name
            start_time: Request start time
            timeout: Request timeout
        """
        while not self._request_cancelled.get(request_id, False):
            elapsed = time.time() - start_time
            
            # Stop monitoring if request completed or timed out
            if elapsed > timeout * 1.2:  # Slightly longer than timeout
                break
            
            # Wait for check interval
            time.sleep(self.health_check_interval)
            
            # Skip if request was cancelled
            if self._request_cancelled.get(request_id, False):
                break
            
            # Perform health check
            health_status = self.health_monitor.monitor_request_health(
                request_id, model, start_time, timeout, self.health_check_interval
            )
            
            if health_status:
                issue = health_status.get("issue")
                if issue == "service_unavailable":
                    logger.error(
                        f"[{request_id}] ❌ Critical: Ollama unavailable (may hang/fail)"
                    )
                elif issue == "model_not_loaded":
                    logger.warning(
                        f"[{request_id}] ⚠️ Model not loaded after {health_status['elapsed']:.1f}s (may be slow)"
                    )
    
    def _heartbeat_logging(
        self,
        request_id: str,
        start_time: float,
        timeout: int
    ) -> None:
        """Log heartbeat messages during long requests.
        
        Uses configurable heartbeat_interval (default: 5 seconds) set during
        initialization. Can be configured via config/output_config.yaml.
        
        Args:
            request_id: Request ID
            start_time: Request start time
            timeout: Request timeout
        """
        heartbeat_interval = self.heartbeat_interval
        last_heartbeat = start_time
        
        while not self._request_cancelled.get(request_id, False):
            elapsed = time.time() - start_time
            
            # Stop if request completed or timed out
            if elapsed > timeout * 1.2:
                break
            
            # Wait for heartbeat interval
            time.sleep(heartbeat_interval)
            
            # Skip if request was cancelled
            if self._request_cancelled.get(request_id, False):
                break
            
            # Log heartbeat
            current_elapsed = time.time() - start_time
            if current_elapsed - last_heartbeat >= heartbeat_interval:
                remaining = timeout - current_elapsed
                logger.debug(
                    f"[{request_id}] 🔄 Progress: {current_elapsed:.1f}s/{timeout}s ({remaining:.1f}s left)"
                )
                last_heartbeat = current_elapsed
    
    def cancel_request(self, request_id: str) -> None:
        """Cancel a request (mark as cancelled).
        
        Note: This doesn't actually cancel the HTTP request (requests library
        doesn't support cancellation), but it stops monitoring threads.
        
        Args:
            request_id: Request ID to cancel
        """
        self._request_cancelled[request_id] = True
        logger.info(f"[{request_id}] 🔄 Cancellation requested")
