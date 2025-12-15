"""Health monitoring for Ollama service.

This module provides health monitoring capabilities for Ollama requests,
including model status checking, resource monitoring, and diagnostics.
"""

import logging
import subprocess
import time
from typing import Any, Dict, List, Optional

import requests

from src.utils.helpers import check_ollama_gpu_usage, run_cmd_capture

logger = logging.getLogger(__name__)


class OllamaHealthMonitor:
    """Monitor Ollama service health and model status.
    
    Provides methods to check Ollama service status, model availability,
    and collect diagnostics for troubleshooting.
    """
    
    def __init__(self, api_url: str = "http://localhost:11434"):
        """Initialize health monitor.
        
        Args:
            api_url: Base Ollama API URL (default: http://localhost:11434)
        """
        self.api_url = api_url.rstrip('/')
        self.version_url = f"{self.api_url}/api/version"
        self.models_url = f"{self.api_url}/api/tags"
        
    def check_service_status(self, timeout: int = 5) -> Dict[str, Any]:
        """Check if Ollama service is running and responsive.
        
        Args:
            timeout: Timeout for health check in seconds
            
        Returns:
            Dict with status information:
            - available: bool - True if service is reachable
            - response_time: float - Response time in seconds
            - version: Optional[str] - Ollama version if available
            - error: Optional[str] - Error message if unavailable
        """
        start_time = time.time()
        try:
            response = requests.get(self.version_url, timeout=timeout)
            response_time = time.time() - start_time
            response.raise_for_status()
            
            version_data = response.json() if response.content else {}
            version = version_data.get("version", "unknown")
            
            return {
                "available": True,
                "response_time": response_time,
                "version": version,
                "error": None
            }
        except requests.RequestException as e:
            response_time = time.time() - start_time
            return {
                "available": False,
                "response_time": response_time,
                "version": None,
                "error": str(e)
            }
    
    def check_model_status(self, model: str) -> Dict[str, Any]:
        """Check if a specific model is loaded and available.
        
        Args:
            model: Model name to check (e.g., "gemma3:4b")
            
        Returns:
            Dict with model status:
            - loaded: bool - True if model is currently loaded
            - available: bool - True if model exists (may not be loaded)
            - processor: Optional[str] - Processor info (e.g., "100% GPU")
            - size: Optional[str] - Model size if loaded
        """
        # Check if model is currently loaded
        gpu_info = check_ollama_gpu_usage()
        loaded_models = gpu_info.get("models_loaded", [])
        details = gpu_info.get("details", [])
        
        is_loaded = model in loaded_models
        processor = None
        size = None
        
        if is_loaded:
            # Find processor info for this model
            for detail in details:
                if detail.get("model") == model:
                    processor = detail.get("processor")
                    break
        
        # Check if model exists (available to load)
        is_available = self._check_model_exists(model)
        
        return {
            "loaded": is_loaded,
            "available": is_available,
            "processor": processor,
            "size": size
        }
    
    def _check_model_exists(self, model: str) -> bool:
        """Check if model exists in Ollama (may not be loaded).
        
        Args:
            model: Model name to check
            
        Returns:
            True if model exists, False otherwise
        """
        try:
            response = requests.get(self.models_url, timeout=5)
            response.raise_for_status()
            models_data = response.json()
            models = models_data.get("models", [])
            
            # Check if model name matches any available model
            for model_info in models:
                model_name = model_info.get("name", "")
                if model == model_name or model_name.startswith(f"{model}:"):
                    return True
            return False
        except Exception:
            # If we can't check, assume it might exist
            return True
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Collect comprehensive diagnostics about Ollama service.
        
        Returns:
            Dict with diagnostic information:
            - service_status: Service availability and version
            - gpu_info: GPU usage information
            - models_available: List of available models
            - system_info: System resource information (if available)
        """
        diagnostics = {
            "service_status": self.check_service_status(),
            "gpu_info": check_ollama_gpu_usage(),
            "models_available": self._get_available_models(),
            "timestamp": time.time()
        }
        
        return diagnostics
    
    def _get_available_models(self) -> List[str]:
        """Get list of available models.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(self.models_url, timeout=5)
            response.raise_for_status()
            models_data = response.json()
            models = models_data.get("models", [])
            return [model_info.get("name", "") for model_info in models]
        except Exception:
            return []
    
    def monitor_request_health(
        self,
        request_id: str,
        model: str,
        start_time: float,
        timeout: int,
        check_interval: int = 10
    ) -> Optional[Dict[str, Any]]:
        """Monitor health during a long-running request.
        
        Args:
            request_id: Request ID for logging
            model: Model being used
            start_time: Request start time
            timeout: Request timeout in seconds
            check_interval: Interval between health checks in seconds
            
        Returns:
            Dict with health status if issues detected, None otherwise
        """
        elapsed = time.time() - start_time
        
        # Only check if enough time has passed
        if elapsed < check_interval:
            return None
        
        # Check service status
        service_status = self.check_service_status(timeout=3)
        if not service_status["available"]:
            logger.warning(
                f"[{request_id}] Health check: Ollama service became unavailable "
                f"after {elapsed:.1f}s. Error: {service_status.get('error')}"
            )
            return {
                "issue": "service_unavailable",
                "elapsed": elapsed,
                "details": service_status
            }
        
        # Check model status
        model_status = self.check_model_status(model)
        if not model_status["loaded"] and elapsed > timeout * 0.5:
            # Model should be loaded by now if request is taking this long
            logger.info(
                f"[{request_id}] Health check: Model {model} not loaded "
                f"after {elapsed:.1f}s (may be loading or unresponsive)"
            )
            return {
                "issue": "model_not_loaded",
                "elapsed": elapsed,
                "details": model_status
            }
        
        # Check if service is slow
        if service_status["response_time"] > 2.0:
            logger.warning(
                f"[{request_id}] Health check: Ollama response slow "
                f"({service_status['response_time']:.2f}s) after {elapsed:.1f}s"
            )
            return {
                "issue": "slow_response",
                "elapsed": elapsed,
                "details": service_status
            }
        
        return None
    
    def get_troubleshooting_suggestions(
        self,
        diagnostics: Dict[str, Any],
        error_type: Optional[str] = None
    ) -> List[str]:
        """Get troubleshooting suggestions based on diagnostics.
        
        Args:
            diagnostics: Diagnostic information from get_diagnostics()
            error_type: Optional error type (e.g., "timeout", "connection")
            
        Returns:
            List of troubleshooting suggestions
        """
        suggestions = []
        
        service_status = diagnostics.get("service_status", {})
        if not service_status.get("available"):
            suggestions.append(
                "Ollama service is not running. Start with: ollama serve"
            )
            suggestions.append(
                f"Check service status: curl {self.version_url}"
            )
            return suggestions
        
        gpu_info = diagnostics.get("gpu_info", {})
        if not gpu_info.get("using_gpu"):
            suggestions.append(
                "Ollama is not using GPU acceleration. This may cause slow generation."
            )
            suggestions.append(
                "Check GPU availability: ollama ps"
            )
        
        if error_type == "timeout":
            suggestions.append(
                "Request timed out. Consider:"
            )
            suggestions.append(
                "  - Increasing timeout in config/llm_config.yaml"
            )
            suggestions.append(
                "  - Using a faster/smaller model"
            )
            suggestions.append(
                "  - Reducing num_predict parameter"
            )
            suggestions.append(
                "  - Checking system resources (CPU/memory)"
            )
        
        if error_type == "connection":
            suggestions.append(
                "Connection failed. Check:"
            )
            suggestions.append(
                f"  - Ollama is running: curl {self.version_url}"
            )
            suggestions.append(
                "  - Network connectivity"
            )
            suggestions.append(
                "  - Firewall settings"
            )
        
        return suggestions
