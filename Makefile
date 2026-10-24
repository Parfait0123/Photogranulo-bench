.PHONY: install test count manifest verify

install:
	uv sync

test:
	uv run pytest

# Phase 1 : sur la copie brute désignée par le profil de paths.yaml
count:
	uv run python scripts/build_manifest.py count

manifest:
	uv run python scripts/build_manifest.py build

verify:
	uv run python scripts/build_manifest.py verify
