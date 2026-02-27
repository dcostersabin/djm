# DJM: Django migration utilities (goose-style SQL, base mixins)
# Use `uv run` or activate .venv before running make targets.

.PHONY: help migrate goose clean install build

help:
	@echo "DJM – Django migration utilities (one app: djm)"
	@echo ""
	@echo "  make migrate     Apply Django migrations"
	@echo "  make goose       Generate goose-style SQL files (djm app, dir: goose_migrations)"
	@echo "  make goose OUT=dir   Generate into dir (e.g. OUT=./sql)"
	@echo "  make clean       Remove generated goose files and __pycache__"
	@echo "  make install     Install dependencies (uv sync)"
	@echo "  make build       Build wheel/sdist for distribution"

migrate:
	uv run python manage.py migrate

goose:
	@OUT=$${OUT:-goose_migrations}; uv run python manage.py generate_goose -o $$OUT

clean:
	rm -f goose_migrations/*.sql 2>/dev/null || true
	find . -type d -name __pycache__ ! -path './.venv/*' -exec rm -rf {} + 2>/dev/null || true

install:
	uv sync

build:
	uv build
