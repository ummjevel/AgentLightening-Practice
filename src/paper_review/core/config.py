"""Configuration management."""

from pathlib import Path
from typing import Any, Dict

import yaml
from loguru import logger


class ConfigLoader:
    """Configuration loader from YAML file."""

    def __init__(self, config_path: str | Path = "config/config.yaml"):
        """
        Initialize config loader.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return {}

        try:
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f) or {}

            logger.info(f"Loaded configuration from {self.config_path}")
            return self.config

        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.

        Args:
            key: Dot-separated key path (e.g., 'arxiv.category')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.

        Args:
            section: Section name

        Returns:
            Section dictionary
        """
        return self.config.get(section, {})

    def reload(self) -> Dict[str, Any]:
        """
        Reload configuration from file.

        Returns:
            Updated configuration dictionary
        """
        return self.load()
