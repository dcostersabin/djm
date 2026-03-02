"""Tests for _migration_sql helpers: get_sorted_migration_names and collect_sql."""
import unittest
from pathlib import Path

from django.db import connection, connections
from django.db.migrations.loader import MigrationLoader
from django.test import TestCase

from djm.management.commands._migration_sql import (
    APP_LABEL,
    collect_sql,
    get_sorted_migration_names,
)


class GetSortedMigrationNamesTests(TestCase):
    """Test get_sorted_migration_names returns djm migrations in order."""

    def test_returns_sorted_names_for_djm_app(self):
        connection = connections["default"]
        loader = MigrationLoader(connection, replace_migrations=False)
        names = get_sorted_migration_names(loader, APP_LABEL)
        self.assertGreater(len(names), 0, "djm app should have at least one migration")
        self.assertIn("0001_initial", names)
        # Numeric prefix order
        for i in range(len(names) - 1):
            parts_cur = names[i].split("_", 1)
            parts_nxt = names[i + 1].split("_", 1)
            num_cur = int(parts_cur[0]) if parts_cur[0].isdigit() else 0
            num_nxt = int(parts_nxt[0]) if parts_nxt[0].isdigit() else 0
            self.assertLessEqual(num_cur, num_nxt, f"Order: {names[i]} before {names[i+1]}")

    def test_returns_empty_for_unknown_app(self):
        connection = connections["default"]
        loader = MigrationLoader(connection, replace_migrations=False)
        names = get_sorted_migration_names(loader, "nonexistent_app")
        self.assertEqual(names, [])


@unittest.skipIf(
    connection.vendor == "sqlite",
    "collect_sql with SQLite test DB triggers schema editor FK limitation",
)
class CollectSQLTests(TestCase):
    """Test collect_sql returns up/down SQL for a migration (non-SQLite)."""

    def test_collect_sql_forward_returns_create_sql(self):
        conn = connections["default"]
        loader = MigrationLoader(conn, replace_migrations=False)
        sql = collect_sql(loader, APP_LABEL, "0001_initial", backwards=False)
        self.assertIn("CREATE TABLE", sql.upper())
        self.assertIn("example", sql.lower())

    def test_collect_sql_backward_returns_drop_sql(self):
        conn = connections["default"]
        loader = MigrationLoader(conn, replace_migrations=False)
        sql = collect_sql(loader, APP_LABEL, "0001_initial", backwards=True)
        self.assertIn("DROP TABLE", sql.upper())
        self.assertIn("example", sql.lower())
