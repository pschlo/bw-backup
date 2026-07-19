# bw-backup

`bw-backup` creates a local JSON backup of a Bitwarden vault and downloads its
attachments into the same backup directory.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- The [Bitwarden CLI](https://bitwarden.com/help/cli/) installed as `bw`

uv manages the Python environment and dependencies. The Bitwarden CLI is a
separate application that must also be installed on the system.

## Run

Install the requirements above and run:

```console
uvx https://github.com/pschlo/bw-backup/archive/refs/heads/main.zip
```

uv downloads the application and Python dependencies automatically. The
application then asks for the information needed to unlock the vault. Pass an
output directory as an argument to choose where backups are created, or pass
`--help` to see all options.

This command follows the latest code on the `main` branch.

Each run creates a timestamped directory containing:

```text
bw-backup_user@example.com_2026-07-19_16-30-00/
├── export.json
└── attachments/
    └── item-id/
        └── attachment.pdf
```

## Security

The generated files are unencrypted and may contain passwords, notes, and
attachments. Store the backup on encrypted storage or encrypt it immediately,
and securely remove plaintext copies you no longer need.

## Development

```console
uv sync --locked
uv run bw-backup
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
```

Run `uv lock --refresh-package pywarden` when you want to update the locked
Pywarden revision from its rolling `main` branch.

The tests use fake vault data and do not invoke `bw`, contact Bitwarden, or
access a real vault.
