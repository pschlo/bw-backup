from __future__ import annotations

import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

from pywarden import Attachment, BaseBwControl, CliConfig, Item, UnlockedBwControl

log = logging.getLogger(__name__)

INDENT = 2
INVALID_FILENAME_CHARACTERS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def guess_clipath() -> Path:
    executable = shutil.which("bw")
    if executable is None:
        executable = shutil.which("bw", path=str(Path.cwd()))
    if executable is not None:
        return Path(executable)

    raise ValueError("Could not find the Bitwarden CLI. Provide its path with '--cli'.")


def create_export(
    outdir_parent: Path | None = None,
    email: str | None = None,
    clipath: Path | None = None,
) -> Path:
    cli_path = clipath.expanduser().resolve() if clipath is not None else guess_clipath()
    cli_config = CliConfig(cli_path)

    with BaseBwControl(cli_config).login_unlock_interactive(email) as control:
        account_email = control.status()["userEmail"]
        parent = (outdir_parent or Path.cwd()).expanduser().resolve()
        parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        directory_name = f"bw-backup_{_safe_path_component(account_email, 'account')}_{timestamp}"
        output_dir = _create_unique_directory(parent, directory_name)

        try:
            log.info('Starting export to "%s"', output_dir)
            _export(control, output_dir)
        except BaseException:
            log.error("Export failed; deleting the incomplete backup")
            shutil.rmtree(output_dir, ignore_errors=True)
            raise

    return output_dir


def _create_unique_directory(parent: Path, name: str) -> Path:
    candidate = parent / name
    suffix = 1

    while True:
        try:
            candidate.mkdir(mode=0o700)
            return candidate
        except FileExistsError:
            suffix += 1
            candidate = parent / f"{name} ({suffix})"


def _safe_path_component(value: str, fallback: str) -> str:
    name = INVALID_FILENAME_CHARACTERS.sub("_", value).strip(" .")
    if not name:
        return fallback

    stem = name.split(".", 1)[0].upper()
    if stem in WINDOWS_RESERVED_NAMES:
        name = f"_{name}"
    return name


def _export(control: UnlockedBwControl, output_dir: Path) -> None:
    _save_json(control, output_dir)
    items = _get_items_with_attachments(control)
    if not items:
        return

    attachments_dir = output_dir / "attachments"
    attachments_dir.mkdir(mode=0o700)
    for item in items:
        _save_attachments(control, attachments_dir, item)


def _save_json(control: UnlockedBwControl, output_dir: Path) -> None:
    log.info("Creating JSON export")
    export = control.get_export()
    destination = output_dir / "export.json"
    destination.write_text(export, encoding="utf-8")
    destination.chmod(0o600)


def _get_items_with_attachments(control: UnlockedBwControl) -> list[Item]:
    log.info("Fetching items")
    items = control.get_items()
    items_with_attachments = [item for item in items if item["attachments"]]
    log.info("Found %s items with attachments", len(items_with_attachments))
    return items_with_attachments


def _save_attachments(
    control: UnlockedBwControl,
    attachments_dir: Path,
    item: Item,
) -> None:
    item_name = item["name"]
    item_id = item["id"]
    log.info('%sGetting attachments of item %s ("%s")', " " * INDENT, item_id, item_name)

    item_dir = attachments_dir / _safe_path_component(item_id, "item")
    item_dir.mkdir(mode=0o700)

    for attachment in item["attachments"]:
        _save_attachment(control, item_dir, item, attachment)


def _save_attachment(
    control: UnlockedBwControl,
    item_dir: Path,
    item: Item,
    attachment: Attachment,
) -> None:
    base_name = _safe_path_component(attachment["fileName"], "attachment")
    destination = item_dir / base_name
    suffix = 1
    while destination.exists():
        suffix += 1
        path = Path(base_name)
        destination = item_dir / f"{path.stem} ({suffix}){path.suffix}"

    log.info('%sFetching attachment "%s"', " " * (2 * INDENT), destination.name)
    content = control.get_attachment(item["id"], attachment["id"])
    destination.write_bytes(content)
    destination.chmod(0o600)
