"""Typed models used across ADK."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from adk.errors import ADKError


class ComponentType(str, Enum):
    TOOL = "tool"
    SKILL = "skill"
    AGENT = "agent"
    COMMAND = "command"

    @property
    def plural(self) -> str:
        return f"{self.value}s"

    @property
    def is_directory(self) -> bool:
        """Whether this component type is stored as a directory (vs a single file)."""
        return self in (ComponentType.TOOL, ComponentType.SKILL)


class Target(str, Enum):
    CLAUDE = "claude"
    CODEX = "codex"


@dataclass(frozen=True)
class ComponentRef:
    type: ComponentType
    name: str

    @classmethod
    def parse(cls, ref: str) -> ComponentRef:
        if ":" not in ref:
            raise ADKError(
                f"Invalid ref '{ref}'. Expected format: type:name "
                f"(e.g. tool:file_search)"
            )
        raw_type, name = ref.split(":", 1)
        try:
            comp_type = ComponentType(raw_type)
        except ValueError:
            valid = ", ".join(t.value for t in ComponentType)
            raise ADKError(
                f"Unknown type '{raw_type}'. Valid types: {valid}"
            ) from None
        if not name or name.startswith("/") or ".." in name.split("/"):
            raise ADKError(
                f"Invalid component name '{name}'. "
                f"Name must be non-empty, must not start with '/', "
                f"and must not contain '..' segments."
            )
        return cls(type=comp_type, name=name.strip("/"))

    @property
    def source_path(self) -> str:
        """Repo-relative path for this component.

        Directory types:  components/tools/file_search
        File types:       components/agents/code_reviewer.md
        """
        base = f"components/{self.type.plural}/{self.name}"
        if self.type.is_directory:
            return base
        return f"{base}.md"

    def __str__(self) -> str:
        return f"{self.type.value}:{self.name}"


@dataclass(frozen=True)
class Config:
    repo: str
    branch: str
    target: Target
