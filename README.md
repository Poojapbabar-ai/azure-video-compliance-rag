# Compliance QA Pipeline

A Python project scaffold for a compliance question-answering pipeline. The repository currently contains the initial package and backend module structure; the API, graph workflow, and service modules are placeholders.

## Requirements

- Python 3.14 (see `.python-version`)
- [uv](https://docs.astral.sh/uv/)

## Setup

From the repository root in PowerShell:

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -r Requirements.txt
uv pip install -e .
```

The dependency list is maintained in `Requirements.txt`. Use a local `.env` file for secrets and environment-specific settings; it is excluded from Git. A checked-in `.env.example` may be used to document required variable names without secret values.

## Project Layout

```text
backend/src/
	api/                   API and telemetry modules
	complianceqapipeline/  Python package and command-line entry point
	graph/                 Pipeline graph modules
	services/              Integration services
data/                    Local data workspace
scripts/                 Utility scripts
test/                    Tests
```

The package is built from `backend/src`, as configured in `pyproject.toml`.
