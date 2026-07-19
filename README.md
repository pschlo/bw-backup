# bw-backup

`bw-backup` creates a local JSON backup of a Bitwarden vault and downloads its
attachments into the same backup directory.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- The [Bitwarden CLI](https://bitwarden.com/help/cli/) installed as `bw`

uv manages the Python environment and dependencies. The Bitwarden CLI is a
separate application and must be installed on the system.

## Run

Open a terminal in this repository and run:

```console
uv run bw-backup
```

On the first run, uv creates `.venv` and installs the locked dependencies. The
application then asks for the information needed to unlock the vault.

To save the backup under a specific directory:

```console
uv run bw-backup path/to/backups
```

Use `uv run bw-backup --help` to see all options, including `--email` and
`--cli` for supplying the path to the Bitwarden CLI manually.

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

## Install as a command

To make `bw-backup` available outside the repository:

```console
uv tool install "bw-backup @ git+https://github.com/pschlo/bw-backup.git"
bw-backup
```

The equivalent installation with pip is:

```console
python -m pip install "bw-backup @ git+https://github.com/pschlo/bw-backup.git"
bw-backup
```

## Development

```console
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
```

The tests use fake vault data and do not invoke `bw`, contact Bitwarden, or
access a real vault.
