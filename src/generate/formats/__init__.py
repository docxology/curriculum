"""Content generator base classes and format-specific generators.

This package provides specialized generators for different content formats:
- lectures: LectureGenerator
- labs: LabGenerator
- study_notes: StudyNotesGenerator
- diagrams: DiagramGenerator
- questions: QuestionGenerator
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config.loader import ConfigLoader
    from src.llm.client import OllamaClient


logger = logging.getLogger(__name__)


class ContentGenerator:
    """Base class for content generators.
    
    Attributes:
        config_loader: Configuration loader instance
        llm_client: LLM client for text generation
    """
    
    def __init__(self, config_loader: "ConfigLoader", llm_client: "OllamaClient"):
        """Initialize the content generator.
        
        Args:
            config_loader: Configuration loader instance
            llm_client: LLM client instance
        """
        self.config_loader = config_loader
        self.llm_client = llm_client
        
        logger.debug(f"Initialized {self.__class__.__name__}")


__all__ = ["ContentGenerator"]


