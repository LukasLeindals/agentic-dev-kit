"""File search tool — find files matching a glob pattern."""

from __future__ import annotations

from pathlib import Path


def search(pattern: str, directory: str = ".") -> list[str]:
    """Return a list of file paths matching *pattern* under *directory*."""
    root = Path(directory)
    return sorted(str(p) for p in root.glob(pattern) if p.is_file())


if __name__ == "__main__":
    import sys

    pat = sys.argv[1] if len(sys.argv) > 1 else "**/*"
    dir_ = sys.argv[2] if len(sys.argv) > 2 else "."
    for match in search(pat, dir_):
        print(match)
