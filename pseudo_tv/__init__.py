"""Pseudo TV standalone Python app.

This package provides tools to build pseudo-live channels from a media library.
"""

__version__ = "0.1.0"

__all__ = [
    "MediaItem",
    "ChannelRule",
    "Channel",
    "ScheduleEntry",
    "LibraryScanner",
    "Config",
    "Scheduler",
    "Player",
    "__version__",
]

from .models import Channel, ChannelRule, MediaItem, ScheduleEntry
from .library import LibraryScanner
from .config import Config
from .scheduler import Scheduler
from .player import Player
