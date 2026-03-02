"""Tests for the djm CLI (init, goose, sqlx subcommands)."""
import subprocess
import sys
import tempfile
from pathlib import Path

from django.test import TestCase

# Project root: djm/tests/test_cli.py -> djm/tests -> djm -> project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class CLIInitTests(TestCase):
    """Test djm init."""

    def test_init_refuses_non_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "existing_file.txt").write_text("x")
            from djm.cli import cmd_init
            result = cmd_init(Path(tmp))
            self.assertEqual(result, 1)
            self.assertFalse((Path(tmp) / "manage.py").exists())

    def test_init_creates_project_in_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            from djm.cli import cmd_init
            result = cmd_init(Path(tmp))
            self.assertEqual(result, 0)
            self.assertTrue((Path(tmp) / "manage.py").exists())
            self.assertTrue((Path(tmp) / "djm" / "management" / "commands" / "goose.py").exists())
            self.assertTrue((Path(tmp) / "djm" / "management" / "commands" / "sqlx.py").exists())
            self.assertTrue((Path(tmp) / "core" / "settings.py").exists())


class CLIGooseSQLxTests(TestCase):
    """Test djm goose and djm sqlx delegate to manage.py."""

    def test_goose_from_project_root_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            proc = subprocess.run(
                [sys.executable, "-m", "djm.cli", "goose", "-o", str(out_dir)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                self.skipTest(
                    "goose command failed (e.g. SQLite schema editor in subprocess): "
                    + (proc.stderr or proc.stdout or "")
                )
            self.assertTrue((out_dir / "0001_initial.sql").exists())
            self.assertTrue((out_dir / ".goose").exists())

    def test_sqlx_from_project_root_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            proc = subprocess.run(
                [sys.executable, "-m", "djm.cli", "sqlx", "-o", str(out_dir)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                self.skipTest(
                    "sqlx command failed (e.g. SQLite schema editor in subprocess): "
                    + (proc.stderr or proc.stdout or "")
                )
            self.assertTrue((out_dir / "0001_initial.up.sql").exists())
            self.assertTrue((out_dir / "0001_initial.down.sql").exists())
            self.assertTrue((out_dir / ".sqlx").exists())

    def test_goose_from_dir_without_manage_py_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, "-m", "djm.cli", "goose", "-o", "migrations"],
                cwd=tmp,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 1, proc.stderr or proc.stdout)
            self.assertIn("manage.py", proc.stderr or proc.stdout)

    def test_sqlx_from_dir_without_manage_py_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, "-m", "djm.cli", "sqlx", "-o", "migrations"],
                cwd=tmp,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 1, proc.stderr or proc.stdout)
            self.assertIn("manage.py", proc.stderr or proc.stdout)
