"""Base agent class for all agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from loguru import logger


class BaseAgent(ABC):
    """모든 에이전트의 베이스 클래스."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base agent.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logger.bind(agent=self.__class__.__name__)

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the agent's main functionality.

        This method must be implemented by all subclasses.
        """
        pass
