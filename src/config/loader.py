"""Configuration loader for educational course generator.

This module provides a ConfigLoader class to load and validate YAML configuration
files for the course generator system.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from src.utils.helpers import slugify


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


class ConfigLoader:
    """Loads and provides access to configuration files.
    
    This class handles loading YAML configuration files and provides
    convenient methods to access configuration values with validation.
    
    Attributes:
        config_dir: Path to the configuration directory
    """
    
    def __init__(self, config_dir: str | Path = "config"):
        """Initialize the ConfigLoader.
        
        Args:
            config_dir: Path to directory containing config files
            
        Raises:
            ConfigurationError: If config directory doesn't exist
        """
        self.config_dir = Path(config_dir)
        
        if not self.config_dir.exists():
            raise ConfigurationError(
                f"Config directory not found: {self.config_dir}"
            )
            
        logger.info(f"Initialized ConfigLoader with directory: {self.config_dir}")
        
        # Cache loaded configs
        self._course_config: Optional[Dict] = None
        self._llm_config: Optional[Dict] = None
        self._output_config: Optional[Dict] = None
        self._current_course_template: Optional[str] = None  # Track current course template name
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file.
        
        Args:
            filename: Name of the config file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            ConfigurationError: If file doesn't exist or is invalid YAML
        """
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise ConfigurationError(f"Config file not found: {filepath}")
            
        try:
            with open(filepath, 'r') as f:
                config = yaml.safe_load(f)
                logger.debug(f"Loaded config from {filename}")
                return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {filename}: {e}")
    
    def list_available_courses(self) -> List[Dict[str, Any]]:
        """List available course templates from config/courses/ directory.
        
        Scans the config/courses/ directory for YAML files and returns
        metadata about each course template.
        
        Returns:
            List of dictionaries with course information:
            - name: Course template name (filename without extension)
            - filename: Full filename
            - course_info: Course metadata (name, description, level, subject)
            
        Example:
            >>> loader = ConfigLoader("config")
            >>> courses = loader.list_available_courses()
            >>> # Returns: [{"name": "biology", "filename": "biology.yaml", "course_info": {...}}, ...]
        """
        courses_dir = self.config_dir / "courses"
        
        if not courses_dir.exists():
            logger.debug(f"Course templates directory not found: {courses_dir}")
            return []
        
        courses = []
        yaml_files = sorted(courses_dir.glob("*.yaml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                course_name = yaml_file.stem
                course_info = config.get("course", {})
                
                courses.append({
                    "name": course_name,
                    "filename": yaml_file.name,
                    "course_info": course_info
                })
                logger.debug(f"Found course template: {course_name}")
            except Exception as e:
                logger.warning(f"Failed to load course template {yaml_file.name}: {e}")
                continue
        
        logger.info(f"Found {len(courses)} course template(s) in {courses_dir}")
        return courses
    
    def load_course_template(self, course_name: str) -> Dict[str, Any]:
        """Load a specific course template from config/courses/.
        
        Args:
            course_name: Name of the course template (filename without .yaml extension)
            
        Returns:
            Full course configuration dictionary (same structure as load_course_config())
            
        Raises:
            ConfigurationError: If course template not found or invalid
            
        Example:
            >>> loader = ConfigLoader("config")
            >>> template = loader.load_course_template("biology")
            >>> # Returns: {"course": {...}}
        """
        courses_dir = self.config_dir / "courses"
        template_file = courses_dir / f"{course_name}.yaml"
        
        if not template_file.exists():
            available = [c["name"] for c in self.list_available_courses()]
            raise ConfigurationError(
                f"Course template '{course_name}' not found in {courses_dir}. "
                f"Available courses: {', '.join(available) if available else 'none'}"
            )
        
        try:
            with open(template_file, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded course template: {course_name}")
            return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in course template {course_name}: {e}")
            
    def load_course_config(self, course_template: Optional[str] = None) -> Dict[str, Any]:
        """Load course configuration.
        
        Args:
            course_template: Optional course template name to load from config/courses/.
                           If None, loads default course_config.yaml.
        
        Returns:
            Course configuration dictionary
            
        Example:
            >>> loader = ConfigLoader("config")
            >>> config = loader.load_course_config()  # Loads default
            >>> config = loader.load_course_config("biology")  # Loads biology template
        """
        if course_template:
            # Track current course template
            self._current_course_template = course_template
            # Load from template (don't cache, as template may change)
            return self.load_course_template(course_template)
        
        # Load default (cached)
        if self._course_config is None:
            self._course_config = self._load_yaml("course_config.yaml")
            # Clear course template when loading default
            self._current_course_template = None
        return self._course_config
    
    def get_current_course_template(self) -> Optional[str]:
        """Get the currently loaded course template name.
        
        Returns:
            Course template name (e.g., "chemistry", "biology") or None if using default config
        """
        return self._current_course_template
        
    def load_llm_config(self) -> Dict[str, Any]:
        """Load LLM configuration.
        
        Returns:
            LLM configuration dictionary
        """
        if self._llm_config is None:
            self._llm_config = self._load_yaml("llm_config.yaml")
        return self._llm_config
        
    def load_output_config(self) -> Dict[str, Any]:
        """Load output configuration.
        
        Returns:
            Output configuration dictionary
        """
        if self._output_config is None:
            self._output_config = self._load_yaml("output_config.yaml")
        return self._output_config
        
    def get_course_info(self, course_template: Optional[str] = None) -> Dict[str, Any]:
        """Get basic course information.
        
        Args:
            course_template: Optional course template name to load from config/courses/.
                           If None, uses default course_config.yaml.
        
        Returns:
            Dictionary with course name, description, level, subject, etc.
        """
        config = self.load_course_config(course_template)
        return config.get("course", {})
    
    def get_course_subject(self) -> str:
        """Get course subject/expertise area.
        
        Returns:
            Subject string (e.g., "biology", "chemistry", "general education")
            Defaults to "general education" if not specified
        """
        course_info = self.get_course_info()
        return course_info.get("subject", "general education")
    
    def get_language(self) -> str:
        """Get language for course content generation.
        
        Checks environment variable COURSE_LANGUAGE first, then config file.
        
        Returns:
            Language string (e.g., "English", "Spanish", "French")
            Defaults to "English" if not specified
        """
        import os
        # Check environment variable first (set by run_pipeline.py)
        env_language = os.environ.get("COURSE_LANGUAGE")
        if env_language:
            return env_language
        
        llm_config = self.load_llm_config()
        llm_section = llm_config.get("llm", {})
        return llm_section.get("language", "English")
        
    def get_modules(
        self, 
        outline_path: Optional[Path] = None,
        from_outline: bool = True
    ) -> List[Dict[str, Any]]:
        """Get modules from JSON outline or static config.
        
        Args:
            outline_path: Optional path to specific outline JSON file
            from_outline: If True (default), load from JSON outline.
                         If False, return static modules from course_config (deprecated).
        
        Returns:
            List of module dictionaries from outline or empty list if from_outline=False
            
        Example:
            >>> loader = ConfigLoader("config")
            >>> modules = loader.get_modules()  # Loads from latest outline
            >>> modules = loader.get_modules(outline_path=Path("outline.json"))  # Loads from specific outline
            >>> modules = loader.get_modules(from_outline=False)  # Returns [] (no static modules)
        """
        if not from_outline:
            # Static modules are deprecated - return empty list
            logger.debug("from_outline=False: returning empty list (static modules deprecated)")
            return []
        return self.get_modules_from_outline(outline_path)
        
    def get_module_by_id(
        self, 
        module_id: int,
        outline_path: Optional[Path] = None,
        from_outline: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get module by ID from JSON outline or static config.
        
        Args:
            module_id: The module ID to find
            outline_path: Optional path to specific outline JSON file
            from_outline: If True (default), load from JSON outline.
                         If False, return None (no static modules available).
            
        Returns:
            Module dictionary if found, None otherwise
            
        Example:
            >>> loader = ConfigLoader("config")
            >>> module = loader.get_module_by_id(1)  # Loads from latest outline
            >>> module = loader.get_module_by_id(1, outline_path=Path("outline.json"))  # From specific outline
            >>> module = loader.get_module_by_id(1, from_outline=False)  # Returns None (no static modules)
        """
        if not from_outline:
            # Static modules are deprecated - return None
            logger.debug(f"from_outline=False: returning None for module_id={module_id} (static modules deprecated)")
            return None
        return self.get_module_by_id_from_outline(module_id, outline_path)
    
    def _find_latest_outline_json(self, outline_path: Optional[Path] = None, course_name: Optional[str] = None) -> Optional[Path]:
        """Find the most recent JSON outline file.
        
        Searches multiple possible locations:
        1. Explicit path (if provided)
        2. Course-specific directory: output/{course_name}/outlines/ (if course_name provided)
        3. Config-specified output directory
        4. Project root output/outlines/
        5. scripts/output/outlines/
        6. All course-specific directories: output/{course}/outlines/ (when course_name not provided, for batch processing)
        
        Args:
            outline_path: Optional explicit path to outline file
            course_name: Optional course template name to search in course-specific directory
            
        Returns:
            Path to most recent outline JSON or None if not found
        """
        # If explicit path provided, use it
        if outline_path:
            outline_path = Path(outline_path)
            if outline_path.exists():
                logger.info(f"Using specified outline: {outline_path.resolve()}")
                return outline_path
            else:
                logger.warning(f"Specified outline not found: {outline_path}")
                return None
        
        # Collect all possible outline directories
        search_paths = []
        
        # 1. Course-specific directory (if course_name provided)
        if course_name:
            try:
                output_config = self.get_output_paths(course_name)
                base_dir = Path(output_config.get('base_directory', 'output'))
                directories = output_config.get('directories', {})
                course_outline_dir = Path(directories.get('outlines', 'outlines'))
                if course_outline_dir not in search_paths:
                    search_paths.append(course_outline_dir)
                logger.debug(f"Added course-specific search path: {course_outline_dir}")
            except Exception as e:
                logger.debug(f"Could not get course-specific outline directory: {e}")
        
        # 2. Config-specified directory (default, for backward compatibility)
        try:
            output_config = self.get_output_paths()  # No course_name = default paths
            base_dir = Path(output_config.get('base_directory', 'output'))
            directories = output_config.get('directories', {})
            config_outline_dir = base_dir / directories.get('outlines', 'outlines')
            if config_outline_dir not in search_paths:
                search_paths.append(config_outline_dir)
        except Exception as e:
            logger.debug(f"Could not get config outline directory: {e}")
        
        # 3. Project root output/outlines (backward compatibility)
        root_outline_dir = Path('output/outlines')
        if root_outline_dir not in search_paths:
            search_paths.append(root_outline_dir)
        
        # 4. scripts/output/outlines (common when run from scripts/)
        scripts_outline_dir = Path('scripts/output/outlines')
        if scripts_outline_dir not in search_paths:
            search_paths.append(scripts_outline_dir)
        
        # 5. Discover and search all course-specific directories (for batch processing)
        # When course_name is not provided, search in all course subdirectories
        if not course_name:
            # Search in output/ for course-specific directories
            base_output_dir = Path('output')
            if base_output_dir.exists():
                for course_dir in base_output_dir.iterdir():
                    if course_dir.is_dir() and not course_dir.name.startswith('.'):
                        course_outlines = course_dir / 'outlines'
                        if course_outlines.exists() and course_outlines not in search_paths:
                            search_paths.append(course_outlines)
                            logger.debug(f"Added course-specific search path: {course_outlines}")
            
            # Also check scripts/output/ for course-specific directories
            scripts_output_dir = Path('scripts/output')
            if scripts_output_dir.exists():
                for course_dir in scripts_output_dir.iterdir():
                    if course_dir.is_dir() and not course_dir.name.startswith('.'):
                        course_outlines = course_dir / 'outlines'
                        if course_outlines.exists() and course_outlines not in search_paths:
                            search_paths.append(course_outlines)
                            logger.debug(f"Added course-specific search path: {course_outlines}")
        
        # Find all JSON outlines across all search paths
        all_json_files = []
        for search_dir in search_paths:
            if search_dir.exists():
                json_files = list(search_dir.glob('course_outline_*.json'))
                all_json_files.extend(json_files)
                logger.debug(f"Searched {search_dir}: found {len(json_files)} JSON outline(s)")
        
        if not all_json_files:
            logger.warning("No JSON outline found in any search location:")
            for path in search_paths:
                logger.warning(f"  - {path.resolve()}")
            return None
        
        # Sort by modification time (most recent first)
        latest_json = max(all_json_files, key=lambda p: p.stat().st_mtime)
        latest_json_resolved = latest_json.resolve()
        logger.info(f"Found most recent outline: {latest_json_resolved}")
        
        return latest_json_resolved
    
    def get_modules_from_outline(self, outline_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Load modules from JSON outline file.
        
        Searches for the most recent outline JSON if path not specified.
        
        Args:
            outline_path: Optional path to specific outline JSON file.
                         If None, finds most recent in standard locations.
            
        Returns:
            List of module dictionaries from outline, or empty list if not found
            
        Example:
            >>> loader = ConfigLoader("config")
            >>> modules = loader.get_modules_from_outline()
            >>> # Returns: [{"module_id": 1, "module_name": "...", "sessions": [...]}, ...]
        """
        import json
        
        # Find outline file
        outline_file = self._find_latest_outline_json(outline_path)
        
        if not outline_file:
            logger.error("No outline JSON found. Generate one first:")
            logger.error("  uv run python3 scripts/03_generate_outline.py")
            return []
        
        # Load and parse JSON
        try:
            with open(outline_file, 'r', encoding='utf-8') as f:
                outline_data = json.load(f)
            
            modules = outline_data.get('modules', [])
            logger.info(f"Loaded {len(modules)} modules from outline: {outline_file.name}")
            
            return modules
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON outline: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading outline: {e}")
            return []
    
    def get_module_by_id_from_outline(
        self, 
        module_id: int, 
        outline_path: Optional[Path] = None
    ) -> Optional[Dict[str, Any]]:
        """Load specific module by ID from JSON outline.
        
        Args:
            module_id: Module ID to find
            outline_path: Optional path to specific outline JSON file
            
        Returns:
            Module dictionary if found, None otherwise
            
        Example:
            >>> loader = ConfigLoader("config")
            >>> module = loader.get_module_by_id_from_outline(1)
            >>> # Returns: {"module_id": 1, "module_name": "...", "sessions": [...]}
        """
        modules = self.get_modules_from_outline(outline_path)
        
        for module in modules:
            if module.get('module_id') == module_id:
                logger.debug(f"Found module {module_id}: {module.get('module_name')}")
                return module
        
        logger.warning(f"Module {module_id} not found in outline")
        return None
    
    def get_course_defaults(self) -> Dict[str, Any]:
        """Get course structure defaults.
        
        Returns:
            Dictionary with num_modules, total_sessions.
            Falls back to sensible defaults if not specified in config.
        """
        course_info = self.get_course_info()
        defaults = course_info.get("defaults", {})
        
        return {
            "num_modules": defaults.get("num_modules", 5),
            "total_sessions": defaults.get("total_sessions", 15),
            "sessions_per_module": defaults.get("sessions_per_module", None)
        }
    
    def get_outline_bounds(self) -> Dict[str, Dict[str, int]]:
        """Get min/max bounds for outline generation fields.
        
        Returns:
            Dictionary with min/max for subtopics, learning_objectives, key_concepts
        """
        llm_config = self.get_llm_config()
        outline_config = llm_config.get('outline_generation', {})
        items_per_field = outline_config.get('items_per_field', {})
        
        return {
            'subtopics': items_per_field.get('subtopics', {'min': 3, 'max': 7}),
            'learning_objectives': items_per_field.get('learning_objectives', {'min': 3, 'max': 7}),
            'key_concepts': items_per_field.get('key_concepts', {'min': 3, 'max': 7})
        }
    
    def get_content_requirements(self) -> Dict[str, Dict[str, int]]:
        """Get content generation requirements for different content types.
        
        Returns:
            Dictionary with requirements for all content types (primary and secondary)
        """
        llm_config = self.get_llm_config()
        content_config = llm_config.get('content_generation', {})
        
        return {
            'lecture': content_config.get('lecture', {
                'min_examples': 5,
                'max_examples': 15,
                'min_sections': 4,
                'max_sections': 8,
                'min_word_count': 1000,
                'max_word_count': 1500
            }),
            'study_notes': content_config.get('study_notes', {
                'min_key_concepts': 3,
                'max_key_concepts': 10,
                'max_word_count': 1200
            }),
            'application': content_config.get('application', {
                'min_applications': 3,
                'max_applications': 5,
                'min_words_per_application': 150,
                'max_words_per_application': 200,
                'max_total_words': 1000
            }),
            'extension': content_config.get('extension', {
                'min_topics': 3,
                'max_topics': 4,
                'min_words_per_topic': 100,
                'max_words_per_topic': 150,
                'max_total_words': 600
            }),
            'visualization': content_config.get('visualization', {
                'min_diagram_elements': 6,
                'min_nodes': 10,
                'min_connections': 8
            }),
            'diagram': content_config.get('visualization', {
                'min_diagram_elements': 6,
                'min_nodes': 10,
                'min_connections': 8
            }),
            'integration': content_config.get('integration', {
                'min_connections': 3,
                'max_total_words': 1000
            }),
            'investigation': content_config.get('investigation', {
                'min_questions': 3,
                'max_total_words': 1000
            }),
            'open_questions': content_config.get('open_questions', {
                'min_questions': 3,
                'max_total_words': 1000
            })
        }
    
    def get_diagrams_per_session(self) -> int:
        """Get the configured number of diagrams to generate per session.
        
        Returns:
            Number of diagrams per session (default: 4)
        """
        llm_config = self.get_llm_config()
        content_config = llm_config.get('content_generation', {})
        return content_config.get('diagrams_per_session', 4)
        
    def get_llm_config(self) -> Dict[str, Any]:
        """Get full LLM configuration.
        
        Returns:
            Complete LLM configuration dictionary including prompts and settings
        """
        return self.load_llm_config()
    
    def get_llm_parameters(self) -> Dict[str, Any]:
        """Get LLM parameters.
        
        Returns:
            Dictionary containing LLM configuration parameters
        """
        config = self.load_llm_config()
        llm_params = config.get("llm", {})
        
        # #region agent log
        import json
        try:
            with open('/Users/4d/Documents/GitHub/biology/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "config-load",
                    "hypothesisId": "B",
                    "location": "loader.py:618",
                    "message": "LLM parameters loaded from config",
                    "data": {"timeout": llm_params.get("timeout"), "model": llm_params.get("model")},
                    "timestamp": int(time.time() * 1000)
                }) + "\n")
        except: pass
        # #endregion
        
        return llm_params
    
    def get_operation_timeout(self, operation: str) -> int:
        """Get timeout for a specific operation.
        
        Args:
            operation: Operation name (e.g., "outline", "lecture", "lab")
            
        Returns:
            Timeout in seconds. Returns operation-specific timeout if configured,
            otherwise returns base timeout from llm.timeout.
        """
        config = self.load_llm_config()
        llm_params = config.get("llm", {})
        base_timeout = llm_params.get("timeout", 180)
        
        # Check for operation-specific timeouts
        operation_timeouts = llm_params.get("operation_timeouts", {})
        if operation_timeouts and operation in operation_timeouts:
            timeout = operation_timeouts[operation]
            logger.debug(f"Using operation-specific timeout for '{operation}': {timeout}s (base: {base_timeout}s)")
            return timeout
        
        # Check for default operation timeout
        if operation_timeouts and "default" in operation_timeouts:
            timeout = operation_timeouts["default"]
            logger.debug(f"Using default operation timeout for '{operation}': {timeout}s (base: {base_timeout}s)")
            return timeout
        
        # Fall back to base timeout
        logger.debug(f"Using base timeout for '{operation}': {base_timeout}s")
        return base_timeout
        
    def get_prompt_template(self, template_name: str) -> Dict[str, str]:
        """Get a specific prompt template.
        
        Args:
            template_name: Name of the template (e.g., 'outline', 'lecture')
            
        Returns:
            Dictionary with 'system' and 'template' keys
            
        Raises:
            ConfigurationError: If template not found
        """
        config = self.load_llm_config()
        prompts = config.get("prompts", {})
        
        if template_name not in prompts:
            raise ConfigurationError(
                f"Prompt template '{template_name}' not found in configuration"
            )
            
        return prompts[template_name]
    
    def _get_default_course_short_name(self) -> str:
        """Get the short name (slug) for the default course from course_config.yaml.
        
        Extracts the course name from the default course configuration and converts
        it to a URL-friendly slug (e.g., "Introductory Biology" → "introductory_biology").
        
        Returns:
            Slugified course name from default config, or "default" if not found
        """
        try:
            course_config = self.load_course_config()  # Loads default config
            course_info = course_config.get('course', {})
            course_name = course_info.get('name', 'Default Course')
            return slugify(course_name)
        except Exception as e:
            logger.debug(f"Could not extract default course name: {e}")
            return "default"
        
    def get_output_paths(self, course_name: Optional[str] = None) -> Dict[str, Any]:
        """Get output path configuration.
        
        Always uses course-specific subfolders. If course_name is not provided,
        derives a short name from the default course configuration.
        
        Args:
            course_name: Optional course template name. If provided, paths will be
                        course-specific (e.g., output/chemistry/outlines/).
                        If None, derives short name from default course config
                        (e.g., output/introductory_biology/outlines/).
        
        Returns:
            Dictionary containing output paths and settings. The 'directories' dict
            always contains course-specific paths under a subfolder.
        """
        config = self.load_output_config()
        output_config = config.get("output", {})
        
        # If no course name specified, derive from default course config
        if not course_name:
            course_name = self._get_default_course_short_name()
        
        # Construct course-specific paths (always use subfolder structure)
        base_dir = Path(output_config.get('base_directory', 'output'))
        course_dir = base_dir / course_name
        directories = output_config.get('directories', {})
        
        # Create course-specific directory paths
        course_specific_dirs = {}
        for name, subdir in directories.items():
            course_specific_dirs[name] = str(course_dir / subdir)
        
        # Return modified config with course-specific paths
        result = output_config.copy()
        result['directories'] = course_specific_dirs
        result['course_name'] = course_name  # Store for reference
        
        return result
    
    def get_logging_intervals(self) -> Dict[str, float]:
        """Get logging interval configuration.
        
        Returns heartbeat_interval and progress_log_interval from output config,
        with sensible defaults if not configured.
        
        Returns:
            Dictionary with keys:
            - heartbeat_interval: Interval for heartbeat logs (seconds, default: 5.0)
            - progress_log_interval: Interval for stream progress logs (seconds, default: 2.0)
            
        Example:
            >>> loader = ConfigLoader("config")
            >>> intervals = loader.get_logging_intervals()
            >>> # Returns: {"heartbeat_interval": 5.0, "progress_log_interval": 2.0}
        """
        try:
            config = self.load_output_config()
            logging_config = config.get("output", {}).get("logging", {})
            
            heartbeat_interval = logging_config.get("heartbeat_interval", 5.0)
            progress_log_interval = logging_config.get("progress_log_interval", 2.0)
            
            # Validate intervals are positive numbers
            if not isinstance(heartbeat_interval, (int, float)) or heartbeat_interval <= 0:
                logger.warning(
                    f"Invalid heartbeat_interval: {heartbeat_interval}. "
                    f"Must be positive. Using default: 5.0"
                )
                heartbeat_interval = 5.0
            
            if not isinstance(progress_log_interval, (int, float)) or progress_log_interval <= 0:
                logger.warning(
                    f"Invalid progress_log_interval: {progress_log_interval}. "
                    f"Must be positive. Using default: 2.0"
                )
                progress_log_interval = 2.0
            
            return {
                "heartbeat_interval": float(heartbeat_interval),
                "progress_log_interval": float(progress_log_interval)
            }
        except Exception as e:
            logger.warning(
                f"Could not load logging intervals from config: {e}. "
                f"Using defaults: heartbeat=5.0s, progress=2.0s"
            )
            return {
                "heartbeat_interval": 5.0,
                "progress_log_interval": 2.0
            }
    
    def _extract_course_name_from_outline(self, outline_path: Path) -> Optional[str]:
        """Extract course template name from outline JSON metadata.
        
        Args:
            outline_path: Path to outline JSON file
            
        Returns:
            Course template name if found in metadata, None otherwise
        """
        try:
            import json
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline_data = json.load(f)
            
            course_metadata = outline_data.get('course_metadata', {})
            return course_metadata.get('course_template')
        except Exception as e:
            logger.debug(f"Could not extract course name from outline {outline_path}: {e}")
            return None
        
    def validate_course_config(self) -> None:
        """Validate that course configuration has required fields.
        
        Raises:
            ConfigurationError: If required fields are missing
        """
        config = self.load_course_config()
        
        # Check for required top-level keys
        required_keys = ["course"]
        for key in required_keys:
            if key not in config:
                raise ConfigurationError(
                    f"Missing required field '{key}' in course configuration"
                )
                
        # Check course info
        course = config["course"]
        required_course_fields = ["name", "description", "level"]
        for field in required_course_fields:
            if field not in course:
                raise ConfigurationError(
                    f"Missing required field 'course.{field}' in course configuration"
                )
        
        # Subject is optional, defaults to "general education" if not present
        # No validation needed as it has a default
        
        # Validate defaults structure (optional but should be dict if present)
        if "defaults" in course:
            defaults = course["defaults"]
            if not isinstance(defaults, dict):
                raise ConfigurationError("'course.defaults' must be a dictionary")
            
            # Check that num_modules and total_sessions are positive if specified
            if "num_modules" in defaults:
                num_modules = defaults["num_modules"]
                if not isinstance(num_modules, int) or num_modules <= 0:
                    raise ConfigurationError("'course.defaults.num_modules' must be a positive integer")
            
            if "total_sessions" in defaults:
                total_sessions = defaults["total_sessions"]
                if not isinstance(total_sessions, int) or total_sessions <= 0:
                    raise ConfigurationError("'course.defaults.total_sessions' must be a positive integer")
                    
        logger.info("Course configuration validated successfully")
        
    def validate_timeout_config(self) -> None:
        """Validate timeout configuration values.
        
        Checks timeout values are within reasonable bounds and warns about
        very long timeouts that may indicate configuration issues.
        
        Raises:
            ConfigurationError: If timeout values are invalid
        """
        llm_config = self.load_llm_config()
        llm_params = llm_config.get("llm", {})
        
        # Validate base timeout
        base_timeout = llm_params.get("timeout", 180)
        if not isinstance(base_timeout, (int, float)) or base_timeout <= 0:
            raise ConfigurationError(
                f"Invalid base timeout: {base_timeout}. Must be a positive number."
            )
        
        # Warn about very long base timeouts
        if base_timeout > 600:  # 10 minutes
            logger.warning(
                f"Very long base timeout ({base_timeout}s = {base_timeout/60:.1f} minutes). "
                f"This may indicate a slow model or system. Consider using a faster model or "
                f"checking system resources."
            )
        elif base_timeout < 30:
            logger.warning(
                f"Very short base timeout ({base_timeout}s). This may cause frequent timeouts. "
                f"Consider increasing to at least 120s for most models."
            )
        
        # Validate operation-specific timeouts
        operation_timeouts = llm_params.get("operation_timeouts", {})
        if operation_timeouts:
            for operation, timeout in operation_timeouts.items():
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    raise ConfigurationError(
                        f"Invalid timeout for operation '{operation}': {timeout}. "
                        f"Must be a positive number."
                    )
                
                # Warn about very long operation timeouts
                if timeout > 900:  # 15 minutes
                    logger.warning(
                        f"Very long timeout for '{operation}' ({timeout}s = {timeout/60:.1f} minutes). "
                        f"This may indicate the operation is too complex or the model is too slow. "
                        f"Consider optimizing the operation or using a faster model."
                    )
                elif timeout < 30:
                    logger.warning(
                        f"Very short timeout for '{operation}' ({timeout}s). "
                        f"This may cause frequent timeouts. Consider increasing to at least 120s."
                    )
                
                # Warn if operation timeout is much longer than base timeout
                if timeout > base_timeout * 2:
                    logger.warning(
                        f"Operation '{operation}' timeout ({timeout}s) is more than 2x base timeout "
                        f"({base_timeout}s). This may indicate the operation needs optimization."
                    )
        
        # Suggest timeout values based on model size (if model info available)
        model = llm_params.get("model", "")
        if model:
            # Extract model size if available (e.g., "gemma3:4b" -> 4B)
            model_size_match = None
            if ":" in model:
                model_size_match = model.split(":")[-1]
            
            if model_size_match:
                try:
                    # Try to extract number (e.g., "4b" -> 4)
                    size_num = int(''.join(filter(str.isdigit, model_size_match)))
                    if size_num <= 4:
                        suggested_timeout = 120
                    elif size_num <= 8:
                        suggested_timeout = 180
                    elif size_num <= 13:
                        suggested_timeout = 240
                    else:
                        suggested_timeout = 300
                    
                    if base_timeout < suggested_timeout * 0.8:
                        logger.info(
                            f"Model '{model}' appears to be {size_num}B parameters. "
                            f"Suggested base timeout: {suggested_timeout}s (current: {base_timeout}s). "
                            f"Consider increasing timeout if you experience frequent timeouts."
                        )
                except (ValueError, AttributeError):
                    pass  # Couldn't parse model size, skip suggestion
        
        logger.debug("Timeout configuration validated successfully")
    
    def validate_all_configs(self) -> None:
        """Validate all configuration files.
        
        Raises:
            ConfigurationError: If any configuration is invalid
        """
        self.validate_course_config()
        
        # Validate LLM config has required fields
        llm_config = self.load_llm_config()
        if "llm" not in llm_config:
            raise ConfigurationError("Missing 'llm' section in LLM configuration")
            
        if "prompts" not in llm_config:
            raise ConfigurationError("Missing 'prompts' section in LLM configuration")
        
        # Validate timeout configuration
        self.validate_timeout_config()
            
        # Validate output config
        output_config = self.load_output_config()
        if "output" not in output_config:
            raise ConfigurationError("Missing 'output' section in output configuration")
            
        logger.info("All configurations validated successfully")

