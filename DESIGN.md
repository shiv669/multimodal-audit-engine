# Design Notes

## Project Overview

Multimodal-audit-engine scans video content across multiple streams—speech, on-screen text, and visuals—to detect compliance violations and flag misleading claims.

## Current Progress

### Setup Complete
- Python 3.13+ project initialized with `uv` package manager
- Git repository configured and linked to GitHub remote
- Backend dependencies installed for LangChain-based AI pipeline

### LangGraph State Architecture (Implemented)
Defined formal state schema for video processing workflow:

**complianceIssue**: Individual violation detection
```python
{
  category: str         # Claim type or violation category
  description: str      # Detailed violation description
  severity: str         # High/Medium/Low
  timestamp: Optional   # When in video violation occurs
}
```

**videoState**: Complete workflow state
```python
# Input
video_url: str         # Source video URL
video_id: str          # Unique identifier per analysis

# Extraction Phase
local_file_path: str   # Downloaded video on disk
video_metadata: Dict   # Resolution, duration, etc.
video_transcript: str  # Speech-to-text output
ocr_text: List[str]    # Screen text (claims, overlays)

# Analysis Phase
compliance_result: List[complianceIssue]  # Accumulating violations

# Output
audit_result: str      # Pass/Fail determination
audit_report: str      # Human-readable compliance report

# Error Tracking
errors: List[str]      # Pipeline errors (accumulating)
```

### Pipeline Flow (Defined)
```
Video URL
  ↓
yt-dlp (Download & Store)
  ├─→ Audio → Whisper (free, local) → Transcripts
  ├─→ Frames → OCR/Tesseract (free) → Screen text
  ↓
Mistral Embeddings (free tier)
  ↓
Vector Indexing (FAISS/Chroma - free, local)
  ↓
PDF Guidelines (indexed as vectors)
  ↓
Mistral LLM Analysis (free tier)
  ↓
Detect Violations & Generate Report
```

### Tech Stack (Current - MVP Phase)
- **LangGraph**: State machine and workflow orchestration
- **LangChain**: AI/LLM framework
- **Mistral AI**: Language model + embeddings (free tier)
- **Video Processing**: yt-dlp (download)
- **Speech-to-Text**: Whisper (local, free, open-source)
- **OCR**: Tesseract/PaddleOCR (free, open-source)
- **Vector DB**: FAISS or Chroma (free, local)
- **PDF Handling**: pypdf
- **API**: FastAPI + Uvicorn
- **Debugging**: LangSmith
- **Development**: python-dotenv

### Tech Stack (Planned for Future Phases)
- **Search**: OpenSearch for semantic search and indexing
- **AWS Integration**: boto3, S3, Lambda for production deployment
- **Observability**: OpenTelemetry for distributed tracing

### Open Questions Addressed
- ✅ State schema defined in LangGraph
- ✅ Multi-modal pipeline architecture established
- ✅ Technology choices locked for MVP (Mistral, free open-source tools)

### Open Questions Remaining
- How to handle audio extraction in production (latency)?
- Optimal chunk size for vector indexing from transcripts?
- How to handle videos without speech content?
- Fine-tuning needs for OCR on specific industries?

## Next Steps
1. Implement transcript extraction module (Whisper integration)
2. Implement OCR module (Tesseract integration)
3. Implement vector indexing (FAISS/Chroma setup)
4. Implement PDF guideline indexing
5. Build LangGraph nodes for each extraction step
6. Integrate Mistral embeddings and LLM analysis
7. Create audit report generator
8. End-to-end testing with sample videos

## Key Principles
- Multimodality first in every design decision
- Build and validate incrementally with real content
- Type-safe workflow with explicit state transitions
- Clear error handling at each pipeline stage
