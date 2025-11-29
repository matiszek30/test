# Pseudo TV Standalone

A Python-based pseudo TV simulator that turns your media library into virtual channels with an EPG-style guide.

## Features
- Scan media folders with filename parsing and optional `*.meta.json` companion files for metadata.
- Configure multiple channels with genre/show filters, shuffle behavior, and repeat controls via YAML.
- Build a 24-hour schedule and query current/upcoming programs.
- Persist last-known playback positions for a live TV feel.
- Ships with sample media filenames you can replace with your own library.

## Quickstart
1. (Optional) Install PyYAML if you plan to use full YAML syntax. The bundled example config is JSON (which is a subset of YAML)
   so the app runs without extra dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a starter config:
   ```bash
   python -m pseudo_tv.app pseudo_tv.example.yaml init-config
   ```

3. Inspect channels and library:
   ```bash
   python -m pseudo_tv.app pseudo_tv.example.yaml channels
   python -m pseudo_tv.app pseudo_tv.example.yaml scan
   ```

4. View the guide or now-playing info:
   ```bash
   python -m pseudo_tv.app pseudo_tv.example.yaml guide --hours 2
   python -m pseudo_tv.app pseudo_tv.example.yaml now
   ```

5. Point `media_roots` in the config to your real library paths. Companion metadata files (e.g., `Episode.mp4.meta.json`) can override title, runtime, genre, season/episode, or year.

## Configuration
The config file accepts JSON or YAML. Out of the box the sample `pseudo_tv.example.yaml` uses JSON formatting to avoid external
dependencies. If you prefer YAML features, install PyYAML and keep using the same file extension.

The config includes:
- `media_roots`: list of folders to scan.
- `channels`: rules with `include_genres`, `include_shows`, optional `exclude_genres`, and `allow_repeats`/`shuffle` flags.
- `state_path`: file used to remember last playback positions.

Use `python -m pseudo_tv.app <config> init-config` to write an example config you can edit.

## Development
The code lives in `pseudo_tv/` with modules for configuration, library scanning, scheduling, and playback. The CLI entry point is `pseudo_tv/app.py`.

## Repository layout
- `pseudo_tv/`: Python package with the app logic and CLI entry point.
- `pseudo_tv.example.yaml`: starter configuration you can copy and edit for your own library.
- `sample_media/`: placeholder media filenames that demonstrate the expected naming/genre parsing (zero-byte stubs—swap with real files).
- `requirements.txt`: optional dependencies (PyYAML if you want YAML syntax).
- `.pseudo_tv_state.json`: generated at runtime to remember playback positions (ignored by git).

If you only see `readme.md` on GitHub, make sure you're on the latest commit or branch that includes the app code (`pseudo_tv/` and related files listed above).

## Publish to your own Git repository
This project currently lives only in this workspace (`/workspace/test`) and has no remote configured. To publish it to your GitHub account:

1. Create an empty repository on GitHub (without adding a README/license).
2. From this folder, set the remote and push all commits:
   ```bash
   git remote add origin https://github.com/<your-account>/<your-repo>.git
   git branch -M main
   git push -u origin main
   ```
3. Refresh the GitHub page; you should now see the full project tree (`pseudo_tv/`, config, sample media, etc.).

## Where is `/workspace/test`?
`/workspace/test` is the path inside this development environment where the project files reside. If you're using a cloud IDE or container, open the integrated terminal or file explorer and navigate to that folder to view or modify the code. On GitHub, you won't see this path until you push the repository using the steps above.
