import importlib.util
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest

from src import config


@pytest.fixture
def assistant(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "memory_file", str(tmp_path / "history.json"))
    gemini = ModuleType("src.gemini_client")
    gemini.client = SimpleNamespace(models=SimpleNamespace(generate_content=Mock()))
