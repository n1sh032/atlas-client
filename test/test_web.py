from src.web import AtlasApplication


def test_invalid_browser_messages_do_not_load_desktop_tools():
    app = AtlasApplication()
    assert app.execute("chat", {"message": ""})["kind"] == "error"
