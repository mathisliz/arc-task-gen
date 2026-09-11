# Clone the repository
git clone https://github.com/mathisliz/arc-task-gen.git
cd arc-task-gen

# Create a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install the package (no external requirements, but this registers the CLI)
pip install -e .
```

## Usage

### Interactive mode (default)

```bash
$ python3 main.py
```

You will see a menu:

```
=== ARC‑Task‑Gen‑Lite ===
1. Generate a random task
2. Generate multiple tasks
3. Show example task
4. Exit
Select an option [1-4]:
```

Choose an option and the generated task(s) will be printed as pretty‑printed JSON.

### Non‑interactive mode (pipeline‑friendly)

When the script detects that **stdin is not a TTY**, it outputs a single task JSON and exits. This is handy for chaining commands:

```bash
# Generate a task and pipe it to jq for pretty printing
python3 main.py | jq .
```

### Generating multiple tasks from the command line

While the interactive menu already supports this, you can also script it:

```bash
# Generate 5 tasks and store them in a file
python3 -c "import json, sys; from main import generate_grid_task; \
tasks = [generate_grid_task() for _ in range(5)]; \
print(json.dumps(tasks, indent=2))" > tasks.json
```

## Project Structure

```
arc-task-gen/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI configuration
├── main.py                 # Core CLI implementation (self‑contained)
├── tests/
│   ├── __init__.py
│   └── test_main.py        # pytest suite covering task generation
├── README.md               # This documentation
├── LICENSE                 # MIT License
└── pyproject.toml          # Optional packaging metadata (if using poetry/pip)
```

## Tests

The project uses **pytest** for its test suite.

```bash
# Install test dependencies (if not already in the venv)
pip install pytest

# Run the tests
pytest -v