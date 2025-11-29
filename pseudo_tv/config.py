from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

try:  # Optional dependency; configs also accept JSON
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - exercised in envs without PyYAML
    yaml = None

from .models import Channel, ChannelRule


@dataclass
class Config:
    """Configuration for the pseudo TV app."""

    media_roots: Sequence[Path]
    channels: List[Channel] = field(default_factory=list)
    state_path: Path = Path(".pseudo_tv_state.json")

    @classmethod
    def load(cls, path: Path) -> "Config":
        data = cls._load_data(path)
        media_roots = [Path(p) for p in data.get("media_roots", [])]
        channels = [cls._parse_channel(entry) for entry in data.get("channels", [])]
        state_path = Path(data.get("state_path", ".pseudo_tv_state.json"))
        return cls(media_roots=media_roots, channels=channels, state_path=state_path)

    @staticmethod
    def _load_data(path: Path) -> Dict:
        text = path.read_text()
        if yaml is not None:
            return yaml.safe_load(text)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Install PyYAML or keep the config JSON-compatible (the bundled example is JSON)."
            ) from exc

    @staticmethod
    def _parse_channel(raw: Dict) -> Channel:
        rule = ChannelRule(
            include_genres=raw.get("include_genres", []) or [],
            include_shows=raw.get("include_shows", []) or [],
            include_paths=raw.get("include_paths", []) or [],
            exclude_genres=raw.get("exclude_genres", []) or [],
            minimum_runtime_minutes=raw.get("minimum_runtime_minutes"),
            maximum_runtime_minutes=raw.get("maximum_runtime_minutes"),
        )
        return Channel(
            name=raw["name"],
            rules=rule,
            shuffle=bool(raw.get("shuffle", True)),
            allow_repeats=bool(raw.get("allow_repeats", False)),
        )

    def to_dict(self) -> Dict:
        return {
            "media_roots": [str(p) for p in self.media_roots],
            "state_path": str(self.state_path),
            "channels": [
                {
                    "name": channel.name,
                    "shuffle": channel.shuffle,
                    "allow_repeats": channel.allow_repeats,
                    "include_genres": channel.rules.include_genres,
                    "include_shows": channel.rules.include_shows,
                    "include_paths": channel.rules.include_paths,
                    "exclude_genres": channel.rules.exclude_genres,
                    "minimum_runtime_minutes": channel.rules.minimum_runtime_minutes,
                    "maximum_runtime_minutes": channel.rules.maximum_runtime_minutes,
                }
                for channel in self.channels
            ],
        }

    def save(self, path: Path) -> None:
        data = self.to_dict()
        if yaml is not None:
            yaml.safe_dump(data, path.open("w"), sort_keys=False)
        else:
            json.dump(data, path.open("w"), indent=2)

    def save_state(self, state: Dict) -> None:
        self.state_path.write_text(json.dumps(state, indent=2, default=str))

    def load_state(self) -> Dict:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text())
        except json.JSONDecodeError:
            return {}
