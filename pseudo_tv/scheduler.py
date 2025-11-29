from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, Iterable, List

from .models import Channel, MediaItem, ScheduleEntry


class Scheduler:
    """Builds schedules for channels and supports EPG-like guides."""

    def __init__(self, channels: Iterable[Channel], seed: int | None = None):
        self.channels = list(channels)
        self.random = random.Random(seed)

    def build_schedule(self, library: Iterable[MediaItem], start: datetime, duration: timedelta) -> List[ScheduleEntry]:
        schedule: List[ScheduleEntry] = []
        horizon = start + duration
        for channel in self.channels:
            channel.select_items(library)
            pool = list(channel.items)
            if channel.shuffle:
                self.random.shuffle(pool)
            pointer = start
            index = 0
            while pointer < horizon:
                if not pool:
                    raise ValueError(f"Channel '{channel.name}' has no items to schedule.")
                item = pool[index % len(pool)]
                schedule.append(ScheduleEntry(channel=channel, item=item, start=pointer))
                pointer += item.duration
                index += 1
                if not channel.allow_repeats and index >= len(pool):
                    break
        schedule.sort(key=lambda e: (e.start, e.channel.name))
        return schedule

    @staticmethod
    def guide(schedule: List[ScheduleEntry], window_start: datetime, window_end: datetime) -> Dict[str, List[ScheduleEntry]]:
        by_channel: Dict[str, List[ScheduleEntry]] = {}
        for entry in schedule:
            if entry.end <= window_start or entry.start >= window_end:
                continue
            by_channel.setdefault(entry.channel.name, []).append(entry)
        return by_channel

    @staticmethod
    def current_program(schedule: List[ScheduleEntry], now: datetime) -> List[ScheduleEntry]:
        return [entry for entry in schedule if entry.overlaps(now)]
