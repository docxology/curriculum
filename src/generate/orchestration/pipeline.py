"""Pipeline orchestration for educational course generation.

This module coordinates the full workflow of generating educational course materials.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient, LLMError
from src.generate.stages.stage1_outline import OutlineGenerator
from src.generate.formats.lectures import LectureGenerator
from src.generate.formats.diagrams import DiagramGenerator
from src.generate.formats.questions import QuestionGenerator
from src.generate.formats.study_notes import StudyNotesGenerator
from src.generate.formats.labs import LabGenerator
from src.generate.processors.parser import OutlineParser
from src.utils.helpers import ensure_directory, slugify
from src.utils.logging_setup import log_section_header
from src.utils.error_collector import ErrorCollector
from src.utils.summary_generator import generate_stage_summary
from src.utils.content_analysis import (
    calculate_quality_score,
    aggregate_validation_results,
    validate_cross_session_consistency
)
import requests


logger = logging.getLogger(__name__)


class ContentGenerator:
    """Main pipeline for generating educational course materials.
    
    This class coordinates the entire workflow:
    1. Generate course outline
    2. Parse outline into modules
    3. Generate content for each module (lectures, diagrams, questions)
    
    Attributes:
        config_loader: Configuration loader
        llm_client: LLM client for generation
        outline_generator: Outline generator
        lecture_generator: Lecture generator
        diagram_generator: Diagram generator
        question_generator: Question generator
    """
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the pipeline.
        
        Args:
            config_loader: Configuration loader instance
        """
        self.config_loader = config_loader
        self.error_collector = ErrorCollector()
        
        # Setup logging
        self._setup_logging()
        
        logger.info("Initializing Educational Course Generator pipeline...")
        
        # Initialize LLM client with logging configuration
        llm_config = config_loader.get_llm_parameters()
        logging_intervals = config_loader.get_logging_intervals()
        self.llm_client = OllamaClient(llm_config, logging_config=logging_intervals)
        
        # Initialize generators
        self.outline_generator = OutlineGenerator(config_loader, self.llm_client)
        self.lecture_generator = LectureGenerator(config_loader, self.llm_client)
        self.lab_generator = LabGenerator(config_loader, self.llm_client)
        self.diagram_generator = DiagramGenerator(config_loader, self.llm_client)
        self.question_generator = QuestionGenerator(config_loader, self.llm_client)
        self.study_notes_generator = StudyNotesGenerator(config_loader, self.llm_client)
        
        logger.info("Pipeline initialized successfully")
    
    def _is_transient_error(self, error: Exception) -> bool:
        """Determine if an error is transient and should be retried.
        
        Transient errors are those that may succeed on retry:
        - Timeout errors (stream timeout, read timeout, connection timeout)
        - Connection errors (network issues, service unreachable)
        - Temporary service unavailability
        
        Permanent errors are not retried:
        - Validation errors
        - Configuration errors
        - Format errors
        
        Args:
            error: Exception to check
            
        Returns:
            True if error is transient (timeout, connection error), False otherwise
            
        Example:
            >>> generator._is_transient_error(LLMError("Stream timeout: 180s"))
            True
            >>> generator._is_transient_error(ValueError("Invalid config"))
            False
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # LLM errors that are transient
        if isinstance(error, LLMError):
            if any(keyword in error_str for keyword in [
                'timeout', 'connection', 'unreachable', 'stream timeout',
                'read timeout', 'connection timeout'
            ]):
                return True
        
        # Network errors
        if isinstance(error, (requests.ConnectionError, requests.Timeout)):
            return True
        
        # Check error message for transient indicators
        if any(keyword in error_str for keyword in [
            'timeout', 'connection', 'network', 'unreachable',
            'temporarily unavailable', 'service unavailable'
        ]):
            return True
        
        return False
    
    def _retry_generation(
        self,
        generation_func: Callable[[], Any],
        max_retries: int = 2,
        retry_delay: float = 2.0,
        operation_name: str = "generation"
    ) -> Any:
        """Retry a generation operation for transient failures.
        
        This method implements automatic retry with exponential backoff for
        transient failures (timeouts, connection errors). Permanent errors
        (validation, configuration) are not retried.
        
        Args:
            generation_func: Callable that performs the generation operation.
                           Should return the generated content or raise an exception.
            max_retries: Maximum number of retry attempts (default: 2, total attempts = 3)
            retry_delay: Initial delay between retries in seconds (default: 2.0).
                        Uses exponential backoff: delay * (2 ** attempt)
            operation_name: Name of operation for logging context (e.g., "lecture generation")
            
        Returns:
            Result from generation_func (typically generated content string)
            
        Raises:
            Exception: If all retries fail or if error is not transient
            
        Example:
            >>> lecture = generator._retry_generation(
            ...     lambda: generator.lecture_generator.generate_lecture(session_data),
            ...     max_retries=2,
            ...     operation_name="lecture generation"
            ... )
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return generation_func()
            except Exception as e:
                last_error = e
                
                # Only retry transient errors
                if not self._is_transient_error(e):
                    logger.debug(f"  Non-transient error in {operation_name}, not retrying: {e}")
                    raise
                
                # If we've exhausted retries, raise
                if attempt >= max_retries:
                    logger.warning(
                        f"  {operation_name} failed after {max_retries + 1} attempts "
                        f"(last error: {e})"
                    )
                    raise
                
                # Wait before retrying
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"  Transient error in {operation_name} (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                    f"Retrying in {wait_time:.1f}s..."
                )
                time.sleep(wait_time)
        
        # Should not reach here, but raise last error if we do
        raise last_error
        
    def _setup_logging(self) -> None:
        """Configure logging based on output config."""
        output_config = self.config_loader.get_output_paths()
        logging_config = output_config.get('logging', {})
        
        log_level = logging_config.get('level', 'INFO')
        
        # Set root logger level
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def _get_output_directories(self, course_name: Optional[str] = None) -> Dict[str, Path]:
        """Get output directory paths.
        
        Always returns course-specific paths under a subfolder. If course_name is not
        provided, attempts to extract from outline, otherwise derives from default course config.
        
        Args:
            course_name: Optional course template name. If provided, returns
                        course-specific paths (e.g., output/chemistry/outlines/).
                        If None, attempts to extract from outline or derives from default
                        course config (e.g., output/introductory_biology/outlines/).
        
        Returns:
            Dictionary of output directories (always under course subfolder)
        """
        # Try to get course name from outline if not provided
        if course_name is None:
            outline_data = self._load_latest_outline_json()
            if outline_data:
                course_metadata = outline_data.get('course_metadata', {})
                course_name = course_metadata.get('course_template')
        
        # Get output paths (always uses course-specific subfolder structure)
        # If course_name is None, get_output_paths() derives it from default course config
        output_config = self.config_loader.get_output_paths(course_name)
        base_dir = Path(output_config.get('base_directory', 'output'))
        directories = output_config.get('directories', {})
        
        return {
            name: Path(path)  # Paths are always course-specific (under subfolder)
            for name, path in directories.items()
        }
    
    def clear_output_directories(self, confirm: bool = True, course_name: Optional[str] = None) -> None:
        """Clear all output directories with optional confirmation.
        
        Args:
            confirm: If True, prompt for confirmation before clearing
            course_name: Optional course template name. If provided, clears course-specific directories.
        """
        import shutil
        
        dirs = self._get_output_directories(course_name)
        
        if confirm:
            logger.warning("\n⚠️  WARNING: This will delete all generated content in:")
            for name, path in dirs.items():
                if path.exists():
                    logger.warning(f"  - {path.resolve()}")
            response = input("\nProceed? (y/N): ").strip().lower()
            if response != 'y':
                logger.info("Clear operation cancelled by user")
                return
        
        logger.info("Clearing output directories...")
        cleared_count = 0
        for name, path in dirs.items():
            if path.exists():
                logger.info(f"Clearing {name}: {path}")
                # Delete all contents but keep the directory
                for item in path.iterdir():
                    if item.is_file():
                        item.unlink()
                        cleared_count += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        cleared_count += 1
                logger.info(f"  ✓ Cleared {name}")
        
        logger.info(f"Cleared {cleared_count} items from output directories")
        
    def _load_latest_outline_json(self) -> Optional[Dict[str, Any]]:
        """Load the most recent JSON outline.
        
        Delegates to ConfigLoader to find the outline file, then loads and parses it.
        
        Returns:
            Parsed JSON outline data or None if not found
        """
        # Use ConfigLoader to find the latest outline
        outline_path = self.config_loader._find_latest_outline_json()
        
        if not outline_path:
            logger.warning("No JSON outline found")
            logger.warning("Run stage 1 (outline generation) first: uv run python3 scripts/03_generate_outline.py")
            return None
        
        # Load and parse the JSON
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON outline from {outline_path}: {e}")
            return None
    
    def stage1_generate_outline(
        self, 
        num_modules: Optional[int] = None,
        total_sessions: Optional[int] = None,
        min_subtopics: Optional[int] = None,
        max_subtopics: Optional[int] = None,
        min_objectives: Optional[int] = None,
        max_objectives: Optional[int] = None,
        min_concepts: Optional[int] = None,
        max_concepts: Optional[int] = None,
        course_name: Optional[str] = None
    ) -> Path:
        """Stage 1: Generate course outline.
        
        Args:
            num_modules: Number of modules to generate (default: from config)
            total_sessions: Optional total session count (default: from config)
            min_subtopics: Minimum subtopics per session (default: from config)
            max_subtopics: Maximum subtopics per session (default: from config)
            min_objectives: Minimum learning objectives per session (default: from config)
            max_objectives: Maximum learning objectives per session (default: from config)
            min_concepts: Minimum key concepts per session (default: from config)
            max_concepts: Maximum key concepts per session (default: from config)
            course_name: Optional course template name for course-specific output paths
        
        Returns:
            Path to generated outline file
        """
        log_section_header(logger, "STAGE 1: Generating Course Outline", major=True)
        
        # Get course name from config loader if not provided
        if course_name is None:
            course_name = self.config_loader.get_current_course_template()
        
        dirs = self._get_output_directories(course_name)
        outline_dir = dirs.get('outlines', Path('output/outlines'))
        
        # Build bounds_override if any parameters provided
        bounds_override = None
        if any(x is not None for x in [min_subtopics, max_subtopics, min_objectives, max_objectives, min_concepts, max_concepts]):
            bounds_override = {}
            if min_subtopics is not None or max_subtopics is not None:
                bounds_override['subtopics'] = {}
                if min_subtopics is not None:
                    bounds_override['subtopics']['min'] = min_subtopics
                if max_subtopics is not None:
                    bounds_override['subtopics']['max'] = max_subtopics
            if min_objectives is not None or max_objectives is not None:
                bounds_override['learning_objectives'] = {}
                if min_objectives is not None:
                    bounds_override['learning_objectives']['min'] = min_objectives
                if max_objectives is not None:
                    bounds_override['learning_objectives']['max'] = max_objectives
            if min_concepts is not None or max_concepts is not None:
                bounds_override['key_concepts'] = {}
                if min_concepts is not None:
                    bounds_override['key_concepts']['min'] = min_concepts
                if max_concepts is not None:
                    bounds_override['key_concepts']['max'] = max_concepts
        
        # Generate outline with specified parameters
        outline = self.outline_generator.generate_outline(
            num_modules=num_modules,
            total_sessions=total_sessions,
            bounds_override=bounds_override
        )
        
        # Get JSON data for saving
        json_data = getattr(self.outline_generator, '_last_json_outline', None)
        
        # Save outline
        outline_path = self.outline_generator.save_outline(
            outline, 
            outline_dir,
            json_data=json_data
        )
        
        logger.info(f"Stage 1 complete. Outline saved to: {outline_path}")
        return outline_path
        
    def stage2_generate_content_by_session(
        self,
        module_ids: Optional[List[int]] = None,
        skip_existing: bool = False
    ) -> List[Dict[str, Any]]:
        """Stage 2: Generate PRIMARY content per SESSION (not per module).
        
        Args:
            module_ids: List of module IDs to process. If None, processes all.
                    
        Returns:
            List of results for each session
        """
        log_section_header(logger, "STAGE 2: Generating Primary Content (Session-Based)", major=True)
        
        # Load JSON outline to get session structure
        outline_data = self._load_latest_outline_json()
        if not outline_data:
            raise ValueError("No JSON outline found. Run stage 1 (outline generation) first.")
        
        # Extract course name from outline metadata
        course_metadata = outline_data.get('course_metadata', {})
        course_name = course_metadata.get('course_template')
        
        modules = outline_data.get('modules', [])
        
        # Filter by module_ids if specified
        if module_ids:
            modules = [m for m in modules if m.get('module_id') in module_ids]
        
        logger.info(f"Processing {len(modules)} modules with session-based generation")
        if course_name:
            logger.info(f"Using course-specific output directory: output/{course_name}/")
        
        dirs = self._get_output_directories(course_name)
        base_output_dir = dirs.get('modules', Path('output/modules'))
        
        results = []
        total_sessions = sum(len(m.get('sessions', [])) for m in modules)
        session_count = 0
        quality_results = []  # Collect quality scores for aggregation
        
        for module in modules:
            module_id = module.get('module_id')
            module_name = module.get('module_name', f'Module {module_id}')
            sessions = module.get('sessions', [])
            
            # Create module folder
            module_slug = slugify(f"module_{module_id:02d}_{module_name}")
            module_dir = base_output_dir / module_slug
            
            # Use structured logging for module header
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"Module {module_id}: {module_name} ({len(sessions)} sessions)")
            logger.info("=" * 60)
            
            for session in sessions:
                session_count += 1
                session_num = session.get('session_number')
                session_title = session.get('session_title', f'Session {session_num}')
                
                logger.info(f"\n[{session_count}/{total_sessions}] Session {session_num}: {session_title}")
                
                # Create session folder
                session_dir = module_dir / f"session_{session_num:02d}"
                ensure_directory(session_dir)
                
                session_result = {
                    'module_id': module_id,
                    'module_name': module_name,
                    'session_number': session_num,
                    'session_title': session_title,
                    'session_dir': session_dir
                }
                
                # Check if content already exists (incremental generation / resume capability)
                if skip_existing:
                    required_files = ['lecture.md', 'lab.md', 'study_notes.md', 'questions.md']
                    existing_files = [f for f in required_files if (session_dir / f).exists()]
                    if len(existing_files) == len(required_files):
                        logger.info(f"  ⏭️  Skipping session {session_num} (all files exist)")
                        session_result['status'] = 'skipped'
                        session_result['reason'] = 'files_exist'
                        results.append(session_result)
                        continue
                    elif existing_files:
                        logger.info(f"  ⚠️  Some files exist for session {session_num}, will regenerate missing files")
                        # Resume: only generate missing content
                        if (session_dir / "lecture.md").exists():
                            lecture_path = session_dir / "lecture.md"
                            lecture = lecture_path.read_text(encoding='utf-8')
                            session_result['lecture_path'] = lecture_path
                        if (session_dir / "lab.md").exists():
                            lab_path = session_dir / "lab.md"
                            lab = lab_path.read_text(encoding='utf-8')
                            session_result['lab_path'] = lab_path
                        if (session_dir / "study_notes.md").exists():
                            notes_path = session_dir / "study_notes.md"
                            notes = notes_path.read_text(encoding='utf-8')
                            session_result['notes_path'] = notes_path
                        # Check for existing diagrams
                        existing_diagrams = sorted(session_dir.glob("diagram_*.mmd"))
                        if existing_diagrams:
                            session_result['diagram_paths'] = existing_diagrams
                        if (session_dir / "questions.md").exists():
                            questions_path = session_dir / "questions.md"
                            questions = questions_path.read_text(encoding='utf-8')
                            session_result['questions_path'] = questions_path
                
                try:
                    # Import cleanup functions
                    from src.generate.processors.cleanup import (
                        clean_conversational_artifacts,
                        standardize_placeholders,
                        full_cleanup_pipeline
                    )
                    
                    # Prepare session-specific data for generators
                    session_data = {
                        'id': module_id,
                        'name': module_name,
                        'session_number': session_num,
                        'session_title': session_title,
                        'subtopics': session.get('subtopics', []),
                        'learning_objectives': session.get('learning_objectives', []),
                        'key_concepts': session.get('key_concepts', []),
                        'rationale': session.get('rationale', '')
                    }
                    
                    # Build comprehensive outline context for lecture generation
                    # Include module description and rationale for better context
                    module_desc = module.get('module_description', '')
                    session_rationale = session.get('rationale', '')
                    outline_context_parts = [
                        f"Module {module_id}/{len(modules)}: {module_name}",
                        f"Session {session_num}/{total_sessions}: {session_title}"
                    ]
                    if module_desc:
                        outline_context_parts.append(f"Module Overview: {module_desc}")
                    if session_rationale:
                        outline_context_parts.append(f"Session Rationale: {session_rationale}")
                    outline_context = "\n".join(outline_context_parts)
                    
                    # Generate lecture (with context) - with retry for transient failures
                    if 'lecture_path' not in session_result:
                        logger.info("  → Generating lecture...")
                        lecture = self._retry_generation(
                            lambda: self.lecture_generator.generate_lecture(
                                session_data,
                                outline_context=outline_context,
                                session_number=session_num,
                                total_sessions=total_sessions,
                                session_title=session_title,
                                error_collector=self.error_collector
                            ),
                            max_retries=2,
                            operation_name="lecture generation"
                        )
                        # Apply cleanup
                        lecture, _ = full_cleanup_pipeline(lecture, "lecture")
                        lecture_path = session_dir / "lecture.md"
                        lecture_path.write_text(lecture, encoding='utf-8')
                        session_result['lecture_path'] = lecture_path
                    else:
                        lecture = session_result.get('lecture', '')
                        if not lecture:
                            lecture = session_result['lecture_path'].read_text(encoding='utf-8')
                    
                    # Generate lab (with lecture context) - with retry for transient failures
                    if 'lab_path' not in session_result:
                        logger.info("  → Generating lab...")
                        lab = self._retry_generation(
                            lambda: self.lab_generator.generate_lab(
                                session_data,
                                lab_number=session_num,
                                lecture_context=lecture,
                                error_collector=self.error_collector
                            ),
                            max_retries=2,
                            operation_name="lab generation"
                        )
                        # Apply cleanup
                        lab, _ = full_cleanup_pipeline(lab, "lab")
                        lab_path = session_dir / "lab.md"
                        lab_path.write_text(lab, encoding='utf-8')
                        session_result['lab_path'] = lab_path
                    else:
                        lab = session_result.get('lab', '')
                        if not lab:
                            lab = session_result['lab_path'].read_text(encoding='utf-8')
                    
                    # Generate study notes (with lecture context) - with retry for transient failures
                    if 'notes_path' not in session_result:
                        logger.info("  → Generating study notes...")
                        notes = self._retry_generation(
                            lambda: self.study_notes_generator.generate_study_notes(
                                session_data,
                                lecture_context=lecture,
                                error_collector=self.error_collector
                            ),
                            max_retries=2,
                            operation_name="study notes generation"
                        )
                        # Apply cleanup
                        notes, _ = full_cleanup_pipeline(notes, "study_notes")
                        notes_path = session_dir / "study_notes.md"
                        notes_path.write_text(notes, encoding='utf-8')
                        session_result['notes_path'] = notes_path
                    else:
                        notes = session_result.get('notes', '')
                        if not notes:
                            notes = session_result['notes_path'].read_text(encoding='utf-8')
                    
                    # Generate diagrams (can be parallelized) - with retry for transient failures
                    logger.info("  → Generating diagrams...")
                    # Get configured number of diagrams per session
                    subtopics = session.get('subtopics', [])
                    num_diagrams = min(self.config_loader.get_diagrams_per_session(), len(subtopics))
                    diagram_paths = []
                    
                    # Generate diagrams in parallel (they're independent)
                    def generate_single_diagram(i: int) -> Path:
                        topic = subtopics[i] if i < len(subtopics) else session_title
                        context = f"{module_name} - {session_title}: {topic}"
                        diagram = self._retry_generation(
                            lambda: self.diagram_generator.generate_diagram(
                                topic,
                                context,
                                error_collector=self.error_collector,
                                module_id=module_id,
                                session_num=session_num
                            ),
                            max_retries=2,
                            operation_name=f"diagram {i+1} generation"
                        )
                        diagram_path = session_dir / f"diagram_{i+1}.mmd"
                        diagram_path.write_text(diagram, encoding='utf-8')
                        return diagram_path
                    
                    # Use parallel generation for diagrams (max 4 workers to avoid overwhelming LLM)
                    if num_diagrams > 1:
                        with ThreadPoolExecutor(max_workers=min(4, num_diagrams)) as executor:
                            futures = [executor.submit(generate_single_diagram, i) for i in range(num_diagrams)]
                            for future in as_completed(futures):
                                try:
                                    diagram_paths.append(future.result())
                                except Exception as e:
                                    logger.error(f"Error generating diagram: {e}")
                    else:
                        # Single diagram - no need for parallelization
                        if num_diagrams > 0:
                            try:
                                diagram_paths.append(generate_single_diagram(0))
                            except Exception as e:
                                logger.error(f"Error generating diagram: {e}")
                    
                    session_result['diagram_paths'] = diagram_paths
                    
                    # Generate questions (with lecture and lab context) - with retry for transient failures
                    if 'questions_path' not in session_result:
                        logger.info("  → Generating questions...")
                        questions = self._retry_generation(
                            lambda: self.question_generator.generate_questions(
                                session_data,
                                lecture_context=lecture,
                                lab_context=lab,
                                error_collector=self.error_collector
                            ),
                            max_retries=2,
                            operation_name="questions generation"
                        )
                        # Apply cleanup
                        questions, _ = full_cleanup_pipeline(questions, "questions")
                        questions_path = session_dir / "questions.md"
                        questions_path.write_text(questions, encoding='utf-8')
                        session_result['questions_path'] = questions_path
                    else:
                        questions = session_result.get('questions', '')
                        if not questions:
                            questions = session_result['questions_path'].read_text(encoding='utf-8')
                    
                    # Calculate quality scores for generated content
                    from src.utils.content_analysis import analyze_lecture, analyze_questions, analyze_study_notes
                    
                    session_quality = {}
                    content_reqs = self.config_loader.get_content_requirements()
                    
                    if 'lecture_path' in session_result:
                        lecture_metrics = analyze_lecture(lecture, requirements=content_reqs.get('lecture', {}))
                        session_quality['lecture'] = calculate_quality_score(lecture_metrics, content_reqs.get('lecture', {}), "lecture")
                    
                    if 'questions_path' in session_result:
                        questions_metrics = analyze_questions(questions)
                        num_questions_val = session_data.get('num_questions', 10)
                        session_quality['questions'] = calculate_quality_score(questions_metrics, {'num_questions': num_questions_val}, "questions")
                    
                    if 'notes_path' in session_result:
                        notes_metrics = analyze_study_notes(notes, requirements=content_reqs.get('study_notes', {}))
                        session_quality['study_notes'] = calculate_quality_score(notes_metrics, content_reqs.get('study_notes', {}), "study_notes")
                    
                    session_result['quality_scores'] = session_quality
                    quality_results.append(session_quality)
                    
                    session_result['status'] = 'success'
                    logger.info(f"  ✓ Session {session_num} completed")
                    
                except Exception as e:
                    # Provide actionable error message with recovery suggestions
                    error_msg = str(e)
                    recovery_suggestions = []
                    
                    # Extract request ID from LLMError if present
                    request_id = None
                    if isinstance(e, LLMError):
                        if "[" in error_msg and "]" in error_msg:
                            try:
                                request_id = error_msg[error_msg.find("[")+1:error_msg.find("]")]
                            except (ValueError, IndexError):
                                pass
                    
                    # Determine error type and material type context
                    error_type = type(e).__name__
                    material_types_generated = []
                    if 'lecture_path' in session_result:
                        material_types_generated.append('lecture')
                    if 'lab_path' in session_result:
                        material_types_generated.append('lab')
                    if 'notes_path' in session_result:
                        material_types_generated.append('study_notes')
                    if 'diagram_paths' in session_result and session_result['diagram_paths']:
                        material_types_generated.append('diagrams')
                    if 'questions_path' in session_result:
                        material_types_generated.append('questions')
                    
                    material_context = f"Generated: {', '.join(material_types_generated)}" if material_types_generated else "No materials generated"
                    
                    # Categorize error and provide specific suggestions
                    is_timeout = "timeout" in error_msg.lower() or "stream timeout" in error_msg.lower()
                    is_connection = "connection" in error_msg.lower() or "unreachable" in error_msg.lower()
                    is_validation = "validation" in error_msg.lower() or "format" in error_msg.lower()
                    
                    if is_timeout:
                        recovery_suggestions.extend([
                            "1. Increase timeout in config/llm_config.yaml for this operation",
                            "2. Check Ollama service status: curl http://localhost:11434/api/version",
                            "3. Consider using a faster model or checking system resources",
                            "4. See docs/TROUBLESHOOTING.md for timeout resolution steps",
                            "5. Retry this session: the pipeline will automatically retry transient failures"
                        ])
                    elif is_connection:
                        recovery_suggestions.extend([
                            "1. Check if Ollama is running: ollama serve",
                            "2. Verify Ollama is accessible: curl http://localhost:11434/api/version",
                            "3. Check network connectivity and firewall settings",
                            "4. Retry this session: the pipeline will automatically retry transient failures"
                        ])
                    elif is_validation:
                        recovery_suggestions.extend([
                            "1. Review generated content for format issues",
                            "2. Check content requirements in config/llm_config.yaml",
                            "3. Regenerate this session with --skip-existing to preserve other content"
                        ])
                    else:
                        recovery_suggestions.extend([
                            "1. Check logs for detailed error information",
                            "2. Verify configuration files are valid",
                            "3. Try regenerating this session: uv run python3 scripts/04_generate_primary.py --modules <module_id>"
                        ])
                    
                    # Log detailed error information
                    logger.error(f"  ✗ Error processing session {session_num}: {error_type}")
                    logger.error(f"     Module: {module_name} (ID: {module_id})")
                    logger.error(f"     Session: {session_title}")
                    logger.error(f"     {material_context}")
                    if request_id:
                        logger.error(f"     Request ID: {request_id} (filter logs: grep '[{request_id}]' output/logs/*.log)")
                    logger.error(f"     Error: {error_msg}")
                    if recovery_suggestions:
                        logger.error("  Recovery suggestions:")
                        for suggestion in recovery_suggestions:
                            logger.error(f"    {suggestion}")
                    
                    session_result['status'] = 'error'
                    session_result['error'] = error_msg
                    session_result['error_type'] = error_type
                    session_result['request_id'] = request_id
                    session_result['material_types_generated'] = material_types_generated
                    session_result['recovery_suggestions'] = recovery_suggestions
                
                results.append(session_result)
        
        # Summary statistics
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = len(results) - successful
        
        # Aggregate quality scores
        if quality_results:
            aggregated_quality = aggregate_validation_results([
                {'quality_score': q.get('lecture', {})} for q in quality_results if 'lecture' in q
            ])
            logger.info("")
            logger.info("=" * 60)
            logger.info("QUALITY SCORE SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Average Quality Score: {aggregated_quality.get('average_score', 0):.1f}/100")
            logger.info(f"Overall Quality: {aggregated_quality.get('overall_quality', 'unknown')}")
            logger.info(f"Quality Distribution: {aggregated_quality.get('quality_distribution', {})}")
            if aggregated_quality.get('common_issues'):
                logger.info("Most Common Issues:")
                for issue_info in aggregated_quality['common_issues'][:3]:
                    logger.info(f"  - {issue_info['issue']} (count: {issue_info['count']})")
            logger.info("=" * 60)
        
        # Cross-session consistency check
        consistency_result = validate_cross_session_consistency(outline_data)
        if consistency_result['total_issues'] > 0:
            logger.warning(f"Cross-session consistency: {consistency_result['total_issues']} issues found")
            for rec in consistency_result['recommendations'][:3]:
                logger.info(f"  Recommendation: {rec}")
        
        # Generate stage summary with error collector
        generate_stage_summary(
            self.error_collector,
            "Primary Materials Generation",
            logger,
            total_items=len(results),
            successful_items=successful,
            failed_items=failed
        )
        
        return results
        
    def run(
        self,
        generate_outline: bool = True,
        modules_to_process: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Run the complete pipeline.
        
        Args:
            generate_outline: Whether to generate new outline (Stage 1)
            modules_to_process: Optional list of module IDs to process.
                               If None, processes all modules.
                               
        Returns:
            Dictionary with pipeline results
        """
        logger.info("\n" + "="*80)
        log_section_header(logger, "EDUCATIONAL COURSE GENERATOR - PIPELINE START", major=True)
        logger.info("")
        
        results = {}
        
        # Stage 1: Generate outline (optional)
        if generate_outline:
            outline_path = self.stage1_generate_outline()
            results['outline_path'] = outline_path
        else:
            logger.info("Skipping Stage 1 (outline generation)")
            
        # Stage 2: Generate content (session-based)
        session_results = self.stage2_generate_content_by_session(modules_to_process)
        results['session_results'] = session_results
        results['sessions_generated'] = len(session_results)
        
        # Summary
        successful = sum(1 for r in session_results if r.get('status') == 'success')
        failed = len(session_results) - successful
        
        # Count unique modules processed
        modules_processed = len(set(r.get('module_id') for r in session_results))
        
        logger.info("\n" + "="*80)
        log_section_header(logger, "PIPELINE COMPLETE", major=True)
        logger.info(f"  • Modules processed: {modules_processed}")
        logger.info(f"  • Sessions processed: {len(session_results)}")
        logger.info(f"  • Successful: {successful}")
        logger.info(f"  • Failed: {failed}")
        logger.info("═" * 80)
        logger.info("")
        
        return results

