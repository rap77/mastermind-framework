# Design — mastermind-cli

## Architecture / Boundaries
```
mastermind/                          # CLI wrapper script (Bourne shell)
├── __main__.py                     # Entry: python -m mastermind (future)
├── cli.py                          # argparse + subparsers (薄wrapper)
├── commands/                       # Wrappers thin → handlers
│   ├── init.py                     # → init-handler.py
│   ├── new_canonical.py            # → new-canonical-handler.py
│   ├── extract_objectives.py       # → extract-objectives-handler.py
│   ├── discover.py                 # → discover-handler.py
│   ├── execute.py                  # → complete-task-handler.py
│   ├── status.py                   # → task-progress.json (direct read)
│   ├── archive.py                  # → archive-objective-handler.py
│   ├── activate.py                 # → activate-next-objective-handler.py
│   └── validate.py                 # → discover-contract-check.py
│
.mm-flow/                           # Framework (mono-repo)
└── commands/mm/                    # Handlers reales (authoritative)
    ├── init-handler.py
    ├── new-canonical-handler.py
    ├── extract-objectives-handler.py
    ├── discover-handler.py
    ├── complete-task-handler.py
    ├── archive-objective-handler.py
    ├── activate-next-objective-handler.py
    └── discover-contract-check.py

.claude/commands/mm/                # Slash command wrappers (Claude Code)
├── init.md
├── new-canonical.md
├── extract-objectives.md
├── discover.md
├── complete-task.md
├── archive-objective.md
├── activate-next-objective.md
└── discover-contract-check.md
```

## Technical Approach
- **Entry point:** Shell script `mastermind` in repo root that invokes Python handlers via `.venv`
- **Handlers:** Python scripts in `.mm-flow/commands/mm/` that contain the business logic
- **Slash commands:** Markdown files in `.mm-flow/commands/mm/` that describe how to invoke handlers
- **Symlink bridge:** `.claude/commands/mm` symlinks to `.mm-flow/commands/mm` for Claude Code integration
- **No package installation required** — CLI works directly from repo root using `.venv`

## Dependencies
- No explicit upstream dependency declared
- Handlers use standard library + shared `db_client.py` for PostgreSQL

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.
