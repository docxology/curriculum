"""Pytest configuration and shared fixtures.

This module provides shared test fixtures and ensures Ollama is running
before executing integration tests.
"""

import pytest
import subprocess
import time
import requests
import logging


logger = logging.getLogger(__name__)


def is_ollama_running():
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def start_ollama_server():
    """Start Ollama server if not already running."""
    if is_ollama_running():
        logger.info("✓ Ollama server already running")
        return True
    
    logger.info("Starting Ollama server...")
    try:
        # Start Ollama in background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to be ready (max 10 seconds)
        for i in range(10):
            time.sleep(1)
            if is_ollama_running():
                logger.info(f"✓ Ollama server started (took {i+1}s)")
                return True
                
        logger.warning("Ollama server failed to start within 10 seconds")
        return False
        
    except FileNotFoundError:
        logger.error("Ollama not found. Install from https://ollama.ai/")
        return False
    except Exception as e:
        logger.error(f"Error starting Ollama: {e}")
        return False


def get_configured_model():
    """Get the configured model name from llm_config.yaml."""
    try:
        from pathlib import Path
        import yaml
        config_path = Path(__file__).parent.parent / "config" / "llm_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("llm", {}).get("model", "ministral-3:3b")
    except Exception:
        return "ministral-3:3b"  # fallback


def verify_model_available(model_name: str = None):
    """Verify the specified model is available.
    
    Args:
        model_name: Name of model to check. If None, uses configured model.
    """
    if model_name is None:
        model_name = get_configured_model()
        
    if not is_ollama_running():
        return False
        
    try:
        # Try to generate a simple response to verify model
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": "test",
                "stream": False
            },
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"{model_name} model not available: {e}")
        logger.info(f"Run: ollama pull {model_name}")
        return False


@pytest.fixture(scope="session", autouse=True)
def ensure_ollama_running():
    """Ensure Ollama is running for the test session."""
    logger.info("=" * 80)
    logger.info("VERIFYING OLLAMA SETUP")
    logger.info("=" * 80)
    
    # Try to start/verify Ollama
    if not start_ollama_server():
        logger.warning("⚠ Ollama not available - integration tests will be skipped")
        return
    
    # Verify configured model
    model_name = get_configured_model()
    if not verify_model_available(model_name):
        logger.warning(f"⚠ {model_name} model not available - integration tests will be skipped")
        logger.info(f"  To install: ollama pull {model_name}")
        return
        
    logger.info(f"✓ Ollama ready with {model_name} model")
    logger.info("=" * 80)


@pytest.fixture
def ollama_available():
    """Check if Ollama is available for this test."""
    return is_ollama_running() and verify_model_available()


@pytest.fixture
def skip_if_no_ollama():
    """Skip test if Ollama is not available."""
    if not is_ollama_running():
        pytest.skip("Ollama server not running")
    model_name = get_configured_model()
    if not verify_model_available(model_name):
        pytest.skip(f"{model_name} model not available")

