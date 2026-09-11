#!/usr/bin/env python3
"""
arc-task-gen-lite
A tiny, self‑contained CLI that generates simple ARC‑style tasks.

Features
--------
- No external dependencies (standard library only).
- Works both interactively and in non‑interactive pipelines.
- Generates random arithmetic grid tasks resembling ARC‑AGI‑1 format.
- MIT licensed.

Usage
-----
Run without arguments:

    $ python3 main.py

If run in a terminal, an interactive menu is shown.
If stdin is not a TTY (e.g., piped), a single task is printed as JSON.
"""

import sys
import json
import random
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------- #
# Core task generation logic
# --------------------------------------------------------------------------- #

def _random_color():
    """Return a random integer between 0 and 9 representing a colour."""
    return random.randint(0, 9)

def generate_grid_task(size: int = 3) -> dict:
    """
    Generate a simple ARC‑style task.

    The task consists of an input grid (size x size) filled with random colours
    and an output grid where each colour is incremented by 1 modulo 10.

    Returns
    -------
    dict
        A dictionary with keys ``input`` and ``output`` containing the grids.
    """
    input_grid = [[_random_color() for _ in range(size)] for _ in range(size)]
    output_grid = [[(cell + 1) % 10 for cell in row] for row in input_grid]

    return {
        "task_id": f"task-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(0, 9999)}",
        "description": "Increment each cell colour by 1 (mod 10).",
        "input": input_grid,
        "output": output_grid,
    }

def task_to_json(task: dict) -> str:
    """Serialize a task dictionary to a pretty‑printed JSON string."""
    return json.dumps(task, indent=2, ensure_ascii=False)

# --------------------------------------------------------------------------- #
# Interactive menu (only shown when stdin is a TTY)
# --------------------------------------------------------------------------- #

def _print_menu():
    print("\n=== ARC‑Task‑Gen‑Lite ===")
    print("1. Generate a random task")
    print("2. Generate multiple tasks")
    print("3. Show example task")
    print("4. Exit")

def _handle_choice(choice: str):
    if choice == "1":
        task = generate_grid_task()
        print("\nGenerated task:")
        print(task_to_json(task))
    elif choice == "2":
        try:
            n = int(input("How many tasks? ").strip())
            if n <= 0:
                raise ValueError
        except (ValueError, EOFError):
            print("Invalid number, defaulting to 3.")
            n = 3
        tasks = [generate_grid_task() for _ in range(n)]
        print("\nGenerated tasks:")
        print(task_to_json(tasks))
    elif choice == "3":
        example = {
            "input": [
                [0, 1, 2],
                [3, 4, 5],
                [6, 7, 8]
            ],
            "output": [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ],
            "description": "Increment each cell by 1 (mod 10)."
        }
        print("\nExample task:")
        print(task_to_json(example))
    elif choice == "4":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice, please select 1‑4.")

def interactive_menu():
    """Run an interactive menu loop."""
    while True:
        _print_menu()
        try:
            choice = input("Select an option [1-4]: ").strip()
        except EOFError:
            # Non‑interactive environment – fall back to default behaviour
            print("\nEOF detected – generating a single task and exiting.")
            print(task_to_json(generate_grid_task()))
            break
        _handle_choice(choice)

# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def main():
    """
    Entry point for the CLI.

    If the standard input is attached to a terminal, an interactive menu is
    presented. Otherwise, a single task is printed to stdout (useful for
    pipelines or automated tests).
    """
    random.seed()  # Initialise from system time / OS entropy

    if sys.stdin.isatty():
        interactive_menu()
    else:
        # Non‑interactive mode: emit a single task as JSON
        task = generate_grid_task()
        print(task_to_json(task))

if __name__ == "__main__":
    main()