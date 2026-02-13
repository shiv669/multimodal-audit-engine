# Multimodal Audit Engine

A system that scans video content across multiple modalities—speech, on-screen text, and visuals—to detect compliance violations and flag misleading claims.

## Tech Stack

- **Framework**: LangChain for AI/LLM orchestration
- **API**: FastAPI + Uvicorn
- **AI Model**: Mistral AI
- **Search**: OpenSearch
- **Video Processing**: yt-dlp
- **Observability**: OpenTelemetry
- **AWS**: boto3 integration
- **Environment**: Python 3.13+

## Features

- **Audio Analysis**: Extracts and analyzes speech from video content
- **Text Extraction**: Identifies on-screen captions and overlays
- **Visual Understanding**: Processes key visuals and imagery
- **Compliance Checking**: Cross-references information across modalities to detect violations
- **LLM-Powered Analysis**: Uses Mistral AI for intelligent claim evaluation
- **Reporting**: Generates compliance reports with flagged violations

## Getting Started

### Installation

```bash
# Install dependencies
pip install boto3 langchain-core langchain-community langchain-mistralai opensearch-py yt-dlp pypdf langchain-text-splitters tiktoken langsmith opentelemetry-sdk opentelemetry-instrumentation-fastapi --user
```

### Environment Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your actual credentials:
   - **MISTRAL_API_KEY**: Get from [console.mistral.ai](https://console.mistral.ai)
   - **LANGSMITH_API_KEY**: Get from [smith.langchain.com](https://smith.langchain.com)
   - **OPENSEARCH_***: Configure based on your OpenSearch instance
   - **AWS_***: Only needed if using AWS services

### Running

```bash
python main.py
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   └── server.py
│   ├── graphs/
│   │   ├── workflow.py
│   │   ├── state.py
│   │   └── nodes.py
│   └── services/
└── scripts/
    └── index_documents.py
```

## Design Philosophy

- Build incrementally with real content validation
- Design for correctness first, speed second
- Make invalid states difficult to represent
- Document decisions and learnings transparently

See [DESIGN.md](DESIGN.md) for detailed architectural notes.
