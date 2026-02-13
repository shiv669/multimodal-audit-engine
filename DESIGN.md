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

---

## LangGraph Workflow Architecture (workflow.py)

### Design Philosophy

The workflow.py file builds a **Directed Acyclic Graph (DAG)** using LangGraph's StateGraph:

```
Input Video State
    ↓
  [INDEXER NODE]  (videoIndexNode)
    ↓
  [AUDITOR NODE]  (audit_content_node)
    ↓
   Output (Pass/Fail + Report)
```

This represents a **sequential, state-driven pipeline** where each node:
1. Receives the complete `videoState`
2. Performs its work
3. Returns updated state fields
4. Passes result to next node

### Workflow Construction

**Step 1: Initialize StateGraph**
```python
workflow = StateGraph(videoState)
```
- Uses `videoState` TypedDict as the state contract
- All nodes communicate through this single, typed state object
- Type safety prevents passing wrong data between nodes

**Step 2: Register Nodes**
```python
workflow.add_node("indexer", videoIndexNode)
workflow.add_node("auditor", audit_content_node)
```
- Each node gets a unique name ("indexer", "auditor")
- Nodes are mapped to their functions (videoIndexNode, audit_content_node)
- Names used for routing and debugging

**Step 3: Define Entry Point**
```python
workflow.set_entry_point("indexer")
```
- All executions start at the "indexer" node
- Reason: Must download and extract video before analysis

**Step 4: Define Edges (Transitions)**
```python
workflow.add_edge("indexer", "auditor")
workflow.add_edge("auditor", END)
```
- Edge 1: After indexer finishes → move to auditor
- Edge 2: After auditor finishes → END (workflow complete)
- All edges are deterministic (no conditional routing yet)

**Step 5: Compile**
```python
app = workflow.compile()
```
- Compiles the DAG into an executable object
- Validates the graph structure
- Returns callable application that can be invoked with input state

### Key Design Decisions

| Decision | Why | Alternative | Why Not |
|----------|-----|-------------|---------|
| Sequential pipeline | Simple, deterministic, easy to debug | Parallel nodes | Adds complexity; can be added later |
| Single StateGraph | Unified state management | Multiple independent workflows | Would lose context between nodes |
| Explicit edge routing | Clear data flow | Conditional routing | Can be added when needed |
| Named nodes | Debugging, logging, tracing | Anonymous nodes | Hard to identify issues |
| Compile before return | Validates graph at startup | Lazy compilation | Easier to catch errors early |

### Execution Flow

**Input**:
```python
{
    "video_url": "https://youtube.com/watch?v=...",
    "video_id": "audit_001",
    # ... other state fields
}
```

**Execution**:
1. LangGraph invokes `videoIndexNode` with full state
2. videoIndexNode downloads video, extracts data, returns partial state update
3. LangGraph merges returned fields into state
4. LangGraph invokes `audit_content_node` with merged state
5. audit_content_node performs RAG audit, returns violations + report
6. LangGraph merges results into state
7. Returns final state to caller (caller can check audit_result, audit_report, errors)

### State Accumulation

LangGraph automatically handles field merging:
- List fields with `Annotated[List, operator.add]` → accumulate items
- Regular fields → overwrite with latest value

Example:
```python
# Node 1 returns: {"errors": ["error_1"]}
# Node 2 returns: {"errors": ["error_2"]}
# Final state:   {"errors": ["error_1", "error_2"]}
```

### Why This Architecture?

1. **Linear vs Complex**
   - MVP needs simple, linear flow
   - Can extend to branching later (conditional edges, parallel paths)

2. **Type Safety**
   - `videoState` is a TypedDict
   - IDE auto-completion for state fields
   - Catches misnamed fields at development time

3. **Statelessness of Nodes**
   - Each node is a pure function
   - No shared mutable state across nodes
   - Easy to test, easy to replace

4. **Observability**
   - LangGraph logs each node execution
   - Can trace state changes between nodes
   - Integrates with LangSmith for monitoring

5. **Resilience**
   - Errors in one node don't break entire pipeline
   - All nodes return dicts, never raise exceptions
   - Errors accumulate in state for final review

### Future Extensibility

This design naturally supports:

1. **Parallel Processing**
   ```python
   # Extract transcripts and OCR in parallel
   workflow.add_node("transcript_extractor", ...)
   workflow.add_node("ocr_extractor", ...)
   workflow.add_edge("indexer", "transcript_extractor")
   workflow.add_edge("indexer", "ocr_extractor")
   workflow.add_edge(["transcript_extractor", "ocr_extractor"], "auditor")
   ```

2. **Conditional Routing**
   ```python
   workflow.add_conditional_edges(
       "indexer",
       should_audit,  # Decision function
       {True: "auditor", False: END}
   )
   ```

3. **Loops (Retries)**
   ```python
   workflow.add_edge("auditor", "indexer")  # Re-analyze with different settings
   ```

4. **Multiple Workflows**
   - Create different graphs for different use cases
   - Reuse the same nodes in different arrangements

### Related Files

- **state.py**: Defines `videoState` TypedDict (the state contract)
- **nodes.py**: Defines `videoIndexNode` and `audit_content_node` (the workers)
- **workflow.py**: Combines states + nodes into executable graph

### Diagram

```
┌─────────────────────────────────────┐
│         INPUT: videoState           │
│  (video_url, video_id, metadata...) │
└──────────────┬──────────────────────┘
               │
               ↓
        ┌──────────────┐
        │   INDEXER    │
        │ - Download   │
        │ - Extract    │
        │   transcripts│
        │ - Extract OCR│
        └──────┬───────┘
               │
               ↓ (State updated with transcript + ocr_text)
        ┌──────────────┐
        │   AUDITOR    │
        │ - RAG search │
        │ - LLM audit  │
        │ - Generate   │
        │   report     │
        └──────┬───────┘
               │
               ↓ (State updated with audit_result + audit_report + compliance_result)
        ┌──────────────┐
        │    OUTPUT    │
        │ Pass/Fail +  │
        │ Violations + │
        │ Report       │
        └──────────────┘
```

---

## PDF Indexing Script (index_documents.py)

### Purpose

Pre-processes compliance guidelines from PDF files and converts them into vector embeddings for similarity search during the audit process. These indexed guidelines are used in the RAG retrieval step of the auditor node.

### Design & Architecture

**Workflow**:
```
PDF Files (compliance guidelines)
    ↓
Load PDFs with PyPDFLoader
    ↓
Split into chunks (RecursiveCharacterTextSplitter)
    ↓
Generate embeddings (Mistral Embeddings API)
    ↓
Store in FAISS vector database
    ↓
Ready for similarity search queries
```

### Key Implementation Decisions

1. **Environment Validation (Lines 31-44)**
   - **Why**: Prevents runtime failures due to missing API keys
   - Checks `MISTRAL_API_KEY` and `LANGSMITH_API_KEY` before processing
   - Logs success/warning for each variable
   - Tests Mistral API connectivity early
   - Initializes FAISS vector store with empty documents

2. **PDF Discovery (Lines 62-64)**
   - **Why**: Flexible input handling; supports multiple compliance documents
   - Searches `backend/data/` folder for all `.pdf` files
   - Logs found files for user awareness
   - Allows adding new guidelines without code changes

3. **Chunking Strategy (Lines 77-80)**
   - **Chunk size: 1000 tokens**
     - Why: Balances context preservation with vector search relevance
     - Too small (100): Loses context meaning
     - Too large (5000): Reduces search precision
   - **Overlap: 200 tokens**
     - Why: Preserves semantic continuity across chunks
     - Ensures related concepts aren't split

4. **Metadata Preservation (Line 83)**
   - **Why**: Tracks which guideline each chunk came from
   - Stores filename in `split.metadata["source"]`
   - Enables audit reports to cite specific guidelines

5. **Accumulation Strategy (Line 85)**
   - **Why**: Batches all PDFs before uploading
   - Uses `all_splits.extend()` to flatten chunks from all PDFs
   - Upload happens OUTSIDE for loop (not after each PDF)
   - Reason: More efficient; single vector store insertion

6. **Error Handling (Lines 87-88)**
   - **Why**: Individual PDF errors don't stop entire indexing
   - Catches and logs per-PDF errors
   - Continues processing remaining PDFs
   - Partial indexing is better than complete failure

7. **Batch Upload After Loop (Lines 90-101)**
   - **Why**: Upload all at once instead of incrementally
   - Reduces API calls (1 call instead of N calls)
   - Uses `vector_store.add_documents()` (plural) for batch insert
   - Logs final indexed chunk count for verification

### Design Decisions Rationale

| Decision | Why | Alternative | Why Not |
|----------|-----|-------------|---------|
| FAISS for vector storage | Free, local, fast similarity search | PostgreSQL pgvector | Adds DB dependency, MVP overhead |
| Mistral embeddings | Same vendor as LLM, free tier | OpenAI embeddings | Requires separate API key, paid |
| Pre-computed indexing script | One-time setup; fast queries in audit | On-the-fly indexing | Slow during audit, repeated computation |
| Outside loop upload | Single batch insert | Inside loop upload | N times slower, inefficient |
| Metadata tracking | Audit trail; cite specific guidelines | No tracking | Audit reports can't reference source |

### Error Scenarios & Recovery

| Scenario | Handling |
|----------|----------|
| Missing `MISTRAL_API_KEY` | Logs warning, continues to attempt FAISS setup |
| Corrupt PDF | Logged and skipped; other PDFs continue processing |
| FAISS initialization fails | Logs error; script exits with status |
| API rate limit hit during embeddings | Exception caught, logged, script warns user |

### Future Enhancements

1. **Support other formats**: Docx, TXT, CSV (extend fileglob pattern)
2. **Scheduled re-indexing**: Update vector store with new guidelines
3. **Index versioning**: Track which guidelines were indexed when
4. **Feedback loop**: Update embeddings based on audit results

---

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
