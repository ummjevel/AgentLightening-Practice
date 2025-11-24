"""Agent Lightning integration for tracking and optimization."""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


logger = logging.getLogger(__name__)


class AgentLightningTracker:
    """
    Tracker for Agent Lightning integration.

    This class provides tracking capabilities for prompts, responses, and rewards
    to enable Agent Lightning's optimization features.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AgentLightningTracker.

        Args:
            config: Configuration dictionary with agent_lightning settings
        """
        agl_config = config.get('agent_lightning', {})

        self.enabled = agl_config.get('enabled', False)
        self.store_path = Path(agl_config.get('store_path', 'data/lightning_store'))
        self.track_prompts = agl_config.get('track_prompts', True)
        self.track_responses = agl_config.get('track_responses', True)
        self.track_rewards = agl_config.get('track_rewards', True)

        if self.enabled:
            self.store_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Agent Lightning tracking enabled: {self.store_path}")
        else:
            logger.info("Agent Lightning tracking disabled")

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.events = []

    def emit_prompt(self, agent_name: str, prompt: str, metadata: Optional[Dict] = None) -> str:
        """
        Track a prompt event.

        Args:
            agent_name: Name of the agent
            prompt: The prompt text
            metadata: Additional metadata

        Returns:
            Event ID for this prompt
        """
        if not self.enabled or not self.track_prompts:
            return ""

        event_id = f"{agent_name}_{len(self.events)}"
        event = {
            'event_id': event_id,
            'event_type': 'prompt',
            'agent_name': agent_name,
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'metadata': metadata or {}
        }

        self.events.append(event)
        logger.debug(f"Tracked prompt event: {event_id}")

        return event_id

    def emit_response(self, event_id: str, response: str, metadata: Optional[Dict] = None) -> None:
        """
        Track a response event.

        Args:
            event_id: ID of the corresponding prompt event
            response: The response text
            metadata: Additional metadata
        """
        if not self.enabled or not self.track_responses:
            return

        event = {
            'event_id': f"{event_id}_response",
            'event_type': 'response',
            'parent_event_id': event_id,
            'timestamp': datetime.now().isoformat(),
            'response': response,
            'metadata': metadata or {}
        }

        self.events.append(event)
        logger.debug(f"Tracked response event for: {event_id}")

    def emit_reward(self, event_id: str, reward: float, reason: str = "") -> None:
        """
        Track a reward event.

        Args:
            event_id: ID of the event to reward
            reward: Reward value (typically -1.0 to 1.0)
            reason: Reason for the reward
        """
        if not self.enabled or not self.track_rewards:
            return

        event = {
            'event_id': f"{event_id}_reward",
            'event_type': 'reward',
            'parent_event_id': event_id,
            'timestamp': datetime.now().isoformat(),
            'reward': reward,
            'reason': reason
        }

        self.events.append(event)
        logger.debug(f"Tracked reward event: {event_id} -> {reward}")

    def emit_tool_call(self, agent_name: str, tool_name: str,
                       args: Dict, result: Any, metadata: Optional[Dict] = None) -> str:
        """
        Track a tool call event.

        Args:
            agent_name: Name of the agent
            tool_name: Name of the tool
            args: Tool arguments
            result: Tool result
            metadata: Additional metadata

        Returns:
            Event ID for this tool call
        """
        if not self.enabled:
            return ""

        event_id = f"{agent_name}_tool_{len(self.events)}"
        event = {
            'event_id': event_id,
            'event_type': 'tool_call',
            'agent_name': agent_name,
            'timestamp': datetime.now().isoformat(),
            'tool_name': tool_name,
            'args': args,
            'result': str(result)[:500],  # Truncate long results
            'metadata': metadata or {}
        }

        self.events.append(event)
        logger.debug(f"Tracked tool call event: {event_id}")

        return event_id

    def save_session(self) -> None:
        """Save tracked events to disk."""
        if not self.enabled or not self.events:
            return

        session_file = self.store_path / f"session_{self.session_id}.json"

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump({
                'session_id': self.session_id,
                'start_time': self.events[0]['timestamp'] if self.events else None,
                'end_time': datetime.now().isoformat(),
                'total_events': len(self.events),
                'events': self.events
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved Agent Lightning session: {session_file}")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of tracked events.

        Returns:
            Summary dictionary
        """
        event_types = {}
        for event in self.events:
            event_type = event['event_type']
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            'session_id': self.session_id,
            'enabled': self.enabled,
            'total_events': len(self.events),
            'event_types': event_types,
            'store_path': str(self.store_path)
        }
