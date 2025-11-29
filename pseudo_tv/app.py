from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from .config import Config
from .library import LibraryScanner
from .player import Player
from .scheduler import Scheduler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone pseudo TV application")
    parser.add_argument("config", type=Path, help="Path to YAML/JSON configuration")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scan", help="Scan media library")
    sub.add_parser("channels", help="List configured channels")

    guide = sub.add_parser("guide", help="Show guide window")
    guide.add_argument("--hours", type=float, default=4, help="Guide window length in hours")

    now = sub.add_parser("now", help="Show what is playing right now")

    upcoming = sub.add_parser("upcoming", help="Show upcoming schedule")
    upcoming.add_argument("--hours", type=float, default=2, help="Lookahead window in hours")

    init_cfg = sub.add_parser("init-config", help="Write a starter config file")
    init_cfg.add_argument("--output", type=Path, default=Path("pseudo_tv.example.yaml"))

    return parser


def load_app(config_path: Path):
    config = Config.load(config_path)
    scanner = LibraryScanner(config.media_roots)
    library = scanner.scan()
    scheduler = Scheduler(config.channels)
    schedule = scheduler.build_schedule(
        library=library,
        start=datetime.now().replace(minute=0, second=0, microsecond=0),
        duration=timedelta(hours=24),
    )
    player = Player(schedule, state_path=config.state_path)
    return config, scanner, scheduler, schedule, player


def command_scan(scanner, library):
    print("Discovered library items:")
    print(scanner.format_items(library))


def command_channels(config):
    print("Configured channels:")
    print(Player.summarize_channels(config.channels))


def command_guide(scheduler, schedule, hours: float):
    window_start = datetime.now()
    window_end = window_start + timedelta(hours=hours)
    by_channel = scheduler.guide(schedule, window_start, window_end)
    for channel, entries in sorted(by_channel.items()):
        print(f"=== {channel} ===")
        for entry in entries:
            print(f"{entry.start:%H:%M} - {entry.end:%H:%M}: {entry.label()}")
        print()


def command_now(player):
    now = datetime.now()
    print(player.describe_now_playing(now))
    player.remember_positions(now)


def command_upcoming(player, hours: float):
    now = datetime.now()
    print(player.describe_upcoming(now, horizon=timedelta(hours=hours)))


def command_init_config(output: Path):
    example = Config(
        media_roots=[Path("./sample_media")],
        channels=[
            Config._parse_channel({"name": "Comedy", "include_genres": ["comedy"], "allow_repeats": True}),
            Config._parse_channel({"name": "Drama", "include_genres": ["drama"]}),
            Config._parse_channel({"name": "Cartoons", "include_genres": ["animation", "family"], "shuffle": False}),
            Config._parse_channel(
                {"name": "Movies", "include_genres": ["movie", "comedy"], "allow_repeats": True}
            ),
        ],
    )
    example.save(output)
    print(f"Wrote starter config to {output}")


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-config":
        command_init_config(args.output)
        return

    config, scanner, scheduler, schedule, player = load_app(args.config)
    library = scanner.scan()

    if args.command == "scan":
        command_scan(scanner, library)
    elif args.command == "channels":
        command_channels(config)
    elif args.command == "guide":
        command_guide(scheduler, schedule, hours=args.hours)
    elif args.command == "now":
        command_now(player)
    elif args.command == "upcoming":
        command_upcoming(player, hours=args.hours)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
