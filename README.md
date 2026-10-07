# Compliance QA Pipeline

This project is a Python-based compliance auditing workflow for reviewing uploaded or linked videos for regulatory and brand-risk issues. The current implementation centers on a LangGraph workflow that:

- downloads a YouTube video,
- extracts video and transcript metadata,
- sends the transcript and OCR text to a retrieval-augmented audit flow,
- compares the extracted content against policy documents in Azure AI Search,
- returns a final compliance status and report.

## What the project does

The core flow is defined in the graph layer and follows this pattern:

```text
index_video_node -> audit_content_node -> final result
```

The indexing stage prepares the input content for review, and the audit stage uses Azure OpenAI plus a vector search index to assess the material against compliance rules.

## Architecture overview

- `backend/src/graph/` holds the workflow, state schema, and node implementations.
- `backend/src/services/` is intended for external integrations such as Azure Video Indexer.
- `backend/src/api/` is reserved for API and telemetry endpoints.
- `backend/src/complianceqapipeline/` contains the package entry point.
- `backend/data/` is the local working area for downloaded or processed media.

## Current status

This repository is in an active development state. The workflow and node logic are present, but some service integrations and runtime orchestration are still being completed. The project is best viewed as a foundation for a compliant media audit application rather than a fully finished end-to-end deployment.

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Azure subscription with access to:
  - Azure OpenAI
  - Azure AI Search
  - Azure Video Indexer (or equivalent media indexing integration)
- A configured `.env` file under the backend folder

## Setup

From the repository root in PowerShell:

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -r Requirements.txt
uv pip install -e .
```

If you are using the project environment in a new shell, activate it again before running commands:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Environment variables

Create a local environment file at `backend/.env` and populate it with the values required by your Azure setup. The workflow references variables such as:

```env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_CHAT_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=
TEXT_EMBEDDING_DEPLOYMENT=
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=
```

The code currently uses a value named `TEXT_EMBEDDING_DEPLOYMENT` exactly as seen in the workflow, so keep that spelling consistent unless you update the code.

> Do not commit secrets to source control. Keep your `.env` file local and excluded from Git.

## Project structure

```text
ComplianceQAPipeline/
├─ .python-version
├─ README.md
├─ pyproject.toml
├─ Requirements.txt
├─ uv.lock
├─ backend/
│  ├─ .env
│  ├─ Dockerfile
│  ├─ data/
│  ├─ scripts/
│  ├─ src/
│  │  ├─ api/
│  │  ├─ complianceqapipeline/
│  │  ├─ graph/
│  │  └─ services/
│  └─ test/
└─ .venv/
```

## Local development workflow

The package entry point is defined in `pyproject.toml` and currently resolves to the `complianceqapipeline` command. From the repo root, the package can be installed in editable mode and then invoked with:

```powershell
complianceqapipeline
```

At the moment, this entry point only demonstrates a basic placeholder output. The full end-to-end graph execution depends on the Azure services and the remaining integration code being configured properly.

## Typical use case

A typical run would:

1. provide a video URL,
2. fetch the media and transcript,
3. extract insight data,
4. run the LangGraph audit flow,
5. query a compliance knowledge base,
6. return PASS/FAIL findings with a narrative report.

## Recommended next steps

- complete the Azure Video Indexer integration in `backend/src/services/`
- implement the API surface in `backend/src/api/`
- add actual environment validation and startup checks
- add tests for the graph flow and service adapters
- flesh out the final report schema and output formatting

## Notes

The repository is intentionally structured as a starter implementation for an AI-powered video compliance QA pipeline. The code already shows the intended design pattern using LangGraph and Azure AI services, and the next phase is to close the gaps between the scaffold and the full production workflow.
