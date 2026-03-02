"""Tests for goose, sqlx, and diesel management commands."""
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

# Patcher for collect_sql to avoid SQLite schema editor FK error in tests
COLLECT_SQL_PATCH = "djm.management.commands._migration_sql.collect_sql"


def _fake_collect_sql(loader, app_label, migration_name, backwards):
    if backwards:
        return 'DROP TABLE IF EXISTS "example";'
    return 'CREATE TABLE "example" ("id" char(32) NOT NULL PRIMARY KEY, "name" varchar(100) NOT NULL);'


class GooseCommandTests(TestCase):
    """Test manage.py goose."""

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_goose_generates_sql_files_with_directives(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("goose", output_dir=out)
            sql_files = list(out.glob("*.sql"))
            self.assertGreater(len(sql_files), 0, "Should generate at least one .sql file")
            content = (out / "0001_initial.sql").read_text()
            self.assertIn("-- +goose Up", content)
            self.assertIn("-- +goose Down", content)
            self.assertIn("CREATE TABLE", content.upper())
            self.assertIn("DROP TABLE", content.upper())

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_goose_creates_marker_file(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("goose", output_dir=out)
            self.assertTrue((out / ".goose").exists(), "Should create .goose marker")

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_goose_custom_output_dir(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "custom_goose"
            call_command("goose", output_dir=out)
            self.assertTrue(out.exists())
            self.assertTrue((out / "0001_initial.sql").exists())

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_goose_no_sql_extension(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("goose", output_dir=out, no_sql_extension=True)
            self.assertTrue((out / "0001_initial").exists())
            self.assertFalse((out / "0001_initial.sql").exists())

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_goose_run_twice_succeeds(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("goose", output_dir=out)
            call_command("goose", output_dir=out)
            self.assertTrue((out / "0001_initial.sql").exists())


class SQLxCommandTests(TestCase):
    """Test manage.py sqlx."""

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_sqlx_generates_up_and_down_files(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("sqlx", output_dir=out)
            up_file = out / "0001_initial.up.sql"
            down_file = out / "0001_initial.down.sql"
            self.assertTrue(up_file.exists())
            self.assertTrue(down_file.exists())
            self.assertIn("CREATE TABLE", up_file.read_text().upper())
            self.assertIn("DROP TABLE", down_file.read_text().upper())

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_sqlx_creates_marker_file(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("sqlx", output_dir=out)
            self.assertTrue((out / ".sqlx").exists(), "Should create .sqlx marker")

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_sqlx_no_goose_directives_in_content(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("sqlx", output_dir=out)
            content = (out / "0001_initial.up.sql").read_text()
            self.assertNotIn("+goose", content)
            self.assertNotIn("+sqlx", content)

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_sqlx_no_sql_extension(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("sqlx", output_dir=out, no_sql_extension=True)
            self.assertTrue((out / "0001_initial.up").exists())
            self.assertTrue((out / "0001_initial.down").exists())

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_sqlx_run_twice_succeeds(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("sqlx", output_dir=out)
            call_command("sqlx", output_dir=out)
            self.assertTrue((out / "0001_initial.up.sql").exists())


class DieselCommandTests(TestCase):
    """Test manage.py diesel."""

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_diesel_generates_subdir_with_up_and_down_sql(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("diesel", output_dir=out)
            subdir = out / "0001_initial"
            self.assertTrue(subdir.is_dir())
            self.assertTrue((subdir / "up.sql").exists())
            self.assertTrue((subdir / "down.sql").exists())
            self.assertIn("CREATE TABLE", (subdir / "up.sql").read_text().upper())
            self.assertIn("DROP TABLE", (subdir / "down.sql").read_text().upper())

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_diesel_creates_marker_file(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("diesel", output_dir=out)
            self.assertTrue((out / ".diesel").exists(), "Should create .diesel marker")

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_diesel_run_twice_succeeds(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("diesel", output_dir=out)
            call_command("diesel", output_dir=out)
            self.assertTrue((out / "0001_initial" / "up.sql").exists())


class MixingCheckTests(TestCase):
    """Test that goose and sqlx cannot write to the same directory."""

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_goose_then_sqlx_in_same_dir_raises(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("goose", output_dir=out)
            with self.assertRaises(CommandError) as ctx:
                call_command("sqlx", output_dir=out)
            msg = str(ctx.exception)
            self.assertIn("SQLx", msg)
            self.assertIn("goose", msg)
            self.assertNotIn(".sqlx", msg)
            self.assertNotIn(".goose", msg)

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_sqlx_then_goose_in_same_dir_raises(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("sqlx", output_dir=out)
            with self.assertRaises(CommandError) as ctx:
                call_command("goose", output_dir=out)
            msg = str(ctx.exception)
            self.assertIn("goose", msg)
            self.assertIn("SQLx", msg)
            self.assertNotIn(".sqlx", msg)
            self.assertNotIn(".goose", msg)

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_diesel_then_goose_in_same_dir_raises(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("diesel", output_dir=out)
            with self.assertRaises(CommandError) as ctx:
                call_command("goose", output_dir=out)
            msg = str(ctx.exception)
            self.assertIn("Diesel", msg)
            self.assertIn("goose", msg)

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_goose_then_diesel_in_same_dir_raises(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            call_command("goose", output_dir=out)
            with self.assertRaises(CommandError) as ctx:
                call_command("diesel", output_dir=out)
            msg = str(ctx.exception)
            self.assertIn("goose", msg)
            self.assertIn("Diesel", msg)

    @patch(COLLECT_SQL_PATCH, side_effect=_fake_collect_sql)
    def test_different_dirs_all_three_succeed(self, _mock_collect):
        with tempfile.TemporaryDirectory() as tmp:
            goose_dir = Path(tmp) / "goose_migrations"
            sqlx_dir = Path(tmp) / "sqlx_migrations"
            diesel_dir = Path(tmp) / "diesel_migrations"
            call_command("goose", output_dir=goose_dir)
            call_command("sqlx", output_dir=sqlx_dir)
            call_command("diesel", output_dir=diesel_dir)
            self.assertTrue((goose_dir / "0001_initial.sql").exists())
            self.assertTrue((goose_dir / ".goose").exists())
            self.assertTrue((sqlx_dir / "0001_initial.up.sql").exists())
            self.assertTrue((sqlx_dir / ".sqlx").exists())
            self.assertTrue((diesel_dir / "0001_initial" / "up.sql").exists())
            self.assertTrue((diesel_dir / ".diesel").exists())
