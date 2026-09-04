"""Undo checkpoints for edit_file / write_file."""

from __future__ import annotations

from anycoder import checkpoints
from anycoder.tools.edit_file import EditFileTool
from anycoder.tools.write_file import WriteFileTool


def setup_function():
    checkpoints.clear()


def test_edit_then_undo_restores_previous_bytes(tmp_path):
    f = tmp_path / "a.py"
    f.write_text("v1\n", encoding="utf-8")
    assert EditFileTool().execute(str(f), "v1", "v2").startswith("Edited")
    assert f.read_text() == "v2\n"

    assert checkpoints.undo() == f"Restored {f}."
    assert f.read_text() == "v1\n"


def test_undo_removes_file_created_by_write(tmp_path):
    f = tmp_path / "new.py"
    assert not f.exists()
    WriteFileTool().execute(str(f), "print(1)\n")
    assert f.exists()

    assert checkpoints.undo() == f"Removed {f} (created this session)."
    assert not f.exists()


def test_undo_pops_one_mutation_at_a_time(tmp_path):
    f = tmp_path / "a.py"
    f.write_text("v1\n", encoding="utf-8")
    EditFileTool().execute(str(f), "v1", "v2")
    EditFileTool().execute(str(f), "v2", "v3")

    assert checkpoints.pending() == 2
    checkpoints.undo()
    assert f.read_text() == "v2\n"
    checkpoints.undo()
    assert f.read_text() == "v1\n"


def test_failed_edit_leaves_no_checkpoint(tmp_path):
    f = tmp_path / "a.py"
    f.write_text("v1\n", encoding="utf-8")
    result = EditFileTool().execute(str(f), "missing", "v2")
    assert result.startswith("[error]") or "not found" in result.lower()
    assert checkpoints.pending() == 0
    assert checkpoints.undo() == "Nothing to undo."
