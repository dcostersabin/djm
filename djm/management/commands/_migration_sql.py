"""
Shared logic for generating SQL from Django migrations (djm app).
Used by goose and sqlx commands (Template Method pattern).
"""
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.migrations.loader import AmbiguityError, MigrationLoader

APP_LABEL = "djm"


def get_sorted_migration_names(loader: MigrationLoader, app_label: str) -> list[str]:
    """Return sorted migration names for the app (numeric prefix then name)."""
    names = [
        name for (a, name) in loader.disk_migrations.keys() if a == app_label
    ]
    if not names:
        return []

    def sort_key(n: str):
        parts = n.split("_", 1)
        return (int(parts[0]) if parts[0].isdigit() else 0, n)

    names.sort(key=sort_key)
    return names


def collect_sql(
    loader: MigrationLoader,
    app_label: str,
    migration_name: str,
    backwards: bool,
) -> str:
    """Collect SQL for one migration (forward or backward). Raises CommandError on ambiguity."""
    try:
        migration = loader.get_migration_by_prefix(app_label, migration_name)
    except (AmbiguityError, KeyError) as e:
        raise CommandError(str(e)) from e
    target = (app_label, migration.name)
    plan = [(loader.graph.nodes[target], backwards)]
    statements = loader.collect_sql(plan)
    return "\n".join(statements) if statements else ""


class BaseGenerateSQLCommand(BaseCommand):
    """
    Base command for exporting Django migrations to SQL files.
    Subclasses set default_output_dir, optional marker_file/other_marker_files,
    and implement format_content(up_sql, down_sql).
    """

    default_output_dir: Path = Path("migrations")
    marker_file: str = ""  # e.g. ".goose" or ".sqlx"; prevents mixing migration types
    other_marker_files: list[str] = []  # e.g. [".sqlx"] for goose
    migration_type_label: str = ""  # user-facing name for this command, e.g. "goose" or "SQLx"
    other_migration_type_labels: list[str] = []  # user-facing names for other types, same order as other_marker_files
    help = "Generate SQL migration files from Django migrations (djm app)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            "-o",
            type=Path,
            default=self.default_output_dir,
            help=f"Output directory for .sql files (default: {self.default_output_dir}).",
        )
        parser.add_argument(
            "--no-sql-extension",
            action="store_true",
            help="Write files without .sql extension (e.g. 0001_initial).",
        )

    def get_output_files(
        self, migration_name: str, up_sql: str, down_sql: str, ext: str
    ) -> list[tuple[str, str]]:
        """
        Return list of (filename, content) to write per migration.
        Default: one file using format_content(up_sql, down_sql).
        Override to emit multiple files (e.g. .up.sql and .down.sql for sqlx-cli).
        """
        content = self.format_content(up_sql, down_sql)
        return [(f"{migration_name}{ext}", content)]

    def format_content(self, up_sql: str, down_sql: str) -> str:
        """Produce file content from up and down SQL. Subclasses must override."""
        raise NotImplementedError

    def handle(self, output_dir, no_sql_extension, **options):
        try:
            apps.get_app_config(APP_LABEL)
        except LookupError as e:
            raise CommandError(str(e)) from e

        connection = connections["default"]
        loader = MigrationLoader(connection, replace_migrations=False)
        if APP_LABEL not in loader.migrated_apps:
            raise CommandError(f"App '{APP_LABEL}' does not have migrations.")

        migration_names = get_sorted_migration_names(loader, APP_LABEL)
        if not migration_names:
            raise CommandError(f"No migrations found for app '{APP_LABEL}'.")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if self.marker_file:
            for i, other in enumerate(self.other_marker_files):
                if (output_dir / other).exists():
                    other_label = (
                        self.other_migration_type_labels[i]
                        if i < len(self.other_migration_type_labels)
                        else "another migration tool"
                    )
                    raise CommandError(
                        f"This directory already contains {other_label} migrations. "
                        f"Use a different --output-dir for {self.migration_type_label} migrations."
                    )

        ext = "" if no_sql_extension else ".sql"
        total_files = 0

        for name in migration_names:
            up_sql = collect_sql(loader, APP_LABEL, name, backwards=False)
            down_sql = collect_sql(loader, APP_LABEL, name, backwards=True)
            for filename, content in self.get_output_files(name, up_sql, down_sql, ext):
                path = output_dir / filename
                path.write_text(content, encoding="utf-8")
                self.stdout.write(f"Wrote {path}")
                total_files += 1

        if self.marker_file:
            (output_dir / self.marker_file).write_text("", encoding="utf-8")
            if self.migration_type_label:
                self.stdout.write(f"Marked directory for {self.migration_type_label} migrations.")

        self.stdout.write(
            self.style.SUCCESS(f"Done. {total_files} file(s) in {output_dir}")
        )
