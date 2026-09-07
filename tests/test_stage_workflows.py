"""Tests for outline workflow and secondary stage modules (logic moved from scripts/03 and 05)."""

import os

import pytest

from src.generate.stages.outline_workflow import maybe_override_course_info
from src.generate.stages.secondary import (
    SECONDARY_TYPES_DEFAULT,
    find_latest_outline,
    load_session_content,
)

pytestmark = pytest.mark.unit


class TestLoadSessionContent:
    """Test session content loading from session folders."""

    def test_combines_primary_and_diagrams_in_order(self, tmp_path):
        """Test primary materials load in order and diagrams are fenced as mermaid."""
        session = tmp_path / "session_01"
        session.mkdir()
        (session / "lecture.md").write_text("Lecture body", encoding="utf-8")
        (session / "lab.md").write_text("Lab body", encoding="utf-8")
        (session / "diagram_2.mmd").write_text("flowchart TB\n  A-->B", encoding="utf-8")
        (session / "diagram_1.mmd").write_text("flowchart LR\n  C-->D", encoding="utf-8")
        (session / "unrelated.txt").write_text("noise", encoding="utf-8")

        content = load_session_content(session)

        assert "## Lecture" in content
        assert "Lecture body" in content
        assert "## Lab" in content
        assert content.index("Lecture body") < content.index("Lab body")
        assert "```mermaid" in content
        assert "flowchart LR" in content
        assert "flowchart TB" in content
        assert content.index("diagram_1.mmd") < content.index("diagram_2.mmd")
        assert "noise" not in content

    def test_missing_session_dir(self, tmp_path):
        """Test a nonexistent session directory yields empty content."""
        assert load_session_content(tmp_path / "does_not_exist") == ""

    def test_empty_session_dir(self, tmp_path):
        """Test an existing but empty session directory yields empty content."""
        session = tmp_path / "session_02"
        session.mkdir()
        assert load_session_content(session) == ""


class TestFindLatestOutline:
    """Test outline discovery across search locations."""

    def test_explicit_path_used_directly(self, tmp_path):
        """Test an explicit path is read without discovery."""
        outline = tmp_path / "course_outline_20260101_000000.md"
        outline.write_text("explicit outline", encoding="utf-8")
        assert find_latest_outline(outline) == "explicit outline"

    def test_explicit_missing_path_returns_empty(self, tmp_path):
        """Test a nonexistent explicit path yields empty string."""
        assert find_latest_outline(tmp_path / "missing.md") == ""

    def test_discovers_most_recent_across_locations(self, tmp_path, monkeypatch):
        """Test newest outline wins across root and course-specific directories."""
        monkeypatch.chdir(tmp_path)
        root_outline = tmp_path / "output" / "outlines" / "course_outline_20260101_000000.md"
        course_outline = tmp_path / "output" / "biology" / "outlines" / "course_outline_20260102_000000.md"
        root_outline.parent.mkdir(parents=True)
        course_outline.parent.mkdir(parents=True)
        root_outline.write_text("root outline", encoding="utf-8")
        course_outline.write_text("course outline", encoding="utf-8")
        # Make the root outline the newest by modification time
        os.utime(root_outline, (2_000_000_000, 2_000_000_000))
        os.utime(course_outline, (1_000_000_000, 1_000_000_000))

        assert find_latest_outline() == "root outline"

    def test_no_outlines_found_returns_empty(self, tmp_path, monkeypatch):
        """Test no outlines anywhere yields empty string."""
        monkeypatch.chdir(tmp_path)
        assert find_latest_outline() == ""


class TestSecondaryTypesDefault:
    """Test the secondary material type table."""

    def test_all_six_types_present(self):
        """Test the default type list matches the documented six types."""
        assert SECONDARY_TYPES_DEFAULT == [
            "application",
            "extension",
            "visualization",
            "integration",
            "investigation",
            "open_questions",
        ]


class TestMaybeOverrideCourseInfo:
    """Test interactive course metadata override (defaults accepted)."""

    def test_accepts_all_defaults(self, monkeypatch):
        """Test pressing Enter everywhere keeps defaults and builds structure config."""
        import logging

        monkeypatch.setattr("builtins.input", lambda *a, **k: "")

        course = {
            "name": "Biology",
            "subject": "life sciences",
            "level": "Undergraduate",
            "description": "Intro course",
            "additional_constraints": "",
        }
        logger = logging.getLogger("test_outline_workflow")

        updated, output_dir, structure = maybe_override_course_info(course, logger, None)

        assert updated["name"] == "Biology"
        assert updated["subject"] == "life sciences"
        assert updated["level"] == "Undergraduate"
        assert output_dir == "output"  # default when no config_loader supplied
        assert structure["num_modules"] == 5
        assert structure["total_sessions"] == 10  # default: num_modules * 2
        assert structure["avg_sessions_per_module"] == 2.0
        assert structure["should_clear_output"] is False
        assert structure["min_subtopics"] == 3
        assert structure["max_subtopics"] == 7
        assert structure["min_objectives"] == 3
        assert structure["max_objectives"] == 7
        assert structure["min_concepts"] == 3
        assert structure["max_concepts"] == 7

    def test_invalid_module_count_falls_back_to_default(self, monkeypatch):
        """Test non-numeric module count input falls back to the default."""
        import logging

        # Feed one bad value for module count, then defaults everywhere else
        responses = ["not a number"] + [""] * 20
        it = iter(responses)
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(it))

        course = {"name": "X", "subject": "Y", "level": "Z"}
        logger = logging.getLogger("test_outline_workflow")

        _, _, structure = maybe_override_course_info(course, logger, None)

        assert structure["num_modules"] == 5
        assert structure["total_sessions"] == 10

    def test_clear_output_yes_sets_flag(self, monkeypatch):
        """Test answering 'y' to the clear prompt sets should_clear_output."""
        import logging

        responses = [""] * 15 + ["y"]
        it = iter(responses)
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(it))

        course = {"name": "X", "subject": "Y", "level": "Z"}
        logger = logging.getLogger("test_outline_workflow")

        _, _, structure = maybe_override_course_info(course, logger, None)

        assert structure["should_clear_output"] is True
