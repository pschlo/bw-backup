from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from .export import create_export
from .setup_logging import setup_logging

log = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bw-backup",
        description="Back up a Bitwarden vault, including attachments.",
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        nargs="?",
        help="directory in which to create the timestamped backup",
    )
    parser.add_argument("--email", help="Bitwarden account email address")
    parser.add_argument("--cli", type=Path, help="path to the Bitwarden CLI executable")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = get_parser().parse_args(argv)
    setup_logging(include_packages={"pywarden"})
    output_dir = create_export(args.output_dir, email=args.email, clipath=args.cli)
    log.info('Backup complete: "%s"', output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
