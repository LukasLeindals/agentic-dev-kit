"""Path resolution for component destinations."""

from __future__ import annotations

import shutil
from pathlib import Path

from adk.models import ComponentRef, Target

TARGET_DIRS: dict[Target, str] = {
    Target.CLAUDE: ".claude",
    Target.CODEX: ".codex",
}


def local_path(target: Target, ref: ComponentRef) -> Path:
    """Resolve the local path for a component.

    Directory types (tools, skills):  .claude/tools/file_search/
    File types (agents, commands):    .claude/agents/code_reviewer.md
    """
    base = Path(TARGET_DIRS[target])
    if ref.type.is_directory:
        return base / ref.type.plural / ref.name
    return base / ref.type.plural / f"{ref.name}.md"


def remove_local(dest: Path) -> None:
    """Delete a local component — handles both directories and single files."""
    if dest.is_dir():
        shutil.rmtree(dest)
    else:
        dest.unlink()
