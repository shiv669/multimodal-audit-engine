# Design Notes

## Project Overview

Multimodal-audit-engine scans video content across multiple streams—speech, on-screen text, and visuals—to detect compliance violations and flag misleading claims.

## Current Progress

### Setup Complete
- Python 3.13+ project initialized with `uv` package manager
- Git repository configured and linked to GitHub remote
- Basic project structure in place (main.py, pyproject.toml, README.md)
- Backend dependencies installed for LangChain-based AI pipeline

### Tech Stack (Current - MVP Phase)
- **LangChain**: Core framework for AI/LLM workflows (langchain-core, langchain-community, langchain-mistralai)
- **AI Model**: Mistral AI for language understanding and claim analysis
- **Data Processing**: yt-dlp for video download, pypdf for document handling, langchain-text-splitters
- **API**: FastAPI with Uvicorn for backend server
- **Debugging**: LangSmith for workflow tracing and debugging
- **Tokenization**: tiktoken for token counting
- **Development**: python-dotenv for environment management

### Tech Stack (Planned for Future Phases)
- **Search**: OpenSearch for semantic search and indexing
- **AWS Integration**: boto3, S3, Lambda for production deployment
- **Observability**: OpenTelemetry for distributed tracing

### Core Conceptual Understanding
- Violations can originate from multiple modalities or inconsistencies between them
- Pipeline approach: Ingestion → Extraction → Analysis → Correlation → Reporting
- Each modality requires specialized analysis (audio transcription, text extraction, visual understanding)
- Using LangChain to orchestrate multi-step AI workflows for analysis

### Open Questions
- How to reliably extract text from dynamic video content?
- What speech recognition accuracy is achievable without fine-tuning?
- How should industry guidelines be formalized and matched?
- How to balance sensitivity with minimizing false positives?

## Next Steps
1. Define the guideline framework
2. Set up dependencies for video processing and AI models
3. Build first audio extraction module as proof-of-concept
4. Create basic pipeline in main.py
5. Test against sample videos

## Key Principles
- Multimodality first in every design decision
- Build and validate incrementally with real content
- Explicit system behavior over implicit assumptions
- Correctness over speed
