from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List

from .models import Channel, ScheduleEntry


@dataclass
class PlayerState:
    last_positions: Dict[str, str]

    @classmethod
    def from_disk(cls, path: Path) -> "PlayerState":
        if not path.exists():
            return cls(last_positions={})
        try:
            data = json.loads(path.read_text())
            return cls(last_positions=data.get("last_positions", {}))
        except json.JSONDecodeError:
            return cls(last_positions={})

    def save(self, path: Path) -> None:
        payload = {"last_positions": self.last_positions}
        path.write_text(json.dumps(payload, indent=2))


class Player:
    """Simulates playback of scheduled items."""

    def __init__(self, schedule: List[ScheduleEntry], state_path: Path):
        self.schedule = schedule
        self.state_path = state_path
        self.state = PlayerState.from_disk(state_path)

    def now_playing(self, now: datetime) -> Dict[str, ScheduleEntry]:
        entries = [entry for entry in self.schedule if entry.overlaps(now)]
        return {entry.channel.name: entry for entry in entries}

    def progress(self, entry: ScheduleEntry, now: datetime) -> float:
        elapsed = (now - entry.start).total_seconds()
        total = entry.item.duration.total_seconds()
        return max(0.0, min(1.0, elapsed / total))

    def remember_positions(self, now: datetime) -> None:
        positions = {}
        for entry in self.schedule:
            if entry.overlaps(now):
                fraction = self.progress(entry, now)
                positions[entry.channel.name] = f"{fraction:.2%}"  # human readable
        self.state.last_positions.update(positions)
        self.state.save(self.state_path)

    def describe_now_playing(self, now: datetime) -> str:
        lines: List[str] = []
        entries = self.now_playing(now)
        if not entries:
            return "No scheduled content right now."
        for name, entry in sorted(entries.items()):
            fraction = self.progress(entry, now)
            elapsed = entry.item.duration * fraction
            remaining = entry.item.duration - elapsed
            lines.append(
                f"Channel {name}: {entry.item.label} (elapsed {elapsed}, remaining {remaining}, start {entry.start:%H:%M})"
            )
        return "\n".join(lines)

    def upcoming(self, now: datetime, horizon: timedelta = timedelta(hours=2)) -> Dict[str, List[ScheduleEntry]]:
        window_end = now + horizon
        upcoming: Dict[str, List[ScheduleEntry]] = {}
        for entry in self.schedule:
            if entry.start <= now:
                continue
            if entry.start > window_end:
                continue
            upcoming.setdefault(entry.channel.name, []).append(entry)
        return upcoming

    def describe_upcoming(self, now: datetime, horizon: timedelta = timedelta(hours=2)) -> str:
        listings = self.upcoming(now, horizon=horizon)
        if not listings:
            return "No upcoming items in window."
        lines: List[str] = []
        for name, entries in sorted(listings.items()):
            lines.append(f"Channel {name}:")
            for entry in entries:
                lines.append(f"  - {entry.start:%H:%M} {entry.item.label} ({entry.item.duration})")
        return "\n".join(lines)

    @staticmethod
    def summarize_channels(channels: Iterable[Channel]) -> str:
        lines = []
        for channel in channels:
            lines.append(
                f"- {channel.name}: genres={channel.rules.include_genres or 'any'}, shows={channel.rules.include_shows or 'any'}, repeat={'yes' if channel.allow_repeats else 'no'}"
            )
        return "\n".join(lines)
