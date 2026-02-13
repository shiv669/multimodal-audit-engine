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

---

## LangGraph Nodes Implementation (nodes.py)

### Design Philosophy

The nodes.py file contains two LangGraph nodes that form the core of the compliance audit pipeline:
1. **videoIndexNode**: Handles video ingestion and data extraction
2. **audio_content_node**: Performs RAG-based compliance analysis

Each node is designed as a pure function that:
- Takes the current `videoState` as input
- Performs specific processing work
- Returns updated state fields
- Handles errors gracefully without breaking the workflow

### Node 1: videoIndexNode

**Purpose**: Download video and extract raw data (transcript, OCR text)

**Key Decisions**:

1. **Local Video Storage**
   - Downloads to `temp_audit_video.mp4` temporarily, then deletes
   - Reason: Avoid storing large video files; only need extracted data
   
2. **Video Service Abstraction**
   - Uses `VideoIndexerService` instead of direct yt-dlp calls
   - Reason: Keeps node logic clean; service handles extraction complexity
   
3. **YouTube URL Validation**
   - Checks for "youtube.com" or "youtu.be" patterns
   - Reason: MVP focuses on YouTube; expandable to other sources later
   
4. **Error Accumulation**
   - Returns errors as list (Annotated with `operator.add`)
   - Reason: Multiple errors possible; list accumulates without losing context
   - Returns default values (empty lists) on failure so pipeline continues

### Node 2: audio_content_node

**Purpose**: Perform RAG-based compliance audit by comparing content against guidelines

**Key Decisions**:

1. **Transcript Requirement Check**
   - Returns early with "fail" status if transcript missing
   - Reason: Can't audit without transcript; fail gracefully instead of crashing
   
2. **Mistral for LLM + Embeddings**
   - Same vendor for both LLM inference and embedding generation
   - Reason: Unified API, free tier, simplified key management
   
3. **FAISS as Vector Store**
   - Uses `langchain_community.vectorstores.FAISS`
   - Local, in-memory storage; populated from PDF guidelines
   - Reason: Free, fast, no external DB dependency for MVP
   
4. **RAG (Retrieval-Augmented Generation)**
   - Combines transcript + OCR into single query
   - Retrieves top-3 similar rules from vector DB
   - Sends both retrieved rules and content to LLM
   - Reason: Context-aware analysis; LLM sees exact compliance rules before judging
   
5. **Explicit JSON Output Format**
   - System prompt specifies exact JSON structure
   - Node parses JSON from LLM response
   - Reason: Predictable output; reliable parsing; no guessing field names
   
6. **Markdown Unwrapping**
   - Handles LLM wrapping JSON in ``` code blocks
   - Uses regex to extract JSON content
   - Reason: LLM often adds markdown formatting; must strip before JSON parsing
   
7. **Resilient Error Handling**
   - Logs both error message and raw LLM response
   - Returns empty results instead of breaking workflow
   - Reason: Node should fail gracefully; LangGraph continues executing

### Design Decision Table

| What | Why | Alternative | Why Not Chosen |
|------|-----|-------------|---|
| Separate extraction & analysis nodes | Modular, reusable, testable | Single monolithic node | Hard to debug, hard to reuse |
| Return state dicts | LangGraph standard pattern | Raise exceptions | Breaks workflow, no recovery |
| Mistral for everything | Free tier, unified API | Multiple vendors | More complexity, more secrets |
| FAISS vector store | Local, free, fast | PostgreSQL | DB dependency, MVP overhead |
| Combined transcript+OCR query | Catch cross-modal violations | Separate queries | Miss inconsistencies between modalities |
| Early return on missing data | Fail fast, clear status | Continue with empty values | Confusing audit results |

### Future Extensibility

The node design allows:
1. Adding new nodes (e.g., image analysis)
2. Swapping LLM (MistralChat → LlamaCpp without changing signature)
3. Switching vector DB (FAISS → Chroma) transparently
4. Supporting multiple compliance frameworks (add audit nodes)

All possible because nodes are isolated, stateful, and communicate only through `videoState`.

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
