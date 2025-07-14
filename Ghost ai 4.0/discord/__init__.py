"""
Discord Module for Ghost AI 3.0

This module contains Discord integration components.
"""

from .discord_bot import GhostAIDiscordIntegration, create_discord_integration, start_discord_integration
from .elite_webhook_layout import _post_tickets_to_webhook, _post_streak_webhook, _post_normal_ticket_webhook

__all__ = ['GhostAIDiscordIntegration', 'create_discord_integration', 'start_discord_integration', '_post_tickets_to_webhook', '_post_streak_webhook', '_post_normal_ticket_webhook'] 