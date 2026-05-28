"""
Pytest configuration and fixtures.
"""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    return tmp_path
