"""ADK CLI — entry point and argument parsing."""

from __future__ import annotations

import argparse
import sys

from adk.commands import add, remove, update
from adk.errors import ADKError
from adk.models import ComponentRef, Config, Target


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adk",
        description="Agentic Dev Kit — manage reusable LLM components.",
    )
    parser.add_argument(
        "--repo",
        default="LukasLeindals/agentic-dev-kit",
        help="GitHub repo (default: LukasLeindals/agentic-dev-kit)",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch to pull from (default: main)",
    )
    parser.add_argument(
        "--target",
        default="claude",
        choices=[t.value for t in Target],
        help="Target platform (default: claude)",
    )

    sub = parser.add_subparsers(dest="command")
    for name, help_text in [
        ("add", "Add a component"),
        ("remove", "Remove a component"),
        ("update", "Update a component"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("ref", help="Component ref, e.g. tool:file_search")

    return parser


DISPATCH = {
    "add": add.run,
    "remove": remove.run,
    "update": update.run,
}


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        ref = ComponentRef.parse(args.ref)
        config = Config(
            repo=args.repo,
            branch=args.branch,
            target=Target(args.target),
        )
        DISPATCH[args.command](ref, config)
    except ADKError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
