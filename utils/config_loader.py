"""Configuration loader for arXiv Paper Summarizer."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """Load and manage configuration from YAML file."""

    def __init__(self, config_path: str = None):
        """
        Initialize ConfigLoader.

        Args:
            config_path: Path to configuration file. If None, uses default path.
        """
        if config_path is None:
            # Get project root directory
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by key path.

        Args:
            key_path: Dot-separated path to configuration value (e.g., 'arxiv.category')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.

        Args:
            section: Section name (e.g., 'arxiv', 'llm')

        Returns:
            Configuration section dictionary
        """
        return self.config.get(section, {})

    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = self._load_config()
