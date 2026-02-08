# Agentic Dev Kit (ADK)

A CLI and component library for distributing reusable LLM components (tools, skills, agents, commands) into projects. Components are copied as plain files — no runtime, no framework coupling.

## Commands

- `pip install -e .` — install locally (zero dependencies)
- `adk add tool:file_search` — download a component
- `adk remove tool:file_search` — delete a local component
- `adk update tool:file_search` — re-download latest version
- `adk --target codex add tool:file_search` — target a specific platform

## Architecture

### CLI (`adk/`)

```
adk/
├── cli.py              # Argparse setup + dispatch (thin entry point)
├── models.py           # ComponentType, ComponentRef, Target, Config (frozen dataclasses + enums)
├── errors.py           # ADKError (single exception type, caught in cli.py)
├── resolve.py          # local_path(), remove_local() — path resolution + deletion
├── github.py           # download_zip(), extract_component() — ZIP download + extraction
└── commands/
    ├── add.py          # run(ref, config) — download if not exists
    ├── remove.py       # run(ref, config) — delete if exists
    └── update.py       # run(ref, config) — re-download if exists
```

Key patterns:
- Each command module exposes a single `run(ref: ComponentRef, config: Config)` function
- All errors are `ADKError` exceptions, caught once in `cli.py:main()`
- `ComponentRef.source_path` computes the repo path (type-aware, see below)
- `resolve.local_path()` computes the destination (type-aware, see below)
- Target mapping is in `resolve.TARGET_DIRS` (claude -> `.claude/`, codex -> `.codex/`)
- Refs support subfolders: `tool:search/semantic` → `components/tools/search/semantic/`
- `ComponentRef.parse()` validates names (rejects empty, leading `/`, and `..` segments)

### Directory vs file components

Component types are either **directory-based** or **file-based** (`ComponentType.is_directory`):

| Type    | Storage   | Source in repo                          | Destination (claude)              |
|---------|-----------|-----------------------------------------|-----------------------------------|
| tool    | directory | `components/tools/file_search/`         | `.claude/tools/file_search/`      |
| skill   | directory | `components/skills/skill-creator/`      | `.claude/skills/skill-creator/`   |
| agent   | file      | `components/agents/code_reviewer.md`    | `.claude/agents/code_reviewer.md` |
| command | file      | `components/commands/learn.md`          | `.claude/commands/learn.md`       |
| rule    | file      | `components/rules/no-console-log.md`    | `.claude/rules/no-console-log.md` |

This distinction flows through the entire codebase:
- `ComponentRef.source_path` — appends `.md` for file types
- `resolve.local_path()` — returns file path (with `.md`) for file types, directory for directory types
- `github.extract_component()` — dispatches to `_extract_directory()` or `_extract_file()`
- `resolve.remove_local()` — uses `shutil.rmtree()` for dirs, `unlink()` for files

### Components (`components/`)

**Tools** (`components/tools/{name}/`) — Directory — Callable functions for LLM tool use
- `metadata.yaml` — name, type, description, version, inputs, outputs, dependencies
- `{name}.py` — Python implementation with a single entry-point function

**Skills** (`components/skills/{name}/`) — Directory — Claude Code skills (SKILL.md-based)
- `SKILL.md` (required) — YAML frontmatter (`name`, `description`) + markdown instructions
- `scripts/` (optional) — Executable helper scripts (Python/Bash)
- `references/` (optional) — Reference docs loaded into context as needed
- `assets/` (optional) — Files used in output (templates, images, etc.)

**Agents** (`components/agents/{name}.md`) — Single file — Claude Code subagent definitions
- Markdown with YAML frontmatter: `name`, `description`, `tools`, `model`
- Body is the system prompt

**Commands** (`components/commands/{name}.md`) — Single file — Claude Code slash commands
- Markdown with optional YAML frontmatter
- Body is the prompt/instructions, supports `$ARGUMENTS` substitution

**Rules** (`components/rules/{name}.md`) — Single file — Claude Code auto-loaded rules
- Markdown with optional YAML frontmatter (supports `paths` for path-scoped rules)
- Body is the constraint/behavior that applies to every session

## Code Style

- Python 3.10+, use `from __future__ import annotations`
- Frozen dataclasses and enums for models — no mutable state objects
- Type all function signatures; avoid `Any` and `argparse.Namespace` leaking into business logic
- Errors as exceptions (`ADKError`), not `sys.exit()` scattered in functions
- Keep command modules focused: one `run()` function, delegate to `resolve` and `github`

## Do Not

- Add runtime dependencies — CLI must stay zero-dep (stdlib only)
- Put `sys.exit()` in command modules — raise `ADKError` instead
- Use a registry file — component paths are convention-based
- Duplicate shared logic — path resolution goes in `resolve.py`, download logic in `github.py`
- Store agents, commands, or rules as directories — they must be single `.md` files for Claude Code
