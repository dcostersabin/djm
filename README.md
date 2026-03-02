# DJM

Generate SQL migrations from Django models for [goose](https://github.com/pressly/goose), [golang-migrate](https://github.com/golang-migrate/migrate), or [SQLx](https://github.com/launchbadge/sqlx) (Rust). One app: define models in **djm**, run Django migrations, then export to SQL.

## Why

I build a lot of POCs in Django. When one works and needs to turn into something with real business impact, I usually rewrite in Go or Rust. I only want to rewrite the business logic—not waste time turning existing tables into SQL migrations by hand. DJM exports the schema from Django so I can drop it into a Go (goose) or Rust (SQLx) project and focus on the code that matters.

## Requirements

- Python ≥3.13
- Django ≥6.0

## Quick start

```bash
pip install djm
djm init myapp
cd myapp
```

Edit models in `djm/models/`, then:

```bash
pip install -e .   # or: uv sync
python manage.py makemigrations djm
python manage.py migrate
python manage.py goose   # or: python manage.py sqlx
```

Use the generated SQL with your migration tool (goose, golang-migrate, or SQLx).

## CLI

| Command | Description |
|--------|-------------|
| `djm init [path]` | Create a new project (default: current directory). |
| `djm goose [-o DIR]` | Generate goose-style SQL (default: `migrations`). |
| `djm sqlx [-o DIR]` | Generate SQLx-style SQL (default: `migrations`). |

Run `djm goose` and `djm sqlx` from the project root (where `manage.py` is).

## Project layout (after `djm init`)

| Path | Purpose |
|------|--------|
| **djm/** | App for your models; includes `goose` and `sqlx` management commands. |
| **base/** | Abstract mixins: `UUIDPrimaryKeyMixin`, `TimestampsMixin`, `SoftDeleteMixin`, `SortNumberMixin`. |
| **core/** | Django project (settings, urls). |

## Generating SQL

**Goose** (one file per migration, up/down in one file):

```bash
python manage.py goose [--output-dir DIR] [--no-sql-extension]
```

**SQLx** ([sqlx-cli](https://github.com/launchbadge/sqlx/tree/main/sqlx-cli) reversible format: `.up.sql` and `.down.sql` per migration):

```bash
python manage.py sqlx [--output-dir DIR] [--no-sql-extension]
```

Both commands write into the same default dir (`migrations`). Each marks the directory so the other won’t overwrite it. To use both, use different dirs (e.g. `goose -o goose_migrations`, sqlx keeps `migrations`).

## Base mixins

Import from `base.models`:

- **UUIDPrimaryKeyMixin** – UUID primary key (`uuid6`).
- **TimestampsMixin** – `created`, `updated`.
- **SoftDeleteMixin** – `deleted` (nullable datetime).
- **SortNumberMixin** – `order_no` and default ordering.

Mixins are abstract; you don’t need `base` in `INSTALLED_APPS` unless you add migrations there.

## Makefile

From project root:

- `make help` – list targets
- `make install` – install dependencies (`uv sync`)
- `make migrate` – apply Django migrations
- `make goose` – generate goose SQL (default: `migrations`)
- `make sqlx` – generate SQLx SQL (default: `migrations`)
- `make test` – run tests
- `make clean` – remove generated SQL and `__pycache__`
- `make build` – build wheel/sdist

Use `make goose OUT=dir` or `make sqlx OUT=dir` to override the output directory.

## Development

From the repo:

```bash
pip install -e .
python manage.py test djm
```

## Notes

- SQL is generated for the database in `settings.DATABASES["default"]`. Use PostgreSQL/MySQL in settings if you need that dialect.
- Down migrations use Django’s `sqlmigrate --backwards` under the hood.

## Credits

This project was largely built with AI. I wrote only the initial rough version that generated SQL; the rest—SQLx support, refactors, tests, CLI, and docs—came from iterating with AI.
