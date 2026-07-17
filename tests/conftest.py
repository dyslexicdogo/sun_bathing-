"""Shared pytest fixtures."""
import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    """Return a function that loads and parses a JSON fixture by filename."""
    def _load(filename: str):
        path = FIXTURES_DIR / filename
        return json.loads(path.read_text())
    return _load