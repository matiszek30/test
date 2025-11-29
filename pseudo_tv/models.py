from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class MediaItem:
    """Represents a single playable item in the library."""

    path: Path
    title: str
    duration: timedelta
    genre: Optional[str] = None
    show: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    year: Optional[int] = None

    @property
    def is_episode(self) -> bool:
        return self.show is not None

    @property
    def label(self) -> str:
        if self.is_episode:
            season_str = f"S{self.season:02d}" if self.season is not None else "S??"
            episode_str = f"E{self.episode:02d}" if self.episode is not None else "E??"
            return f"{self.show} {season_str}{episode_str} - {self.title}"
        year = f" ({self.year})" if self.year else ""
        return f"{self.title}{year}"


@dataclass
class ChannelRule:
    """Filtering rules for channel creation."""

    include_genres: List[str] = field(default_factory=list)
    include_shows: List[str] = field(default_factory=list)
    include_paths: List[str] = field(default_factory=list)
    exclude_genres: List[str] = field(default_factory=list)
    minimum_runtime_minutes: Optional[int] = None
    maximum_runtime_minutes: Optional[int] = None

    def matches(self, item: MediaItem) -> bool:
        if self.include_genres:
            if not item.genre or item.genre.lower() not in {g.lower() for g in self.include_genres}:
                return False
        if self.include_shows:
            if not item.show or item.show.lower() not in {s.lower() for s in self.include_shows}:
                return False
        if self.include_paths:
            if not any(str(item.path).startswith(p) for p in self.include_paths):
                return False
        if self.exclude_genres and item.genre and item.genre.lower() in {g.lower() for g in self.exclude_genres}:
            return False
        minutes = item.duration.total_seconds() / 60
        if self.minimum_runtime_minutes and minutes < self.minimum_runtime_minutes:
            return False
        if self.maximum_runtime_minutes and minutes > self.maximum_runtime_minutes:
            return False
        return True


@dataclass
class Channel:
    """A pseudo channel built from matching library items."""

    name: str
    rules: ChannelRule
    items: List[MediaItem] = field(default_factory=list)
    shuffle: bool = True
    allow_repeats: bool = False

    def select_items(self, library: Iterable[MediaItem]) -> None:
        self.items = [item for item in library if self.rules.matches(item)]
        if not self.items:
            raise ValueError(f"Channel '{self.name}' has no matching items.")


@dataclass
class ScheduleEntry:
    channel: Channel
    item: MediaItem
    start: datetime

    @property
    def end(self) -> datetime:
        return self.start + self.item.duration

    def overlaps(self, moment: datetime) -> bool:
        return self.start <= moment < self.end

    def label(self) -> str:
        return f"{self.item.label} ({self.item.duration})"
