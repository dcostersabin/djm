from pathlib import Path

from ._migration_sql import BaseGenerateSQLCommand


class Command(BaseGenerateSQLCommand):
    help = "Generate goose-style SQL migration files from Django migrations (djm app)."
    default_output_dir = Path("migrations")
    marker_file = ".goose"
    other_marker_files = [".sqlx", ".diesel"]
    migration_type_label = "goose"
    other_migration_type_labels = ["SQLx", "Diesel"]

    def format_content(self, up_sql: str, down_sql: str) -> str:
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
