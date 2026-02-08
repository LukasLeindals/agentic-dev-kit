# Session Learning Command

Review this conversation session and propose updates to Claude's configuration based on learnings from our work together.

## What to Analyze

1. **Reusable workflows**: Repeated actions or multi-step tasks that could become commands
2. **Specialized behaviors**: Work requiring a specific persona or expertise that could become an agent
3. **Domain knowledge**: Conventions, structures, or expertise that could become a skill
4. **Conditional behaviors**: Rules that should apply in specific situations (e.g., file types, directories)
5. **Corrections or clarifications**: Mistakes that were corrected or knowledge gaps that were filled
6. **Automation opportunities**: Repetitive validations or checks that could become hooks

## Configuration Components

### CLAUDE.md / AGENTS.md
Project memory and instructions. Propose additions for:
- Project conventions and standards
- Architecture decisions
- Domain-specific terminology
- Workflow guidelines

```markdown
## Section Name
- Proposed content here
```

### Commands (`.claude/commands/*.md`)
Slash commands for reusable workflows. Invoked via `/command-name`.

```markdown
# Command Name

Description of what the command does.

## Instructions
Step-by-step guidance for Claude to follow.

Use $ARGUMENTS for user-provided input.
```

### Agents (`.claude/agents/*.md`)
Custom AI personas with specialized behaviors. Invoked via `@agent-name`.

```markdown
---
model: sonnet
tools:
  - Read
  - Grep
  - Glob
---

# Agent Name

You are a specialized agent for [purpose].

## Expertise
- Domain knowledge area 1
- Domain knowledge area 2

## Behavior
How this agent should approach tasks differently.
```

### Skills (`.claude/skills/[skill-name]/SKILL.md`)
Knowledge modules with domain expertise. Auto-activated by trigger keywords.

```markdown
# Skill Name

## Triggers
Keywords that activate this skill: keyword1, keyword2

## Knowledge
Domain expertise and reference material.
```

### Rules (`.claude/rules/*.md`)
Auto-loaded behavior constraints applied to every session.

```markdown
# Rule Name

## Applies When
Condition that triggers this rule.

## Behavior
What Claude must do when this rule applies.
```

### Hooks (`.claude/hooks/bash/*.sh`)
Event-triggered automation scripts. Exit 0 to continue, exit 2 to block.

```bash
#!/bin/bash
# Hook: [PreToolUse|PostToolUse|SessionStart]
# Purpose: Description

# Script logic here
exit 0
```

## Output Format

### If learnings exist:
Propose specific updates using the formats above. Include:
- Which component to update (new file or existing)
- The exact content to add
- Rationale for the change

### If no learnings:
Output ONLY this single line with no additional explanation, context, or rationale:
```
Could not identify any new learnings from this session.
```

## Guidelines

- Be selective: Only propose changes that genuinely improve future sessions
- Be specific: Vague guidelines are not helpful
- Don't duplicate: Check existing configuration before proposing
- Focus on project-specific knowledge, not general programming advice
- Use the right component:
  - **Commands**: Reusable workflows invoked on demand
  - **Agents**: Specialized personas for specific types of work
  - **Skills**: Domain knowledge activated by context
  - **Rules**: Constraints applied to every session
  - **Hooks**: Automated validation or blocking
  - **CLAUDE.md**: General project context and conventions
