from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.migrations.loader import MigrationLoader

APP_LABEL = "djm"


class Command(BaseCommand):
    help = "Generate goose-style SQL migration files from Django migrations (djm app)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            "-o",
            type=Path,
            default=Path("goose_migrations"),
            help="Output directory for .sql files (default: goose_migrations).",
        )
        parser.add_argument(
            "--no-sql-extension",
            action="store_true",
            help="Write files without .sql extension (e.g. 0001_initial).",
        )

    def handle(self, output_dir, no_sql_extension, **options):
        try:
            apps.get_app_config(APP_LABEL)
        except LookupError as e:
            raise CommandError(str(e)) from e

        connection = connections["default"]
        loader = MigrationLoader(connection, replace_migrations=False)
        if APP_LABEL not in loader.migrated_apps:
            raise CommandError(f"App '{APP_LABEL}' does not have migrations.")

        migration_names = [
            name for (a, name) in loader.disk_migrations.keys() if a == APP_LABEL
        ]
        if not migration_names:
            raise CommandError(f"No migrations found for app '{APP_LABEL}'.")

        def sort_key(n):
            parts = n.split("_", 1)
            return (int(parts[0]) if parts[0].isdigit() else 0, n)

        migration_names.sort(key=sort_key)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        ext = "" if no_sql_extension else ".sql"

        for name in migration_names:
            up_sql = self._collect_sql(loader, name, backwards=False)
            down_sql = self._collect_sql(loader, name, backwards=True)
            path = output_dir / f"{name}{ext}"
            content = self._format_goose(up_sql, down_sql)
            path.write_text(content, encoding="utf-8")
            self.stdout.write(f"Wrote {path}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. {len(migration_names)} file(s) in {output_dir}")
        )

    def _collect_sql(self, loader, migration_name, backwards):
        from django.db.migrations.loader import AmbiguityError

        try:
            migration = loader.get_migration_by_prefix(APP_LABEL, migration_name)
        except (AmbiguityError, KeyError) as e:
            raise CommandError(str(e)) from e
        target = (APP_LABEL, migration.name)
        plan = [(loader.graph.nodes[target], backwards)]
        statements = loader.collect_sql(plan)
        return "\n".join(statements) if statements else ""

    def _format_goose(self, up_sql, down_sql):
        parts = [
            "-- +goose Up",
            "-- +goose StatementBegin",
            up_sql.strip(),
            "-- +goose StatementEnd",
            "",
            "-- +goose Down",
            "-- +goose StatementBegin",
            down_sql.strip(),
            "-- +goose StatementEnd",
        ]
        return "\n".join(parts).strip() + "\n"
