"""adk update — re-download a locally installed component."""

from __future__ import annotations

from adk.errors import ADKError
from adk.github import download_zip, extract_component
from adk.models import ComponentRef, Config
from adk.resolve import local_path, remove_local


def run(ref: ComponentRef, config: Config) -> None:
    dest = local_path(config.target, ref)
    if not dest.exists():
        raise ADKError(
            f"{dest} does not exist. Use 'adk add {ref}' first."
        )
    zf = download_zip(config.repo, config.branch)
    remove_local(dest)
    extract_component(zf, ref, dest)
    print(f"Updated {ref} -> {dest}")
