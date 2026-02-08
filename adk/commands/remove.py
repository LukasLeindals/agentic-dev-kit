"""adk remove — delete a locally installed component."""

from __future__ import annotations

from adk.errors import ADKError
from adk.models import ComponentRef, Config
from adk.resolve import local_path, remove_local


def run(ref: ComponentRef, config: Config) -> None:
    dest = local_path(config.target, ref)
    if not dest.exists():
        raise ADKError(f"{dest} does not exist. Nothing to remove.")
    remove_local(dest)
    print(f"Removed {ref} from {dest}")
