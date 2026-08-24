"""Tests for the run_tests tool. subprocess is mocked throughout."""

import json
import subprocess
from unittest.mock import patch

import pytest

from anycoder.tools.run_tests import RunTestsTool, _detect_command


def _completed(stdout="", stderr="", returncode=0):
    return subprocess.CompletedProcess(
        args=["x"], returncode=returncode, stdout=stdout, stderr=stderr
    )


@pytest.fixture
def tool():
    return RunTestsTool()


# --- detection ---

def test_detect_pytest_from_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n", encoding="utf-8")
    assert _detect_command(str(tmp_path)) == "pytest -q"


def test_detect_pytest_from_pytest_ini(tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    assert _detect_command(str(tmp_path)) == "pytest -q"


def test_detect_pytest_from_setup_cfg(tmp_path):
    (tmp_path / "setup.cfg").write_text("[tool:pytest]\n", encoding="utf-8")
    assert _detect_command(str(tmp_path)) == "pytest -q"


def test_detect_plain_python_project_probes(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
    assert _detect_command(str(tmp_path)) == "python -m pytest -q"


def test_detect_tests_dir_only_probes(tmp_path):
    (tmp_path / "tests").mkdir()
    assert _detect_command(str(tmp_path)) == "python -m pytest -q"


def test_detect_npm(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"test": "jest"}}), encoding="utf-8"
    )
    (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")
    assert _detect_command(str(tmp_path)) == "npm test"


def test_detect_pnpm_from_lockfile(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"test": "vitest run"}}), encoding="utf-8"
    )
    (tmp_path / "pnpm-lock.yaml").write_text("", encoding="utf-8")
    assert _detect_command(str(tmp_path)) == "pnpm test"


def test_placeholder_test_script_doesnt_count(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"test": 'echo "Error: no test specified" && exit 1'}}),
        encoding="utf-8",
    )
    assert _detect_command(str(tmp_path)) is None


def test_detect_nothing(tmp_path):
    assert _detect_command(str(tmp_path)) is None


# --- execute ---

def test_execute_runs_detected_command(tool, tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    with patch("anycoder.tools.run_tests.subprocess.run") as run:
        run.return_value = _completed(stdout="3 passed in 0.12s\n")
        result = tool.execute(path=str(tmp_path))
    assert "$ pytest -q" in result
    assert "3 passed" in result
    assert run.call_args.kwargs["cwd"] == str(tmp_path)
    assert run.call_args.kwargs["timeout"] == 300


def test_execute_reports_exit_code_on_failure(tool, tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    with patch("anycoder.tools.run_tests.subprocess.run") as run:
        run.return_value = _completed(stdout="1 failed, 2 passed\n", returncode=1)
        result = tool.execute(path=str(tmp_path))
    assert "1 failed" in result
    assert "[exit code: 1]" in result


def test_execute_includes_stderr(tool, tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    with patch("anycoder.tools.run_tests.subprocess.run") as run:
        run.return_value = _completed(stdout="out\n", stderr="warn: something\n")
        result = tool.execute(path=str(tmp_path))
    assert "[stderr]" in result
    assert "warn: something" in result


def test_execute_no_detection_explains_and_runs_nothing(tool, tmp_path):
    with patch("anycoder.tools.run_tests.subprocess.run") as run:
        result = tool.execute(path=str(tmp_path))
    assert "Could not detect" in result
    run.assert_not_called()


def test_execute_timeout(tool, tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    with patch("anycoder.tools.run_tests.subprocess.run") as run:
        run.side_effect = subprocess.TimeoutExpired(cmd="pytest -q", timeout=5)
        result = tool.execute(path=str(tmp_path), timeout=5)
    assert "timed out" in result.lower()
    assert "5s" in result


def test_execute_truncates_but_keeps_head_and_tail(tool, tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    head = "collected 5000 items\n"
    tail = "FAILED tests/test_x.py::test_y - AssertionError\n"
    with patch("anycoder.tools.run_tests.subprocess.run") as run:
        run.return_value = _completed(stdout=head + "x" * 20000 + tail, returncode=1)
        result = tool.execute(path=str(tmp_path))
    assert "truncated" in result
    assert "collected 5000 items" in result  # head survives
    assert "FAILED tests/test_x.py" in result  # tail with the failure survives
    assert len(result) < 15_000 + 300


def test_execute_rejects_bad_directory(tool):
    result = tool.execute(path="/nonexistent/dir/xyz")
    assert "[error]" in result
