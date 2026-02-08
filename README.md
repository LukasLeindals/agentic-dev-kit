# Agentic Dev Kit (ADK)

A lightweight kit of reusable LLM components — tools, skills, agents, and commands — that you can add to any project with a single command. No frameworks, no runtime coupling. Files are simply copied into your repo.

## Install

```bash
pip install agentic-dev-kit
```

## Usage

```bash
# Add a component (default target: claude)
adk add tool:file_search

# Components can be nested in subfolders
adk add tool:search/semantic

# Update to the latest version
adk update tool:file_search

# Remove a component
adk remove tool:file_search
```

Components are placed into a target-specific directory:

```bash
# Claude (default) — places into .claude/
adk add skill:skill-creator

# Codex — places into .codex/
adk --target codex add skill:skill-creator
```

Example directory after adding components:

```
.claude/
├── tools/
│   └── file_search/            # directory (tool)
├── skills/
│   └── skill-creator/          # directory (skill)
│       └── SKILL.md
├── agents/
│   └── code_reviewer.md        # single file (agent)
├── commands/
│   └── learn.md                # single file (command)
└── rules/
    └── no-console-log.md       # single file (rule)
```

### Options

| Flag       | Default                          | Description                |
|------------|----------------------------------|----------------------------|
| `--target` | `claude`                         | Target platform (`claude`, `codex`) |
| `--repo`   | `LukasLeindals/agentic-dev-kit`  | Source GitHub repository    |
| `--branch` | `main`                           | Branch to pull from         |

## Component Types

| Type      | Storage   | Description                              | Example                |
|-----------|-----------|------------------------------------------|------------------------|
| `tool`    | directory | A callable function for LLM tool use     | `tool:file_search`     |
| `skill`   | directory | A skill with SKILL.md + optional resources | `skill:skill-creator`|
| `agent`   | file      | A subagent definition (`.md` with frontmatter) | `agent:code_reviewer` |
| `command` | file      | A slash command (`.md`)                  | `command:learn`        |
| `rule`    | file      | An auto-loaded rule (`.md`)              | `rule:no-console-log`  |

The name part of a ref can include subfolders: `tool:search/semantic` maps to `components/tools/search/semantic/` in the source repo.

## Creating Your Own Components

### Skills (directory)

```
components/skills/my-skill/
├── SKILL.md          # Required — YAML frontmatter + instructions
├── scripts/          # Optional — helper scripts
├── references/       # Optional — reference docs
└── assets/           # Optional — templates, images
```

### Tools (directory)

```
components/tools/my-tool/
├── metadata.yaml     # Name, description, inputs, outputs
└── my_tool.py        # Implementation
```

### Agents (single file)

```
components/agents/my-agent.md
```

With YAML frontmatter (`name`, `description`, `tools`, `model`) and system prompt as the body.

### Commands (single file)

```
components/commands/my-command.md
```

Markdown instructions, optionally with YAML frontmatter. Supports `$ARGUMENTS` substitution.

### Rules (single file)

```
components/rules/my-rule.md
```

Markdown constraints/behaviors, optionally with YAML frontmatter. Supports `paths` for path-scoped rules.

## Repository Structure

```
agentic-dev-kit/
├── adk/              # CLI package
├── components/
│   ├── tools/        # Tool components (directories)
│   ├── skills/       # Skill components (directories)
│   ├── agents/       # Agent components (single .md files)
│   ├── commands/     # Command components (single .md files)
│   └── rules/        # Rule components (single .md files)
└── docs/             # Documentation
```

## License

MIT
