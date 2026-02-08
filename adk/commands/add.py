"""adk add — download a component from the registry."""

from __future__ import annotations

from adk.errors import ADKError
from adk.github import download_zip, extract_component
from adk.models import ComponentRef, Config
from adk.resolve import local_path


def run(ref: ComponentRef, config: Config) -> None:
    dest = local_path(config.target, ref)
    if dest.exists():
        raise ADKError(
            f"{dest} already exists. Use 'adk update {ref}' to re-download."
        )
    zf = download_zip(config.repo, config.branch)
    extract_component(zf, ref, dest)
    print(f"Added {ref} -> {dest}")
