"""Integration tests for JSON outline loading functionality."""

import json
import pytest
from pathlib import Path
from src.config.loader import ConfigLoader


@pytest.fixture
def sample_outline_json(tmp_path):
    """Create a sample outline JSON file for testing."""
    outline_data = {
        "course_metadata": {
            "name": "Test Biology Course",
            "level": "Undergraduate",
            "duration_weeks": 10,
            "total_sessions": 6,
            "total_modules": 3
        },
        "modules": [
            {
                "module_id": 1,
                "module_name": "Cell Biology",
                "module_description": "Introduction to cells",
                "sessions": [
                    {
                        "session_number": 1,
                        "session_title": "Cell Structure",
                        "subtopics": ["Prokaryotes", "Eukaryotes"],
                        "learning_objectives": ["Understand cell types"],
                        "key_concepts": ["Cell membrane", "Organelles"],
                        "rationale": "Foundation for biology"
                    },
                    {
                        "session_number": 2,
                        "session_title": "Cell Functions",
                        "subtopics": ["Metabolism", "Transport"],
                        "learning_objectives": ["Explain cellular processes"],
                        "key_concepts": ["ATP", "Diffusion"],
                        "rationale": "Understanding cell function"
                    }
                ]
            },
            {
                "module_id": 2,
                "module_name": "Genetics",
                "module_description": "Introduction to genetics",
                "sessions": [
                    {
                        "session_number": 3,
                        "session_title": "DNA Structure",
                        "subtopics": ["Double helix", "Base pairs"],
                        "learning_objectives": ["Describe DNA structure"],
                        "key_concepts": ["Nucleotides", "Complementarity"],
                        "rationale": "Basis for heredity"
                    },
                    {
                        "session_number": 4,
                        "session_title": "Gene Expression",
                        "subtopics": ["Transcription", "Translation"],
                        "learning_objectives": ["Explain gene expression"],
                        "key_concepts": ["mRNA", "Protein synthesis"],
                        "rationale": "Understanding genetics"
                    }
                ]
            },
            {
                "module_id": 3,
                "module_name": "Evolution",
                "module_description": "Principles of evolution",
                "sessions": [
                    {
                        "session_number": 5,
                        "session_title": "Natural Selection",
                        "subtopics": ["Variation", "Selection"],
                        "learning_objectives": ["Apply evolutionary principles"],
                        "key_concepts": ["Fitness", "Adaptation"],
                        "rationale": "Core evolutionary concept"
                    },
                    {
                        "session_number": 6,
                        "session_title": "Speciation",
                        "subtopics": ["Isolation", "Divergence"],
                        "learning_objectives": ["Understand speciation"],
                        "key_concepts": ["Reproductive isolation", "Species"],
                        "rationale": "Understanding biodiversity"
                    }
                ]
            }
        ]
    }
    
    # Create in output/outlines/ which is where ConfigLoader searches
    outline_file = tmp_path / "output" / "outlines" / "course_outline_20241208_120000.json"
    outline_file.parent.mkdir(parents=True, exist_ok=True)
    outline_file.write_text(json.dumps(outline_data, indent=2), encoding='utf-8')
    
    return outline_file


def test_config_loader_find_latest_outline_json(sample_outline_json, tmp_path, monkeypatch):
    """Test ConfigLoader finds the latest outline JSON."""
    # Change to tmp directory so it searches there
    monkeypatch.chdir(tmp_path)
    
    # Create minimal config for loader
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "course_config.yaml").write_text("""
course:
  name: "Test"
  description: "Test"
  level: "Test"
""")
    (config_dir / "llm_config.yaml").write_text("""
llm:
  model: "test"
prompts: {}
""")
    (config_dir / "output_config.yaml").write_text("""
output:
  base_directory: "output"
  directories:
    outlines: "outlines"
""")
    
    loader = ConfigLoader(config_dir)
    
    # Should find the sample outline (created in tmp_path/outlines)
    found_path = loader._find_latest_outline_json()
    
    assert found_path is not None
    assert found_path.name == sample_outline_json.name


def test_config_loader_find_outline_explicit_path(sample_outline_json):
    """Test ConfigLoader with explicit outline path."""
    loader = ConfigLoader("config")
    
    found_path = loader._find_latest_outline_json(sample_outline_json)
    
    assert found_path is not None
    assert found_path == sample_outline_json


def test_config_loader_get_modules_from_outline(sample_outline_json):
    """Test ConfigLoader loads modules from JSON outline."""
    loader = ConfigLoader("config")
    
    modules = loader.get_modules_from_outline(sample_outline_json)
    
    assert len(modules) == 3
    assert modules[0]["module_id"] == 1
    assert modules[0]["module_name"] == "Cell Biology"
    assert len(modules[0]["sessions"]) == 2
    assert modules[1]["module_id"] == 2
    assert modules[2]["module_id"] == 3


def test_config_loader_get_module_by_id_from_outline(sample_outline_json):
    """Test ConfigLoader loads specific module by ID from outline."""
    loader = ConfigLoader("config")
    
    # Get module 2
    module = loader.get_module_by_id_from_outline(2, sample_outline_json)
    
    assert module is not None
    assert module["module_id"] == 2
    assert module["module_name"] == "Genetics"
    assert len(module["sessions"]) == 2
    
    # Test non-existent module
    module = loader.get_module_by_id_from_outline(99, sample_outline_json)
    assert module is None


def test_config_loader_get_modules_default_behavior(sample_outline_json, tmp_path, monkeypatch):
    """Test that get_modules() now loads from outline by default."""
    # Change to tmp directory
    monkeypatch.chdir(tmp_path)
    
    # Create config directory
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    
    # Create minimal course config
    course_config = config_dir / "course_config.yaml"
    course_config.write_text("""
course:
  name: "Test Course"
  description: "Test description"
  level: "Undergraduate"
""", encoding='utf-8')
    
    # Create minimal output config
    output_config = config_dir / "output_config.yaml"
    output_config.write_text("""
output:
  base_directory: "output"
  directories:
    outlines: "outlines"
""", encoding='utf-8')
    
    loader = ConfigLoader(config_dir)
    
    # get_modules() should load from outline by default
    modules = loader.get_modules(outline_path=sample_outline_json)
    
    assert len(modules) == 3
    assert modules[0]["module_id"] == 1


def test_config_loader_get_module_by_id_default_behavior(sample_outline_json):
    """Test that get_module_by_id() now loads from outline by default."""
    loader = ConfigLoader("config")
    
    # get_module_by_id() should load from outline by default
    module = loader.get_module_by_id(1, outline_path=sample_outline_json)
    
    assert module is not None
    assert module["module_id"] == 1
    assert module["module_name"] == "Cell Biology"


def test_config_loader_get_modules_backward_compatibility(sample_outline_json):
    """Test backward compatibility with from_outline=False."""
    loader = ConfigLoader("config")
    
    # Old behavior should return empty list
    modules = loader.get_modules(from_outline=False)
    
    assert modules == []


def test_outline_json_structure_validation(sample_outline_json):
    """Test that loaded modules have correct JSON structure."""
    loader = ConfigLoader("config")
    
    modules = loader.get_modules_from_outline(sample_outline_json)
    
    # Validate first module structure
    module = modules[0]
    assert "module_id" in module
    assert "module_name" in module
    assert "module_description" in module
    assert "sessions" in module
    
    # Validate first session structure
    session = module["sessions"][0]
    assert "session_number" in session
    assert "session_title" in session
    assert "subtopics" in session
    assert "learning_objectives" in session
    assert "key_concepts" in session
    assert "rationale" in session
    
    # Validate data types
    assert isinstance(session["subtopics"], list)
    assert isinstance(session["learning_objectives"], list)
    assert isinstance(session["key_concepts"], list)


def test_no_outline_found_returns_empty_list(tmp_path, monkeypatch):
    """Test that get_modules_from_outline returns empty list when no outline found."""
    # Change to empty tmp directory
    monkeypatch.chdir(tmp_path)
    
    # Create config directory
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    
    # Create minimal configs
    (config_dir / "course_config.yaml").write_text("""
course:
  name: "Test"
  description: "Test"
  level: "Test"
""")
    (config_dir / "output_config.yaml").write_text("""
output:
  base_directory: "output"
""")
    
    loader = ConfigLoader(config_dir)
    
    modules = loader.get_modules_from_outline()
    
    assert modules == []


def test_invalid_json_returns_empty_list(tmp_path):
    """Test that invalid JSON file returns empty list."""
    # Create invalid JSON file
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{ invalid json }", encoding='utf-8')
    
    loader = ConfigLoader("config")
    
    modules = loader.get_modules_from_outline(invalid_file)
    
    assert modules == []

