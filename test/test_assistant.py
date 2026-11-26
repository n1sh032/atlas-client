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
    monkeypatch.setitem(assistant.tool_functions, "close_app", action)
    part = SimpleNamespace(
        text="Closed it.",
        function_call=SimpleNamespace(name="close_app", args={"query": "Notepad"}),
    )
    result = SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))])
    generate = assistant.client.models.generate_content
    generate.side_effect = [FakeAPIError(), result]

    assert assistant.talk_to_atlas_safe("Close Notepad") == "No visible window found."
    action.assert_called_once_with(query="Notepad")
    assert generate.call_count == 2
    assert len(assistant.chat_history) == 2
    assert assistant.load_history() == assistant.chat_history


def test_browser_can_disable_desktop_actions(assistant):
    action = Mock(return_value="Executed")
    assistant.tool_functions["close_app"] = action
    part = SimpleNamespace(
        text="Closed.", function_call=SimpleNamespace(name="close_app", args={"query": "Notepad"}),
    )
    assistant.client.models.generate_content.return_value = SimpleNamespace(
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))],
    )
    reply = assistant.talk_to_atlas("Close Notepad", allow_actions=False)
