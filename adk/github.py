"""GitHub ZIP download and component extraction."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from adk.errors import ADKError
from adk.models import ComponentRef


def download_zip(repo: str, branch: str) -> zipfile.ZipFile:
    """Download the repo ZIP archive and return a ZipFile object."""
    url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
    try:
        response = urlopen(url)  # noqa: S310
        data = response.read()
    except URLError as exc:
        raise ADKError(f"Failed to download from {url}\n{exc}") from exc
    return zipfile.ZipFile(io.BytesIO(data))


def extract_component(
    zf: zipfile.ZipFile, ref: ComponentRef, dest: Path
) -> None:
    """Extract a component from the ZIP to a local destination.

    Dispatches to directory or file extraction based on the component type.
    """
    if ref.type.is_directory:
        _extract_directory(zf, ref.source_path, dest)
    else:
        _extract_file(zf, ref.source_path, dest)


def _extract_directory(
    zf: zipfile.ZipFile, source_dir: str, dest: Path
) -> None:
    """Extract a component directory from the ZIP."""
    full_prefix: str | None = None
    needle = source_dir if source_dir.endswith("/") else source_dir + "/"
    for entry in zf.namelist():
        if needle in entry:
            idx = entry.index(needle)
            full_prefix = entry[: idx + len(needle)]
            break

    if full_prefix is None:
        raise ADKError(f"Directory '{source_dir}' not found in repository.")

    dest.mkdir(parents=True, exist_ok=True)
    for entry in zf.namelist():
        if not entry.startswith(full_prefix):
            continue
        relative = entry[len(full_prefix) :]
        if not relative or entry.endswith("/"):
            continue
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(entry) as src, open(target, "wb") as dst:
            dst.write(src.read())


def _extract_file(
    zf: zipfile.ZipFile, source_path: str, dest: Path
) -> None:
    """Extract a single file from the ZIP."""
    match: str | None = None
    for entry in zf.namelist():
        if entry.endswith(source_path) or entry.endswith("/" + source_path):
            match = entry
            break

    if match is None:
        raise ADKError(f"File '{source_path}' not found in repository.")

    dest.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(match) as src, open(dest, "wb") as dst:
        dst.write(src.read())
