# Autodidex

Autodidex is a personal study and productivity toolkit built in Python. It bundles UI tools, trackers, and small utilities to help manage study sessions, habits, notes, flashcards, and mini-games.

This repository contains a PySide6 GUI plus a number of helpers and small tools used by the app.

## Highlights
- Habit tracker and progress heatmap
- Pomodoro timer and session management
- Notes with summarization helpers
- Flashcards and study algorithms
- Small games and widgets (e.g., Space Invader) used for rewards and motivation

## Requirements
The project uses a variety of 3rd-party Python packages. A starting list is included in `requirements.txt`. Review and pin versions before deploying.

Suggested workflow to set up a local environment (Windows / PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

If you already have a working environment and want exact pinned versions, run:

```powershell
pip freeze > requirements.txt
```

## Running
There is not a single packaged entrypoint — run the module that represents the UI or tool you want. Examples:

```powershell
python v_tabs.py        # main tab-based UI
python test_file.py     # playground / dev UI
python lyric_n_summarization_ui.py  # lyrics summarization tool
```

Adjust the command for the module you intend to run. The app expects typical desktop environment capabilities (audio devices for recorder features, etc.).

## Secrets and sensitive data
- The `secrets/` folder is ignored by Git and will not be committed (`.gitignore` includes `/secrets/`).
- I removed tracked secrets from the tip of `main` and then purged `secrets/` from repository history. A backup branch called `backup-before-purge` was created on the remote before the history rewrite.

Important: assume any keys that were in `secrets/` may have been exposed and rotate them (API keys, tokens, etc.). If you collaborate with others, ask them to re-clone or to run a hard reset to sync with the rewritten history.

Recommended collaborator steps after the rewrite:

```powershell
# Simple (recommended):
rm -Recurse -Force <local-clone-folder>
git clone https://github.com/TripleMCodes/Autodidex.git

# Advanced: (if you understand history rewrite consequences):
cd <existing-clone>
git fetch origin
git reset --hard origin/main
```

## License
This project is licensed under the MIT License — see `LICENSE`.

## Contributing
- Create issues for bugs or feature requests.
- Open pull requests for small, focused changes.
- If you need to share secrets for CI or deployment, store them outside the repo and use environment variables or a secrets manager.

## Contact
If you want help with the repo (tests, packaging, CI, or dependency pinning), open an issue or reply here and I can help set it up.
