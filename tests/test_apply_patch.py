"""apply_patch: atomic multi-block exact-match edits."""

from anycoder.tools import TOOL_MAP
from anycoder.tools.apply_patch import ApplyPatchTool, _parse_blocks


def _patch(*blocks: tuple[str, str]) -> str:
    parts = []
    for old, new in blocks:
        parts.append(f"<<<<<<< SEARCH\n{old}\n=======\n{new}\n>>>>>>> REPLACE")
    return "\n".join(parts)


def test_registered_in_tool_map():
    assert "apply_patch" in TOOL_MAP


def test_parse_blocks_round_trip():
    blocks = _parse_blocks(_patch(("a", "b"), ("c", "d")))
    assert blocks == [("a", "b"), ("c", "d")]


def test_parse_blocks_rejects_unterminated():
    assert _parse_blocks("<<<<<<< SEARCH\na\n=======\nb") .startswith("[error]")
    assert _parse_blocks("no markers here") .startswith("[error]")


def test_apply_two_blocks_atomically(tmp_path):
    f = tmp_path / "app.py"
    f.write_text("x = 1\ny = 2\nz = 3\n")
    result = ApplyPatchTool().execute(str(f), _patch(("x = 1", "x = 10"), ("z = 3", "z = 30")))
    assert result.startswith("Patched")
    assert f.read_text() == "x = 10\ny = 2\nz = 30\n"


def test_missing_anchor_writes_nothing(tmp_path):
    f = tmp_path / "app.py"
    f.write_text("x = 1\ny = 2\n")
    result = ApplyPatchTool().execute(str(f), _patch(("x = 1", "x = 10"), ("nope", "nada")))
    assert "not found" in result
    assert f.read_text() == "x = 1\ny = 2\n"


def test_duplicate_anchor_writes_nothing(tmp_path):
    f = tmp_path / "app.py"
    f.write_text("x = 1\nx = 1\n")
    result = ApplyPatchTool().execute(str(f), _patch(("x = 1", "x = 10")))
    assert "matches 2 times" in result
    assert f.read_text() == "x = 1\nx = 1\n"


def test_overlapping_blocks_rejected(tmp_path):
    f = tmp_path / "app.py"
    f.write_text("abcdef\n")
    result = ApplyPatchTool().execute(str(f), _patch(("abc", "x"), ("bcd", "y")))
    assert "overlap" in result
    assert f.read_text() == "abcdef\n"


def test_out_of_order_blocks_apply(tmp_path):
    f = tmp_path / "app.py"
    f.write_text("aaa\nbbb\nccc\n")
    result = ApplyPatchTool().execute(str(f), _patch(("ccc", "CCC"), ("aaa", "AAA")))
    assert result.startswith("Patched")
    assert f.read_text() == "AAA\nbbb\nCCC\n"
