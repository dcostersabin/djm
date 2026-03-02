# DJM: Django migration utilities (goose/SQLx SQL, base mixins)
# Use `uv run` or activate .venv before running make targets.

.PHONY: help migrate goose sqlx diesel test clean install build

help:
	@echo "DJM – Django migration utilities (one app: djm)"
	@echo ""
	@echo "  make migrate     Apply Django migrations"
	@echo "  make goose       Generate goose-style SQL files (djm app, dir: migrations)"
	@echo "  make goose OUT=dir   Generate into dir (e.g. OUT=./goose_migrations)"
	@echo "  make sqlx        Generate SQLx SQL files (djm app, dir: migrations)"
	@echo "  make sqlx OUT=dir   Generate into dir (e.g. OUT=./db/migrations)"
	@echo "  make diesel      Generate Diesel CLI migrations (djm app, dir: migrations)"
	@echo "  make diesel OUT=dir   Generate into dir (e.g. OUT=./diesel_migrations)"
	@echo "  make test        Run tests (djm app)"
	@echo "  make clean       Remove generated goose/sqlx/diesel files and __pycache__"
	@echo "  make install     Install dependencies (uv sync)"
	@echo "  make build       Build wheel/sdist for distribution"

migrate:
	uv run python manage.py migrate

goose:
	@OUT=$${OUT:-migrations}; uv run python manage.py goose -o $$OUT

sqlx:
	@OUT=$${OUT:-migrations}; uv run python manage.py sqlx -o $$OUT

diesel:
	@OUT=$${OUT:-migrations}; uv run python manage.py diesel -o $$OUT

test:
	uv run python manage.py test djm

clean:
	rm -f goose_migrations/*.sql 2>/dev/null || true
	rm -f migrations/*.sql migrations/*.up.sql migrations/*.down.sql 2>/dev/null || true
	rm -rf migrations/*/ 2>/dev/null || true
	rm -f migrations/.goose migrations/.sqlx migrations/.diesel 2>/dev/null || true
	find . -type d -name __pycache__ ! -path './.venv/*' -exec rm -rf {} + 2>/dev/null || true

install:
	uv sync

build:
	uv build
