"""
DJM CLI: init a project or generate goose/SQLx migrations.

  djm init [path]     Create a new DJM project (default: current directory)
  djm goose [-o DIR]  Generate goose-style SQL migrations (run from project root)
  djm sqlx [-o DIR]   Generate SQLx-style SQL migrations (run from project root)
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="djm",
        description="DJM – Django models to goose-style SQL migrations.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # djm init [path]
    init_p = subparsers.add_parser("init", help="Create a new DJM project")
    init_p.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project directory (default: current directory)",
    )

    # djm goose [-o dir]
    goose_p = subparsers.add_parser("goose", help="Generate goose SQL migrations")
    goose_p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("migrations"),
        help="Output directory for .sql files (default: migrations)",
    )

    # djm sqlx [-o dir]
    sqlx_p = subparsers.add_parser("sqlx", help="Generate SQLx SQL migrations")
    sqlx_p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("migrations"),
        help="Output directory for .sql files (default: migrations)",
    )

    args = parser.parse_args()

    if args.command == "init":
        return cmd_init(Path(args.path))
    if args.command == "goose":
        return cmd_goose(args.output_dir)
    if args.command == "sqlx":
        return cmd_sqlx(args.output_dir)
    return 0


def cmd_init(dest: Path) -> int:
    dest = dest.resolve()
    if dest.exists() and any(dest.iterdir()):
        print(f"Error: {dest} is not empty. Choose another path or use an empty directory.", file=sys.stderr)
        return 1

    try:
        template_dir = _get_template_dir()
    except Exception as e:
        print(f"Error: could not find project template: {e}", file=sys.stderr)
        return 1

    dest.mkdir(parents=True, exist_ok=True)
    for name in _list_template_contents(template_dir):
        src = template_dir / name
        out = dest / name
        if src.is_dir():
            shutil.copytree(src, out, dirs_exist_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out)

    print(f"Created DJM project at {dest}")
    print("Next steps:")
    cd_name = dest.name if dest.name != "." else dest
    print(f"  cd {cd_name}")
    print("  uv sync   # or: pip install -e .")
    print("  uv run python manage.py makemigrations djm")
    print("  uv run python manage.py migrate")
    print("  uv run python manage.py goose   # → migrations/*.sql")
    print("  uv run python manage.py sqlx    # → migrations/*.up.sql, *.down.sql")
    return 0


def _get_template_dir() -> Path:
    try:
        from importlib.resources import files
        pkg = files("djm")
        return pkg / "project_template"
    except Exception:
        pass
    # Fallback: __file__ relative (e.g. development)
    this = Path(__file__).resolve().parent
    return this / "project_template"


def _list_template_contents(template_dir: Path):
    """Yield relative paths for all files and dirs in template (top-level names)."""
    if not template_dir.is_dir():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    return [p.name for p in template_dir.iterdir()]


def cmd_goose(output_dir: Path) -> int:
    cwd = Path.cwd()
    manage_py = cwd / "manage.py"
    if not manage_py.is_file():
        print("Error: no manage.py in current directory. Run 'djm goose' from the project root.", file=sys.stderr)
        return 1

    result = subprocess.run(
        [sys.executable, "manage.py", "goose", "-o", str(output_dir)],
        cwd=cwd,
    )
    return result.returncode


def cmd_sqlx(output_dir: Path) -> int:
    cwd = Path.cwd()
    manage_py = cwd / "manage.py"
    if not manage_py.is_file():
        print("Error: no manage.py in current directory. Run 'djm sqlx' from the project root.", file=sys.stderr)
        return 1

    result = subprocess.run(
        [sys.executable, "manage.py", "sqlx", "-o", str(output_dir)],
        cwd=cwd,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main() or 0)
