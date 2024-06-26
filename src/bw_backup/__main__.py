from pathlib import Path
from typing import Protocol, cast
import argparse
import logging

from .setup_logging import setup_logging
from .export import create_export


setup_logging(include_packages={'pywarden'})
log = logging.getLogger(__name__)


class Args(Protocol):
    output_dir: Path | None
    email: str | None
    cli: Path | None


def get_args() -> Args:
    parser = argparse.ArgumentParser('bw-backup')
    parser.add_argument('output_dir', type=Path, nargs='?')
    parser.add_argument('--email', type=str)
    parser.add_argument('--cli', type=Path)
    return cast(Args, parser.parse_args())

args = get_args()
create_export(args.output_dir, email=args.email, clipath=args.cli)
