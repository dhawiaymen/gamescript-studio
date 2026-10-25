# Architecture

`model.py` owns defaults, strict validation, and JSON persistence.
`compiler.py` builds an export in a sibling staging folder, then renames it.
Existing export folders are never replaced. Project saves use atomic file
replacement. `templates/runtime.js` separates deterministic simulation from
Canvas rendering. It also exports a CommonJS engine for Node.js tests.
`gui.py` edits the same schema used by the CLI; it has no separate game logic.

Adding a game mechanic requires schema/range decisions, engine behavior,
visual settings, and behavioral tests. Future work: custom sprite assets,
additional event types, and engine adapters after demand is demonstrated.
These are roadmap items, not implemented features.
