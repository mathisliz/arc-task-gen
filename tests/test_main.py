import json
import re
import sys
from types import SimpleNamespace

import pytest

# Import the module under test. Adjust the import path if the module name differs.
import main


def test_random_color_range():
    """_random_color should always return an int in [0, 9]."""
    for _ in range(100):
        c = main._random_color()
        assert isinstance(c, int)
        assert 0 <= c <= 9


@pytest.mark.parametrize("size,expected_shape", [(0, (0, 0)), (1, (1, 1)), (3, (3, 3))])
def test_generate_grid_task_shapes(size, expected_shape):
    """generate_grid_task should respect the requested size, even edge cases."""
    task = main.generate_grid_task(size=size)
    input_grid = task["input"]
    output_grid = task["output"]

    # shape checks
    assert len(input_grid) == expected_shape[0]
    assert all(len(row) == expected_shape[1] for row in input_grid)
    assert len(output_grid) == expected_shape[0]
    assert all(len(row) == expected_shape[1] for row in output_grid)

    # output must be (input+1) % 10
    for i_row, o_row in zip(input_grid, output_grid):
        for i_cell, o_cell in zip(i_row, o_row):
            assert o_cell == (i_cell + 1) % 10


def test_generate_grid_task_content():
    """Default task should contain required keys and a correctly formatted task_id."""
    task = main.generate_grid_task()
    # required keys
    for key in ("task_id", "description", "input", "output"):
        assert key in task

    # description constant
    assert task["description"] == "Increment each cell colour by 1 (mod 10)."

    # task_id format: task-YYYYMMDDhhmmss-xxxx
    pattern = r"^task-\d{14}-\d{1,4}$"
    assert re.match(pattern, task["task_id"])


def test_task_to_json_roundtrip():
    """Serialising then deserialising a task should yield an equivalent dict."""
    task = main.generate_grid_task()
    json_str = main.task_to_json(task)
    # ensure pretty printed (contains newlines and indentation)
    assert "\n" in json_str and "  " in json_str

    loaded = json.loads(json_str)
    # json loads numbers as ints, strings unchanged – compare whole dict
    assert loaded == task


def test_handle_choice_invalid(capsys):
    """Invalid menu choice should print the correct warning."""
    main._handle_choice("9")
    captured = capsys.readouterr()
    assert "Invalid choice, please select 1‑4." in captured.out


def test_handle_choice_exit(monkeypatch):
    """Choice '4' should call sys.exit with code 0."""
    exit_mock = SimpleNamespace(called=False, code=None)

    def fake_exit(code=0):
        exit_mock.called = True
        exit_mock.code = code
        raise SystemExit(code)

    monkeypatch.setattr(sys, "exit", fake_exit)

    with pytest.raises(SystemExit) as excinfo:
        main._handle_choice("4")
    assert exit_mock.called
    assert exit_mock.code == 0
    assert excinfo.value.code == 0


def test_handle_choice_multiple_tasks_default(monkeypatch, capsys):
    """When an invalid number is entered for option 2, default to 3 tasks."""
    inputs = iter(["not-a-number"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main._handle_choice("2")
    out = capsys.readouterr().out

    # The printed JSON should represent a list of three tasks
    data = json.loads(out.splitlines()[-1])  # last line is the JSON
    assert isinstance(data, list)
    assert len(data) == 3
    for task in data:
        assert "input" in task and "output" in task


def test_interactive_menu_eof(monkeypatch, capsys):
    """EOFError during input should trigger the fallback behaviour."""
    # Force input() to raise EOFError on first call
    def raise_eof(_):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    # Run the menu – it should break after handling EOF
    main.interactive_menu()
    out = capsys.readouterr().out

    assert "EOF detected – generating a single task and exiting." in out
    # The last non‑empty line should be a JSON representation of a single task
    json_lines = [ln for ln in out.splitlines() if ln.strip().startswith("{")]
    assert json_lines, "No JSON output found after EOF handling"
    task = json.loads("\n".join(json_lines))
    assert isinstance(task, dict)
    assert "input" in task and "output" in task