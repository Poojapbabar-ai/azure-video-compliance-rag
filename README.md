# Compliance QA Pipeline

A Python scaffold for a video compliance audit and question-answering pipeline. The graph module describes the intended audit workflow; the package entry point and backend modules are still under development.

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

The project metadata is in `pyproject.toml`, and the package is built from `backend/src`. The additional application dependencies are listed in `Requirements.txt`.

Keep local credentials and environment-specific values in `backend/.env`. Environment files and virtual environments are excluded from Git. Use `.env.example` for documenting variable names without including secret values.

## Current Status

The installed `complianceqapipeline` command currently runs a placeholder entry point. The API, graph workflow, and integration services are not yet ready to run as a complete pipeline.

## Project Layout

```text
backend/
	data/                  Local data workspace
	scripts/               Utility scripts
	src/
		api/                 API and telemetry modules
		complianceqapipeline/ Python package and command-line entry point
		graph/               Audit workflow and state
		services/            Integration services
	test/                  Tests
```
