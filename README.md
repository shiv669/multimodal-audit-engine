# Multimodal Audit Engine

A system that scans video content across multiple modalities—speech, on-screen text, and visuals—to detect compliance violations and flag misleading claims.

## Tech Stack

### Current (MVP - Mistral + LangSmith)
- **Framework**: LangChain for AI/LLM orchestration
- **API**: FastAPI + Uvicorn
- **AI Model**: Mistral AI (free tier)
- **Debugging**: LangSmith for workflow tracing
- **Video Processing**: yt-dlp
- **Environment**: Python 3.13+

### Planned (Future Phases)
- **Search**: OpenSearch for semantic indexing
- **AWS**: S3, Lambda integration for production

## Features

- **Audio Analysis**: Extracts and analyzes speech from video content
- **Text Extraction**: Identifies on-screen captions and overlays
- **Visual Understanding**: Processes key visuals and imagery
- **Compliance Checking**: Cross-references information across modalities to detect violations
- **LLM-Powered Analysis**: Uses Mistral AI for intelligent claim evaluation
- **Reporting**: Generates compliance reports with flagged violations

## Getting Started

### Quick Start

1. **Install dependencies**:
```bash
pip install langchain-core langchain-community langchain-mistralai yt-dlp pypdf langchain-text-splitters tiktoken langsmith python-dotenv fastapi uvicorn --user
```

2. **Get Free API Keys** (no credit card needed):
   - **Mistral AI**: Sign up at [console.mistral.ai](https://console.mistral.ai) → Get API key
   - **LangSmith**: Sign up at [smith.langchain.com](https://smith.langchain.com) → Get API key

3. **Set up `.env`**:
```bash
cp .env.example .env
```
Then edit `.env` and add your API keys:
```env
MISTRAL_API_KEY=your_key_from_console.mistral.ai
LANGSMITH_API_KEY=your_key_from_smith.langchain.com
```

4. **See [FREE_SETUP_GUIDE.md](FREE_SETUP_GUIDE.md) for detailed step-by-step instructions**

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
