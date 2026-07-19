from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from bw_backup import export


class FakeControl:
    def __init__(self, *, fail_export: BaseException | None = None) -> None:
        self.fail_export = fail_export
        self.downloads: list[tuple[str, str]] = []

    def status(self) -> dict[str, str]:
        return {"userEmail": "person:backup@example.com"}

    def get_export(self) -> str:
        if self.fail_export is not None:
            raise self.fail_export
        return '{"encrypted": false}'

    def get_items(self) -> list[dict[str, object]]:
        return [
            {
                "id": "item-id",
                "name": "Test item",
                "attachments": [
                    {"id": "first", "fileName": "../../report.txt"},
                    {"id": "second", "fileName": "..\\..\\report.txt"},
                ],
            },
            {"id": "empty-item", "name": "No attachments", "attachments": []},
        ]

    def get_attachment(self, item_id: str, attachment_id: str) -> bytes:
        self.downloads.append((item_id, attachment_id))
        return attachment_id.encode()


class FakeLogin:
    def __init__(self, control: FakeControl) -> None:
        self.control = control

    def __enter__(self) -> FakeControl:
        return self.control

    def __exit__(self, *_args: object) -> None:
        return None


def install_fake_base_control(
    monkeypatch: pytest.MonkeyPatch,
    control: FakeControl,
) -> list[str | None]:
    login_emails: list[str | None] = []

    class FakeBaseControl:
        def __init__(self, _config: object) -> None:
            pass

        def login_unlock_interactive(self, email: str | None) -> FakeLogin:
            login_emails.append(email)
            return FakeLogin(control)

    monkeypatch.setattr(export, "BaseBwControl", FakeBaseControl)
    return login_emails


def test_create_export_writes_json_and_safe_attachment_names(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    control = FakeControl()
    login_emails = install_fake_base_control(monkeypatch, control)
    cli_path = tmp_path / "bw"
    cli_path.touch()

    output_dir = export.create_export(
        tmp_path / "nested" / "backups",
        email="person@example.com",
        clipath=cli_path,
    )

    assert login_emails == ["person@example.com"]
    assert ":" not in output_dir.name
    assert (output_dir / "export.json").read_text(encoding="utf-8") == '{"encrypted": false}'
    item_dir = output_dir / "attachments" / "item-id"
    assert (item_dir / "_.._report.txt").read_bytes() == b"first"
    assert (item_dir / "_.._report (2).txt").read_bytes() == b"second"
    assert control.downloads == [("item-id", "first"), ("item-id", "second")]


def test_create_export_removes_incomplete_backup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    control = FakeControl(fail_export=RuntimeError("synthetic failure"))
    install_fake_base_control(monkeypatch, control)
    cli_path = tmp_path / "bw"
    cli_path.touch()
    parent = tmp_path / "backups"

    with pytest.raises(RuntimeError, match="synthetic failure"):
        export.create_export(parent, clipath=cli_path)

    assert list(parent.iterdir()) == []


def test_create_export_cleans_up_after_keyboard_interrupt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    control = FakeControl(fail_export=KeyboardInterrupt())
    install_fake_base_control(monkeypatch, control)
    cli_path = tmp_path / "bw"
    cli_path.touch()
    parent = tmp_path / "backups"

    with pytest.raises(KeyboardInterrupt):
        export.create_export(parent, clipath=cli_path)

    assert list(parent.iterdir()) == []


def test_create_unique_directory_avoids_collisions(tmp_path: Path) -> None:
    first = export._create_unique_directory(tmp_path, "backup")
    second = export._create_unique_directory(tmp_path, "backup")

    assert first.name == "backup"
    assert second.name == "backup (2)"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("../../secret.txt", "_.._secret.txt"),
        ("CON", "_CON"),
        ("  ", "fallback"),
    ],
)
def test_safe_path_component(value: str, expected: str) -> None:
    assert export._safe_path_component(value, "fallback") == expected


def test_guess_clipath_uses_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda *_args, **_kwargs: "/tools/bw")

    assert export.guess_clipath() == Path("/tools/bw")


def test_guess_clipath_has_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda *_args, **_kwargs: None)

    with pytest.raises(ValueError, match="--cli"):
        export.guess_clipath()
