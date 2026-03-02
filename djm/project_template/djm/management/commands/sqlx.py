"""
Generate sqlx-cli reversible migrations from Django migrations for the djm app.

Usage:
  python manage.py sqlx [--output-dir DIR] [--no-sql-extension]

Output: <name>.up.sql and <name>.down.sql per migration (sqlx migrate add -r format).
"""
from pathlib import Path

from ._migration_sql import BaseGenerateSQLCommand


class Command(BaseGenerateSQLCommand):
    help = "Generate sqlx-cli reversible migrations (.up.sql and .down.sql) from Django migrations (djm app)."
    default_output_dir = Path("migrations")
    marker_file = ".sqlx"
    other_marker_files = [".goose"]
    migration_type_label = "SQLx"
    other_migration_type_labels = ["goose"]

    def get_output_files(self, migration_name, up_sql, down_sql, ext):
        """Emit separate .up.sql and .down.sql files per sqlx-cli reversible format."""
        return [
            (f"{migration_name}.up{ext}", up_sql.strip() + "\n" if up_sql.strip() else ""),
            (f"{migration_name}.down{ext}", down_sql.strip() + "\n" if down_sql.strip() else ""),
        ]

    def format_content(self, up_sql: str, down_sql: str) -> str:
        """Unused; get_output_files writes up/down to separate files."""
        return ""
