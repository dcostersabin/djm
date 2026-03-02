"""
Generate Diesel CLI migrations from Django migrations for the djm app.

Usage:
  python manage.py diesel [--output-dir DIR]

Output: migrations/<name>/up.sql and migrations/<name>/down.sql (Diesel format).
"""
from pathlib import Path

from ._migration_sql import BaseGenerateSQLCommand


class Command(BaseGenerateSQLCommand):
    help = "Generate Diesel CLI migrations (subdir per migration with up.sql/down.sql) from Django migrations (djm app)."
    default_output_dir = Path("migrations")
    marker_file = ".diesel"
    other_marker_files = [".goose", ".sqlx"]
    migration_type_label = "Diesel"
    other_migration_type_labels = ["goose", "SQLx"]

    def get_output_files(self, migration_name, up_sql, down_sql, ext):
        """Emit <name>/up.sql and <name>/down.sql per Diesel CLI format."""
        return [
            (f"{migration_name}/up.sql", up_sql.strip() + "\n" if up_sql.strip() else ""),
            (f"{migration_name}/down.sql", down_sql.strip() + "\n" if down_sql.strip() else ""),
        ]

    def format_content(self, up_sql: str, down_sql: str) -> str:
        """Unused; get_output_files writes up/down to separate files."""
        return ""
