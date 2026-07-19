from __future__ import annotations

from pathlib import Path

from bw_backup import __main__


def test_main_forwards_command_line_options(monkeypatch) -> None:
    calls: list[tuple[Path | None, str | None, Path | None]] = []
    monkeypatch.setattr(__main__, "setup_logging", lambda **_kwargs: None)

    def fake_create_export(
        output_dir: Path | None,
        email: str | None,
        clipath: Path | None,
    ) -> Path:
        calls.append((output_dir, email, clipath))
        return Path("created-backup")

    monkeypatch.setattr(__main__, "create_export", fake_create_export)

    result = __main__.main(["backups", "--email", "person@example.com", "--cli", "tools/bw"])

    assert result == 0
    assert calls == [(Path("backups"), "person@example.com", Path("tools/bw"))]
