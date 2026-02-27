# DJM

CLI and helpers to go from **Django models → goose-style SQL migrations** (up/down). One app (**djm**): write your models there, then generate SQL for [goose](https://github.com/pressly/goose) or [golang-migrate](https://github.com/golang-migrate/migrate).

## Quick start (CLI)

1. **Install and create a project:**

   ```bash
   pip install djm
   djm init myapp
   cd myapp
   ```

2. **Write your models** in the `djm` app (edit `djm/models/`), then run migrations:

   ```bash
   uv sync   # or: pip install -e .
   uv run python manage.py makemigrations djm
   uv run python manage.py migrate
   ```

3. **Generate goose SQL** (up/down) into `goose_migrations/`:

   ```bash
   uv run python manage.py generate_goose
   ```

   From a project that has the `djm` CLI installed you can instead run:

   ```bash
   djm goose
   ```

4. Use the generated `.sql` files with goose or golang-migrate.

## Requirements

- Python ≥3.13 (or adjust in `pyproject.toml`)
- Django ≥6.0
- [uv](https://github.com/astral-shared/uv) (recommended) or pip

## CLI

| Command | Description |
|--------|-------------|
| `djm init [path]` | Create a new DJM project (default: current directory). Preconfigured with `djm` app and `generate_goose` command. |
| `djm goose [-o DIR]` | Generate goose SQL migrations (run from project root; uses `manage.py generate_goose`). |

## Project layout (after `djm init`)

| Path | Purpose |
|------|--------|
| **djm/** | The only app: write your models here. Includes the `generate_goose` management command. |
| **base/** | Reusable abstract model mixins: `UUIDPrimaryKeyMixin`, `TimestampsMixin`, `SoftDeleteMixin`, `SortNumberMixin`. |
| **core/** | Main Django project (settings, urls). |

## Commands (inside a project)

- **Generate goose migrations:**
  ```bash
  uv run python manage.py generate_goose [--output-dir DIR] [--no-sql-extension]
  ```
  Uses the `djm` app. Default output dir is `goose_migrations`. Files are named `{migration_name}.sql`.

## Base mixins

Use these in your models (see `djm.models` and `base.models`):

- **UUIDPrimaryKeyMixin** – UUID primary key (via `uuid6`).
- **TimestampsMixin** – `created`, `updated` (auto_now_add / auto_now).
- **SoftDeleteMixin** – `deleted` nullable datetime for soft deletes.
- **SortNumberMixin** – `order_no` and default ordering.

Import from `base.models`; the mixins are abstract and do not require `base` in `INSTALLED_APPS` unless you add migrations in `base`.

## Shipping as a package

The package ships **djm** (models + `generate_goose` command) and **base** (mixins). One app only; users write models in `djm`.

- **Install:** `pip install -e /path/to/djm` or `pip install djm`
- **In the consuming project:** Add `djm` to `INSTALLED_APPS`, write models in `djm`, run `python manage.py generate_goose -o your_goose_dir`.
- **Build:** `make build` or `uv build`

## Publishing to PyPI (GitHub Actions)

The repo includes a workflow that builds and publishes to [PyPI](https://pypi.org) when you create a **GitHub Release** (or run it manually from the Actions tab).

1. **One-time:** Add a [trusted publisher](https://pypi.org/manage/account/publishing/) on PyPI:
   - PyPI project name: `djm`
   - Repository: `OWNER/djm`
   - Workflow name: `publish.yml`

2. **To release:** Create a new release on GitHub (tag, e.g. `v0.1.0`). The workflow will build and publish the package to PyPI. No API token is needed (OIDC).

- `.github/workflows/publish.yml` – build + publish to PyPI on release
- `.github/workflows/ci.yml` – build only on push/PR to `main`

## Makefile

- `make help` – show targets  
- `make migrate` – run Django migrations  
- `make goose` – generate goose SQL into `goose_migrations`  
- `make goose OUT=./sql` – generate into `./sql`  
- `make clean` – remove generated goose files and `__pycache__`  
- `make install` – `uv sync`  
- `make build` – build distribution artifacts  

## Notes

- Django’s `sqlmigrate` supports **`--backwards`** (with an “s”) to print SQL that unapplies a migration; the generator uses this for the “Down” section.
- Generated SQL is for the database configured in `settings.DATABASES["default"]` (e.g. SQLite). For PostgreSQL/MySQL, run the generator with that database configured.
