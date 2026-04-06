"""Tests for core modules: config, tools, session, context."""

import os
import tempfile

from anycoder import __version__, Agent, LLMClient, Config
from anycoder.config import MODEL_ALIASES
from anycoder.tools import ALL_TOOLS, TOOL_MAP, get_tool_schemas
from anycoder.session import save_session, load_session, list_sessions


def test_version():
    assert __version__ == "0.1.0"


def test_public_api():
    assert Agent is not None
    assert LLMClient is not None
    assert Config is not None


def test_config_defaults():
    saved = {}
    for k in ["ANYCODER_MODEL", "ANYCODER_API_BASE", "ANYCODER_API_KEY"]:
        if k in os.environ:
            saved[k] = os.environ.pop(k)

    c = Config.from_env()
    assert c.model == "deepseek/deepseek-chat"
    assert c.max_tokens > 0
    os.environ.update(saved)


def test_config_resolve_alias():
    c = Config()
    c.resolve_model("claude")
    assert "claude" in c.model


def test_model_aliases_non_empty():
    assert len(MODEL_ALIASES) > 10


# --- Tools ---

def test_all_tools_loaded():
    assert len(ALL_TOOLS) == 6


def test_tool_schemas():
    schemas = get_tool_schemas()
    assert len(schemas) == 6
    for s in schemas:
        assert s["type"] == "function"
        assert "name" in s["function"]
        assert "description" in s["function"]


def test_read_file():
    tool = TOOL_MAP["read_file"]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("line1\nline2\nline3\n")
        f.flush()
        result = tool.execute(file_path=f.name)
        assert "line1" in result
        assert "3 lines total" in result
        os.unlink(f.name)


def test_read_file_not_found():
    tool = TOOL_MAP["read_file"]
    result = tool.execute(file_path="/nonexistent/file.txt")
    assert "[error]" in result


def test_write_file():
    tool = TOOL_MAP["write_file"]
    path = tempfile.mktemp(suffix=".txt")
    result = tool.execute(file_path=path, content="hello\nworld\n")
    assert "Wrote" in result
    with open(path) as f:
        assert f.read() == "hello\nworld\n"
    os.unlink(path)


def test_edit_file():
    tool = TOOL_MAP["edit_file"]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("foo = 1\nbar = 2\n")
        f.flush()
        result = tool.execute(file_path=f.name, old_string="foo = 1", new_string="foo = 42")
        assert "Replaced 1" in result
        with open(f.name) as rf:
            assert "foo = 42" in rf.read()
        os.unlink(f.name)


def test_edit_file_not_found():
    tool = TOOL_MAP["edit_file"]
    result = tool.execute(file_path="/tmp/no_such_file.py", old_string="x", new_string="y")
    assert "[error]" in result


def test_edit_file_unique_check():
    tool = TOOL_MAP["edit_file"]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("x = 1\nx = 1\n")
        f.flush()
        result = tool.execute(file_path=f.name, old_string="x = 1", new_string="x = 2")
        assert "appears 2 times" in result
        os.unlink(f.name)


def test_glob_tool():
    tool = TOOL_MAP["glob"]
    result = tool.execute(pattern="*.py", path=os.path.dirname(__file__))
    assert "test_core.py" in result


def test_grep_tool():
    tool = TOOL_MAP["grep"]
    result = tool.execute(pattern="def test_version", path=__file__)
    assert "test_version" in result


def test_bash_tool():
    tool = TOOL_MAP["bash"]
    result = tool.execute(command="echo hello")
    assert "hello" in result


def test_bash_timeout():
    tool = TOOL_MAP["bash"]
    result = tool.execute(command="sleep 10", timeout=1)
    assert "timed out" in result.lower()


# --- File change tracking ---

def test_edit_tracks_changes():
    from anycoder.tools.edit_file import _changed_files
    _changed_files.clear()
    tool = TOOL_MAP["edit_file"]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("aaa\nbbb\n")
        f.flush()
        tool.execute(file_path=f.name, old_string="aaa", new_string="zzz")
        assert len(_changed_files) > 0
        os.unlink(f.name)
    _changed_files.clear()


def test_write_tracks_changes():
    from anycoder.tools.edit_file import _changed_files
    _changed_files.clear()
    tool = TOOL_MAP["write_file"]
    path = tempfile.mktemp(suffix=".txt")
    tool.execute(file_path=path, content="tracked\n")
    assert len(_changed_files) > 0
    os.unlink(path)
    _changed_files.clear()


# --- Session ---

def test_session_save_load():
    msgs = [{"role": "user", "content": "test"}]
    save_session(msgs, "test-model", "pytest_anycoder_test")
    loaded = load_session("pytest_anycoder_test")
    assert loaded is not None
    assert loaded[0] == msgs
    assert loaded[1] == "test-model"
    # cleanup
    import pathlib
    pathlib.Path.home().joinpath(".anycoder/sessions/pytest_anycoder_test.json").unlink()


def test_session_not_found():
    assert load_session("nonexistent_session_xyz") is None


def test_list_sessions():
    sessions = list_sessions()
    assert isinstance(sessions, list)
