# Getting Started with ADK

## Installation

Install ADK from PyPI:

```bash
pip install agentic-dev-kit
```

This gives you the `adk` command.

## Adding Your First Component

Add a skill to your project:

```bash
adk add skill:skill-creator
```

This downloads the `skill-creator` skill into `.claude/skills/skill-creator/` (the default target is `claude`).

Components can be nested in subfolders — the name part of the ref supports slashes:

```bash
adk add tool:search/semantic
# Places into .claude/tools/search/semantic/
```

To use a different target:

```bash
adk --target codex add skill:skill-creator
# Places into .codex/skills/skill-creator/
```

## Updating a Component

Pull the latest version of an installed component:

```bash
adk update skill:skill-creator
```

This re-downloads the component, replacing the local copy.

## Removing a Component

```bash
adk remove skill:skill-creator
```

This deletes the `.claude/skills/skill-creator/` directory.

For single-file components (agents, commands):

```bash
adk remove agent:code_reviewer
# Deletes .claude/agents/code_reviewer.md
```

## Directory Structure

After adding components with the default `claude` target:

```
your-project/
├── .claude/
│   ├── tools/
│   │   └── file_search/          # directory
│   │       ├── metadata.yaml
│   │       └── file_search.py
│   ├── skills/
│   │   └── skill-creator/        # directory
│   │       ├── SKILL.md
│   │       └── scripts/
│   ├── agents/
│   │   └── code_reviewer.md      # single file
│   └── commands/
│       └── learn.md              # single file
└── ...
```

## Creating a Custom Component

### Directory components (tools, skills)

#### Tool

```bash
mkdir -p components/tools/my_tool
```

Add a `metadata.yaml`:

```yaml
name: my_tool
type: tool
description: A brief description of what it does.
version: "0.1"
inputs:
  - name: query
    type: string
    description: What the input is.
outputs:
  - name: result
    type: string
    description: What the output is.
dependencies: []
```

Add a Python implementation alongside it.

#### Skill

```bash
mkdir -p components/skills/my-skill
```

Add a `SKILL.md` with YAML frontmatter:

```markdown
---
name: my-skill
description: What this skill does and when to use it.
---

Instructions for Claude when this skill is activated.
```

### Single-file components (agents, commands)

#### Agent

Create `components/agents/my-agent.md`:

```markdown
---
name: my-agent
description: What this agent specializes in.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a specialized agent for [purpose].

## Instructions
- Step-by-step guidance
```

#### Command

Create `components/commands/my-command.md`:

```markdown
# My Command

Instructions for Claude to follow when this command is invoked.

Use $ARGUMENTS for user-provided input.
```

All components are automatically available by convention at their path — no registry file needed.

## Metadata Schema Reference (tools)

| Field          | Type   | Required | Description                                    |
|----------------|--------|----------|------------------------------------------------|
| `name`         | string | yes      | Component identifier                           |
| `type`         | string | yes      | One of: `tool`, `skill`, `agent`, `command`    |
| `description`  | string | yes      | What the component does                        |
| `version`      | string | yes      | Semantic version (e.g. `"0.1"`)                |
| `inputs`       | list   | yes      | List of input parameters                       |
| `outputs`      | list   | yes      | List of output values                          |
| `dependencies` | list   | no       | Other components this depends on (e.g. `tool:file_search`) |

### Input/Output Fields

| Field         | Type   | Required | Description                  |
|---------------|--------|----------|------------------------------|
| `name`        | string | yes      | Parameter name               |
| `type`        | string | yes      | Data type (string, list, etc)|
| `description` | string | yes      | What this parameter is       |
| `default`     | any    | no       | Default value if not provided|
