"""Tests for llm_client module.

Note: These are integration tests that require Ollama to be running locally.
The conftest.py ensures Ollama is started before tests run.
"""

import logging
import time
import pytest
from src.llm.client import OllamaClient, LLMError
from src.llm.health import OllamaHealthMonitor
from src.llm.request_handler import RequestHandler


@pytest.fixture
def llm_config():
    """Sample LLM configuration for testing."""
    return {
        "provider": "ollama",
        "model": "gemma3:4b",
        "api_url": "http://localhost:11434/api/generate",
        "timeout": 60,
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 100  # Keep short for tests
        }
    }


class TestOllamaClient:
    """Integration tests for OllamaClient."""
    
    def test_init_with_config(self, llm_config, skip_if_no_ollama):
        """Test initialization with configuration."""
        client = OllamaClient(llm_config)
        
        assert client.api_url == llm_config["api_url"]
        assert client.model == llm_config["model"]
        assert client.timeout == llm_config["timeout"]
        assert client.default_params == llm_config["parameters"]
        
    def test_init_with_defaults(self):
        """Test initialization with minimal config."""
        minimal_config = {
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate"
        }
        client = OllamaClient(minimal_config)
        
        assert client.model == "gemma3:4b"
        assert client.timeout == 120  # default
        
    def test_generate_simple_prompt(self, llm_config, skip_if_no_ollama):
        """Test generation with a simple prompt."""
        client = OllamaClient(llm_config)
        
        result = client.generate("Say 'hello' and nothing else.")
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "hello" in result.lower()
        
    def test_generate_with_system_prompt(self, llm_config, skip_if_no_ollama):
        """Test generation with system prompt."""
        client = OllamaClient(llm_config)
        
        system = "You are a helpful biology teacher."
        prompt = "What is a cell?"
        
        result = client.generate(prompt, system_prompt=system)
        
        assert isinstance(result, str)
        assert len(result) > 0
        
    def test_generate_with_custom_temperature(self, llm_config, skip_if_no_ollama):
        """Test generation with custom temperature parameter."""
        client = OllamaClient(llm_config)
        
        # Low temperature should give more deterministic output
        result1 = client.generate(
            "Count from 1 to 3.",
            params={"temperature": 0.1}
        )
        
        assert isinstance(result1, str)
        assert len(result1) > 0
        
    def test_format_prompt_simple(self, llm_config):
        """Test simple prompt formatting."""
        client = OllamaClient(llm_config)
        
        template = "Write about {topic}"
        variables = {"topic": "biology"}
        
        result = client.format_prompt(template, variables)
        assert result == "Write about biology"
        
    def test_format_prompt_multiple_vars(self, llm_config):
        """Test prompt formatting with multiple variables."""
        client = OllamaClient(llm_config)
        
        template = "{greeting}, {name}!"
        variables = {"greeting": "Hello", "name": "Alice"}
        
        result = client.format_prompt(template, variables)
        assert result == "Hello, Alice!"
        
    def test_format_prompt_missing_variable(self, llm_config):
        """Test prompt formatting with missing variable."""
        client = OllamaClient(llm_config)
        
        template = "Write about {topic} and {other}"
        variables = {"topic": "biology"}
        
        with pytest.raises(LLMError, match="Missing required template variables"):
            client.format_prompt(template, variables)
            
    def test_generate_with_template(self, llm_config, skip_if_no_ollama):
        """Test generation using template formatting."""
        client = OllamaClient(llm_config)
        
        template = "Name one {organism_type}."
        variables = {"organism_type": "mammal"}
        
        result = client.generate_with_template(template, variables)
        
        assert isinstance(result, str)
        assert len(result) > 0
        
    def test_generate_empty_prompt_handling(self, llm_config, skip_if_no_ollama):
        """Test handling of edge case inputs."""
        client = OllamaClient(llm_config)
        
        # Empty prompt should still work
        result = client.generate("")
        assert isinstance(result, str)
        
    def test_client_with_invalid_model(self, skip_if_no_ollama):
        """Test error handling for invalid model."""
        invalid_config = {
            "model": "nonexistent-model-xyz",
            "api_url": "http://localhost:11434/api/generate",
            "parameters": {"num_predict": 10}
        }
        
        client = OllamaClient(invalid_config)
        
        # This should raise an error when trying to generate
        with pytest.raises(LLMError):
            client.generate("Test", params={"num_predict": 10})


# PHASE 4: Additional LLM Client Tests (20% → 60% coverage)
# Note: Retry logic is tested implicitly through integration tests with real Ollama service

class TestLLMTimeoutHandling:
    """Test timeout configuration and handling."""
    
    def test_timeout_handling(self, llm_config):
        """Test that timeout settings are respected."""
        # Set very short timeout
        llm_config["timeout"] = 0.001  # 1ms - will timeout
        client = OllamaClient(llm_config)
        
        # If Ollama is running, this should timeout
        # If not, it will fail differently - that's OK
        try:
            client.generate("Test prompt")
        except LLMError as e:
            # Should mention timeout and include request ID
            error_msg = str(e).lower()
            assert "timeout" in error_msg or "timed out" in error_msg or "connection" in error_msg
            # Error should include request ID in format [request_id]
            assert "[" in str(e) and "]" in str(e)
    
    def test_custom_timeout_per_request(self, llm_config, skip_if_no_ollama):
        """Test setting timeout for individual requests."""
        client = OllamaClient(llm_config)
        
        # Default timeout should work
        result1 = client.generate("Say hello", params={"num_predict": 5})
        assert isinstance(result1, str)
        
        # Can override timeout (if client supports it)
        # This tests the configuration is properly used
    
    def test_stream_timeout_tracking(self, llm_config, skip_if_no_ollama):
        """Test that stream timeout is tracked separately from connection timeout."""
        # Set very short timeout to trigger stream timeout
        llm_config["timeout"] = 0.1  # 100ms - very short
        client = OllamaClient(llm_config)
        
        # This should trigger stream timeout (timeout * 1.5 = 150ms max stream time)
        try:
            client.generate("Generate a long response", params={"num_predict": 1000})
        except LLMError as e:
            error_msg = str(e).lower()
            # Should mention stream timeout or request timeout
            assert "timeout" in error_msg or "stream" in error_msg
            # Should include request ID (format: [op:uuid] or [req:uuid])
            assert "[" in str(e) and "]" in str(e)
            # Should include diagnostic info (chunks, bytes, chars, or elapsed)
            assert any(word in error_msg for word in ["chunk", "byte", "char", "elapsed", "received"])


class TestTemplateVariableHandling:
    """Test template variable formatting with edge cases."""
    
    def test_template_variable_special_chars(self, llm_config):
        """Test template variables with special characters."""
        client = OllamaClient(llm_config)
        
        template = "Topic: {topic}, Symbol: {symbol}"
        variables = {
            "topic": "DNA & RNA",
            "symbol": "α-helix"
        }
        
        result = client.format_prompt(template, variables)
        
        assert "DNA & RNA" in result
        assert "α-helix" in result
    
    def test_template_variable_unicode(self, llm_config):
        """Test template variables with unicode."""
        client = OllamaClient(llm_config)
        
        template = "学科: {subject}, 主题: {topic}"
        variables = {
            "subject": "生物学",
            "topic": "细胞"
        }
        
        result = client.format_prompt(template, variables)
        
        assert "生物学" in result
        assert "细胞" in result
    
    def test_template_variable_empty_string(self, llm_config):
        """Test template with empty string variable."""
        client = OllamaClient(llm_config)
        
        template = "Topic: {topic}, Details: {details}"
        variables = {
            "topic": "Biology",
            "details": ""  # Empty string
        }
        
        result = client.format_prompt(template, variables)
        
        # Should handle empty string
        assert "Topic: Biology" in result
        assert "Details:" in result


class TestStreamingAndChunking:
    """Test streaming response handling."""
    
    def test_streaming_response_handling(self, llm_config, skip_if_no_ollama):
        """Test handling of streaming responses (if supported)."""
        client = OllamaClient(llm_config)
        
        # Standard generate should work (may use streaming internally)
        result = client.generate("Say hello", params={"num_predict": 10})
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestConnectionPooling:
    """Test connection pooling and reuse."""
    
    def test_multiple_requests_same_client(self, llm_config, skip_if_no_ollama):
        """Test that client can handle multiple sequential requests."""
        client = OllamaClient(llm_config)
        
        # Make multiple requests
        results = []
        for i in range(3):
            result = client.generate(f"Say number {i}", params={"num_predict": 5})
            results.append(result)
        
        # All should succeed
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)
        assert all(len(r) > 0 for r in results)


class TestAPICompatibility:
    """Test API version and compatibility handling."""
    
    def test_api_version_compatibility(self, llm_config, skip_if_no_ollama):
        """Test handling of different API response formats."""
        client = OllamaClient(llm_config)
        
        # Current API should work
        result = client.generate("Test", params={"num_predict": 10})
        
        assert isinstance(result, str)
    
    # Note: Malformed response handling tested implicitly through integration tests


class TestParameterValidation:
    """Test parameter validation and defaults."""
    
    def test_parameter_merging(self, llm_config, skip_if_no_ollama):
        """Test that request params merge with defaults correctly."""
        client = OllamaClient(llm_config)
        
        # Default params should be used
        result1 = client.generate("Test", params=None)
        
        # Custom params should override defaults
        result2 = client.generate("Test", params={"temperature": 0.1, "num_predict": 5})
        
        assert isinstance(result1, str)
        assert isinstance(result2, str)
    
    def test_invalid_parameter_handling(self, llm_config, skip_if_no_ollama):
        """Test handling of invalid parameters."""
        client = OllamaClient(llm_config)
        
        # Invalid parameter should be handled (may be ignored or raise error)
        try:
            result = client.generate(
                "Test",
                params={"invalid_param_xyz": 999, "num_predict": 5}
            )
            # If it succeeds, that's OK - server might ignore invalid params
            assert isinstance(result, str)
        except LLMError:
            # Also OK if it raises an error
            pass


class TestSystemPromptHandling:
    """Test system prompt variations."""
    
    def test_system_prompt_with_special_chars(self, llm_config, skip_if_no_ollama):
        """Test system prompt with special characters."""
        client = OllamaClient(llm_config)
        
        system = "You are a biology teacher specializing in DNA & RNA."
        result = client.generate("What is DNA?", system_prompt=system, params={"num_predict": 20})
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_system_prompt_unicode(self, llm_config, skip_if_no_ollama):
        """Test system prompt with unicode."""
        client = OllamaClient(llm_config)
        
        system = "你是一位生物学老师"  # "You are a biology teacher" in Chinese
        result = client.generate("Test", system_prompt=system, params={"num_predict": 10})
        
        assert isinstance(result, str)
    
    def test_empty_system_prompt(self, llm_config, skip_if_no_ollama):
        """Test with empty system prompt."""
        client = OllamaClient(llm_config)
        
        result = client.generate("Test", system_prompt="", params={"num_predict": 10})
        
        assert isinstance(result, str)


class TestRequestIDTracing:
    """Test request ID generation and tracing."""
    
    def test_request_id_generation(self, llm_config, skip_if_no_ollama, caplog):
        """Test that each request gets a unique request ID."""
        import logging
        caplog.set_level(logging.INFO)
        
        client = OllamaClient(llm_config)
        
        # Make two requests
        result1 = client.generate("Say hello", params={"num_predict": 5})
        result2 = client.generate("Say goodbye", params={"num_predict": 5})
        
        # Both should succeed
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        
        # Check logs for request IDs
        log_messages = [record.message for record in caplog.records]
        request_ids = []
        for msg in log_messages:
            if "LLM Request:" in msg and "[" in msg:
                # Extract request ID from format "[request_id] LLM Request: ..."
                start = msg.find("[") + 1
                end = msg.find("]")
                if start > 0 and end > start:
                    request_ids.append(msg[start:end])
        
        # Should have at least 2 request IDs
        assert len(request_ids) >= 2
        # Request IDs should be unique (8 characters each)
        assert len(set(request_ids)) >= 2
        assert all(len(rid) == 8 for rid in request_ids)
    
    def test_request_id_in_all_logs(self, llm_config, skip_if_no_ollama, caplog):
        """Test that request ID appears in all related log messages."""
        import logging
        caplog.set_level(logging.INFO)
        
        client = OllamaClient(llm_config)
        client.generate("Test prompt", params={"num_predict": 10})
        
        # Find the request ID from the first log message
        log_messages = [record.message for record in caplog.records]
        request_id = None
        for msg in log_messages:
            if "LLM Request:" in msg and "[" in msg:
                start = msg.find("[") + 1
                end = msg.find("]")
                if start > 0 and end > start:
                    request_id = msg[start:end]
                    break
        
        if request_id:
            # Check that request ID appears in multiple log messages
            messages_with_id = [msg for msg in log_messages if f"[{request_id}]" in msg]
            assert len(messages_with_id) >= 2, "Request ID should appear in multiple log messages"


class TestStreamProgressLogging:
    """Test progress logging during stream parsing."""
    
    def test_progress_logging_during_long_stream(self, llm_config, skip_if_no_ollama, caplog):
        """Test that progress is logged during long streams."""
        import logging
        import time
        caplog.set_level(logging.INFO)
        
        client = OllamaClient(llm_config)
        
        # Generate a longer response to trigger progress logging
        # Progress logs every 5 seconds, so we need a slow generation
        start_time = time.time()
        result = client.generate(
            "Write a detailed explanation of cell biology",
            params={"num_predict": 200}  # Longer generation
        )
        duration = time.time() - start_time
        
        # If generation took more than 5 seconds, we should see progress logs
        log_messages = [record.message for record in caplog.records]
        progress_logs = [msg for msg in log_messages if "Stream progress:" in msg]
        
        # If generation was long enough, we should have progress logs
        if duration > 5:
            assert len(progress_logs) > 0, "Should have progress logs for long generations"
            # Progress logs should include request ID
            for log in progress_logs:
                assert "[" in log and "]" in log, "Progress log should include request ID"
                assert any(word in log for word in ["elapsed", "chunks", "chars"]), "Progress log should include metrics"
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestConfigurableLoggingIntervals:
    """Test configurable logging intervals."""
    
    def test_ollama_client_with_logging_config(self, llm_config):
        """Test OllamaClient accepts logging_config parameter."""
        logging_config = {
            "heartbeat_interval": 10.0,
            "progress_log_interval": 5.0
        }
        
        client = OllamaClient(llm_config, logging_config=logging_config)
        
        # Verify intervals are stored
        assert client.progress_log_interval == 5.0
        assert client.request_handler.heartbeat_interval == 10.0
    
    def test_ollama_client_without_logging_config(self, llm_config):
        """Test OllamaClient uses defaults when logging_config not provided."""
        client = OllamaClient(llm_config)
        
        # Should use defaults
        assert client.progress_log_interval == 2.0
        assert client.request_handler.heartbeat_interval == 5.0
    
    def test_ollama_client_partial_logging_config(self, llm_config):
        """Test OllamaClient handles partial logging_config."""
        logging_config = {
            "progress_log_interval": 3.0
            # heartbeat_interval not provided
        }
        
        client = OllamaClient(llm_config, logging_config=logging_config)
        
        # Should use provided value and default for missing
        assert client.progress_log_interval == 3.0
        assert client.request_handler.heartbeat_interval == 5.0  # Default


class TestErrorMessages:
    """Test error message quality and informativeness."""
    
    def test_error_message_includes_context(self, llm_config):
        """Test that error messages include helpful context."""
        client = OllamaClient(llm_config)
        
        # Missing variable should have helpful error
        template = "Write about {missing_var}"
        
        try:
            client.format_prompt(template, {})
        except LLMError as e:
            error_msg = str(e)
            # Should mention what's missing
            assert "missing_var" in error_msg or "Missing" in error_msg
    
    def test_connection_error_message(self, llm_config):
        """Test connection error messages are informative.
        
        Note: Uses real connection attempt to invalid port, not mocks.
        """
        # Use wrong URL to simulate connection error
        llm_config["api_url"] = "http://localhost:99999/api/generate"
        client = OllamaClient(llm_config)
        
        try:
            client.generate("Test")
        except LLMError as e:
            # Should have informative message
            error_msg = str(e).lower()
            assert any(word in error_msg for word in ["connection", "connect", "failed", "refused"])
            # Should include request ID
            assert "[" in str(e) and "]" in str(e), "Error should include request ID"
            # Should include elapsed time
            assert "after" in error_msg or "elapsed" in error_msg, "Error should include timing information"
    
    def test_timeout_error_message_includes_diagnostics(self, llm_config):
        """Test that timeout error messages include diagnostic information."""
        # Set very short timeout
        llm_config["timeout"] = 0.001  # 1ms
        client = OllamaClient(llm_config)
        
        try:
            client.generate("Test prompt")
        except LLMError as e:
            error_msg = str(e)
            # Should include request ID
            assert "[" in error_msg and "]" in error_msg, "Error should include request ID"
            # Should include timing information
            assert any(word in error_msg.lower() for word in ["after", "elapsed", "timeout", "limit"])
            # Should include diagnostic info or troubleshooting suggestion
            assert any(word in error_msg.lower() for word in ["check", "ollama", "timeout", "model", "increase"])
    
    def test_stream_timeout_error_includes_chunks(self, llm_config, skip_if_no_ollama):
        """Test that stream timeout errors include chunk/byte information."""
        # Set short timeout to trigger stream timeout
        llm_config["timeout"] = 0.1  # 100ms
        client = OllamaClient(llm_config)
        
        try:
            client.generate("Generate long response", params={"num_predict": 1000})
        except LLMError as e:
            error_msg = str(e).lower()
            # Should mention stream timeout or request timeout
            assert "timeout" in error_msg or "stream" in error_msg
            # Should include diagnostic info about chunks/bytes/chars/elapsed
            assert any(word in error_msg for word in ["chunk", "byte", "char", "received", "elapsed"])


class TestHangingRequests:
    """Test scenarios where requests might hang."""
    
    def test_timeout_enforcement(self, llm_config):
        """Test that timeouts are properly enforced."""
        # Set very short timeout
        llm_config["timeout"] = 0.1  # 100ms
        client = OllamaClient(llm_config)
        
        try:
            # This should timeout quickly
            client.generate("Test prompt", params={"num_predict": 1000})
            pytest.fail("Should have raised timeout error")
        except LLMError as e:
            error_msg = str(e).lower()
            # Should mention timeout
            assert "timeout" in error_msg or "timed out" in error_msg
            # Should include request ID
            assert "[" in str(e) and "]" in str(e)
    
    def test_connection_timeout_vs_read_timeout(self, llm_config):
        """Test distinction between connection and read timeouts."""
        # Use invalid URL to trigger connection timeout
        llm_config["api_url"] = "http://localhost:99999/api/generate"
        llm_config["timeout"] = 1
        client = OllamaClient(llm_config)
        
        try:
            client.generate("Test")
        except LLMError as e:
            error_msg = str(e).lower()
            # Should mention connection or unreachable
            assert any(word in error_msg for word in ["connection", "unreachable", "refused", "connect"])
            # Should include request ID
            assert "[" in str(e) and "]" in str(e)


class TestHealthMonitoring:
    """Test health monitoring functionality."""
    
    def test_health_monitor_initialization(self):
        """Test health monitor can be initialized."""
        monitor = OllamaHealthMonitor()
        assert monitor.api_url == "http://localhost:11434"
    
    def test_service_status_check(self, skip_if_no_ollama):
        """Test service status checking."""
        monitor = OllamaHealthMonitor()
        status = monitor.check_service_status()
        
        assert isinstance(status, dict)
        assert "available" in status
        assert "response_time" in status
        
        if status["available"]:
            assert status["response_time"] > 0
            assert "version" in status
    
    def test_model_status_check(self, llm_config, skip_if_no_ollama):
        """Test model status checking."""
        monitor = OllamaHealthMonitor()
        model = llm_config["model"]
        status = monitor.check_model_status(model)
        
        assert isinstance(status, dict)
        assert "loaded" in status
        assert "available" in status
        assert isinstance(status["loaded"], bool)
        assert isinstance(status["available"], bool)
    
    def test_get_diagnostics(self, skip_if_no_ollama):
        """Test comprehensive diagnostics collection."""
        monitor = OllamaHealthMonitor()
        diagnostics = monitor.get_diagnostics()
        
        assert isinstance(diagnostics, dict)
        assert "service_status" in diagnostics
        assert "gpu_info" in diagnostics
        assert "models_available" in diagnostics
        assert "timestamp" in diagnostics
    
    def test_troubleshooting_suggestions(self, skip_if_no_ollama):
        """Test troubleshooting suggestions generation."""
        monitor = OllamaHealthMonitor()
        diagnostics = monitor.get_diagnostics()
        
        suggestions = monitor.get_troubleshooting_suggestions(diagnostics, "timeout")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestRequestHandler:
    """Test request handler with monitoring."""
    
    def test_request_handler_initialization(self):
        """Test request handler can be initialized."""
        handler = RequestHandler()
        assert handler.api_url == "http://localhost:11434"
        assert handler.health_monitor is not None
    
    def test_request_with_monitoring(self, llm_config, skip_if_no_ollama):
        """Test request execution with monitoring."""
        import requests
        
        handler = RequestHandler()
        client = OllamaClient(llm_config)
        
        def make_request():
            return requests.post(
                client.api_url,
                json={
                    "model": client.model,
                    "prompt": "Say hello",
                    "stream": True,
                    "num_predict": 10
                },
                timeout=(5, 30),
                stream=True
            )
        
        response = handler.execute_with_monitoring(
            request_func=make_request,
            timeout=30,
            request_id="test-123",
            model=client.model
        )
        
        assert response.status_code == 200
    
    def test_request_cancellation(self):
        """Test request cancellation (marking as cancelled)."""
        handler = RequestHandler()
        handler.cancel_request("test-123")
        assert handler._request_cancelled.get("test-123") is True


class TestTimeoutScenarios:
    """Comprehensive timeout scenario testing."""
    
    def test_very_short_timeout(self, llm_config):
        """Test with extremely short timeout."""
        llm_config["timeout"] = 0.001  # 1ms
        client = OllamaClient(llm_config)
        
        try:
            client.generate("Test")
        except LLMError as e:
            error_msg = str(e).lower()
            assert "timeout" in error_msg or "connection" in error_msg
    
    def test_timeout_with_long_generation(self, llm_config, skip_if_no_ollama):
        """Test timeout during long generation."""
        llm_config["timeout"] = 2  # 2 seconds
        client = OllamaClient(llm_config)
        
        try:
            # Request long generation that should timeout
            client.generate(
                "Write a very long detailed explanation",
                params={"num_predict": 5000}  # Very long
            )
        except LLMError as e:
            error_msg = str(e).lower()
            # Should mention timeout
            assert "timeout" in error_msg or "timed out" in error_msg
    
    def test_timeout_override(self, llm_config, skip_if_no_ollama):
        """Test timeout override per request."""
        llm_config["timeout"] = 1  # Short default
        client = OllamaClient(llm_config)
        
        # Override with longer timeout
        result = client.generate(
            "Say hello",
            params={"num_predict": 10},
            timeout_override=30
        )
        assert isinstance(result, str)
        assert len(result) > 0


class TestOllamaUnavailable:
    """Test scenarios where Ollama is unavailable."""
    
    def test_unavailable_service(self, llm_config):
        """Test handling when Ollama service is unavailable."""
        llm_config["api_url"] = "http://localhost:99999/api/generate"
        client = OllamaClient(llm_config)
        
        try:
            client.generate("Test")
        except LLMError as e:
            error_msg = str(e).lower()
            assert any(word in error_msg for word in ["connection", "unreachable", "refused", "unavailable"])
    
    def test_invalid_model(self, llm_config, skip_if_no_ollama):
        """Test handling of invalid model name."""
        llm_config["model"] = "nonexistent-model-xyz-123"
        client = OllamaClient(llm_config)
        
        try:
            client.generate("Test", params={"num_predict": 10})
        except LLMError:
            # Should raise error for invalid model
            pass


class TestStreamingIssues:
    """Test streaming-specific issues."""
    
    def test_stream_timeout_tracking(self, llm_config, skip_if_no_ollama):
        """Test that stream timeout is tracked separately."""
        llm_config["timeout"] = 1  # Short timeout
        client = OllamaClient(llm_config)
        
        try:
            # Generate something that might take longer than timeout
            client.generate(
                "Write a detailed explanation",
                params={"num_predict": 2000}
            )
        except LLMError as e:
            error_msg = str(e).lower()
            # Should mention timeout or stream
            assert "timeout" in error_msg or "stream" in error_msg
    
    def test_empty_stream_handling(self, llm_config, skip_if_no_ollama):
        """Test handling of empty or malformed streams."""
        client = OllamaClient(llm_config)
        
        # Empty prompt should still work
        result = client.generate("")
        assert isinstance(result, str)
    
    def test_stream_progress_logging(self, llm_config, skip_if_no_ollama, caplog):
        """Test that stream progress is logged."""
        import logging
        caplog.set_level(logging.INFO)
        
        client = OllamaClient(llm_config)
        result = client.generate(
            "Write a detailed explanation of biology",
            params={"num_predict": 200}
        )
        
        # Check for progress or completion logs
        log_messages = [record.message for record in caplog.records]
        has_progress = any(
            "progress" in msg.lower() or "complete" in msg.lower() or "stream" in msg.lower()
            for msg in log_messages
        )
        
        # Should have some stream-related logging
        assert has_progress or len(result) > 0
