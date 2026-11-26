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
    monkeypatch.setitem(sys.modules, "src.gemini_client", gemini)
    tools = ModuleType("tools")
    for name in ("file_tools", "system_tools", "content_tools", "calendar_tools"):
        setattr(tools, name, SimpleNamespace())
    monkeypatch.setitem(sys.modules, "tools", tools)
    spec = importlib.util.spec_from_file_location("assistant_under_test", "src/assistant.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retry_keeps_one_command_and_reports_tool_outcome(assistant, monkeypatch):
    class FakeAPIError(Exception):
        code = 503

    monkeypatch.setattr(assistant, "APIError", FakeAPIError)
    monkeypatch.setattr(assistant.time, "sleep", Mock())
    action = Mock(return_value="No visible window found.")
