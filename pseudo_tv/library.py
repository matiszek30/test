from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Iterable, List, Sequence

from .models import MediaItem


_META_SUFFIX = ".meta.json"


@dataclass
class LibraryScanner:
    """Scans folders for media files and infers metadata.

    The scanner uses filename parsing with fallbacks to companion
    ``*.meta.json`` files that can include ``title``, ``duration_minutes``,
    ``genre``, ``show``, ``season``, ``episode``, and ``year``.
    """

    media_roots: Sequence[Path]
    supported_extensions: Sequence[str] = (".mp4", ".mkv", ".mov", ".avi", ".mp3")

    def scan(self) -> List[MediaItem]:
        items: List[MediaItem] = []
        for root in self.media_roots:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in self.supported_extensions and not path.name.endswith(_META_SUFFIX):
                    continue
                if path.name.endswith(_META_SUFFIX):
                    # Metadata file; will be consumed when paired with a real media file.
                    continue
                metadata = self._load_companion_metadata(path)
                item = self._build_item(path, metadata)
                items.append(item)
        return items

    def _load_companion_metadata(self, media_path: Path) -> dict:
        companion = media_path.with_name(media_path.name + _META_SUFFIX)
        if companion.exists():
            try:
                return json.loads(companion.read_text())
            except json.JSONDecodeError:
                pass
        return {}

    def _build_item(self, path: Path, metadata: dict) -> MediaItem:
        parsed = self._parse_filename(path.name)
        title = metadata.get("title") or parsed.get("title") or path.stem
        duration_minutes = metadata.get("duration_minutes") or parsed.get("duration") or 30
        genre = metadata.get("genre") or parsed.get("genre")
        show = metadata.get("show") or parsed.get("show")
        season = metadata.get("season") or parsed.get("season")
        episode = metadata.get("episode") or parsed.get("episode")
        year = metadata.get("year") or parsed.get("year")
        return MediaItem(
            path=path,
            title=title,
            duration=timedelta(minutes=float(duration_minutes)),
            genre=genre,
            show=show,
            season=season,
            episode=episode,
            year=year,
        )

    def _parse_filename(self, name: str) -> dict:
        # Pattern: Show.Name.S01E02.Title[Genre].ext or Movie.Title.2012[Genre].ext
        base = name.rsplit(".", 1)[0]
        tv_match = re.match(
            r"(?P<show>.+?)\s*[.-]\s*S(?P<season>\d{1,2})E(?P<episode>\d{1,2})\s*[.-]?\s*(?P<title>[^\[]+)?(?:\[(?P<genre>[^\]]+)\])?",
            base,
            re.IGNORECASE,
        )
        if tv_match:
            data = tv_match.groupdict()
            season = int(data["season"])
            episode = int(data["episode"])
            return {
                "show": data.get("show"),
                "season": season,
                "episode": episode,
                "title": (data.get("title") or "").replace(".", " ").strip() or f"Episode {episode}",
                "genre": (data.get("genre") or "").strip() or None,
            }
        movie_match = re.match(r"(?P<title>.+?)\s*(?P<year>\d{4})?(?:\[(?P<genre>[^\]]+)\])?", base)
        if movie_match:
            data = movie_match.groupdict()
            year = int(data["year"]) if data.get("year") else None
            return {
                "title": (data.get("title") or "").replace(".", " ").strip(),
                "year": year,
                "genre": (data.get("genre") or "").strip() or None,
            }
        return {"title": base}

    @staticmethod
    def format_items(items: Iterable[MediaItem]) -> str:
        lines = []
        for item in items:
            details = [f"Duration: {item.duration}"]
            if item.genre:
                details.append(f"Genre: {item.genre}")
            if item.show:
                details.append(f"Show: {item.show}")
            if item.year:
                details.append(f"Year: {item.year}")
            lines.append(f"- {item.label} ({'; '.join(details)}) -> {item.path}")
        return "\n".join(lines)
