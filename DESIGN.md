# Multimodal Video Compliance Engine - Complete Development Journey

## Project Origin and Vision

The goal was to build a production-ready system that could analyze YouTube videos for compliance violations against company guidelines. Instead of using expensive proprietary services like Azure Video Indexer or AWS Rekognition, we built a system using entirely free services: Mistral AI for language processing, Whisper for speech recognition, Tesseract for text extraction, and FAISS for vector search. The entire system operates without recurring infrastructure costs.

## Architecture Overview

The system processes videos through a state-driven pipeline orchestrated by LangGraph. Each stage transforms the video into structured data: first extraction of raw content (transcript and text overlays), then semantic analysis against compliance rules using retrieval-augmented generation. The pipeline is resilient to individual component failures, continuing with partial results rather than crashing.

State flows through these stages: video download from YouTube, audio transcription via Whisper, visual text extraction via Tesseract OCR, embedding generation via Mistral, similarity search against compliance rules via FAISS, and final LLM-powered analysis.

## Development Journey - Phase by Phase

### Phase 1: Initial Setup and Environment Configuration

We started with a basic Python project structure using the uv package manager. The immediate challenge was setting up a clean development environment. We created a virtual environment to isolate dependencies, then configured environment variables for the Mistral API and LangSmith tracing service.

Mistake made: Initially tried using global Python packages instead of the virtual environment. This led to conflicts between globally installed packages and project requirements. Fixed by strictly using the virtual environment for all installation and execution.

Decision made: Chose uv over pip for faster dependency resolution. This proved helpful when debugging complex dependency trees later.

### Phase 2: Architecture Design with LangGraph State Management

Rather than building a simple function-based pipeline, we adopted LangGraph's StateGraph pattern. This required defining a strict state contract using TypedDict for type safety. We defined two core data structures:

videoState tracks the complete lifecycle of a single audit: input parameters (video_url, video_id), intermediate extraction results (local_file_path, video_transcript, ocr_text), analysis results (compliance_result containing violation objects), final output (audit_result as pass/fail, audit_report as summary text), and accumulated errors.

complianceIssue defines each violation with category (what rule was violated), description (explanation of the violation), severity (critical/high/medium/low), and timestamp (when detected).

Mistake made: Initially underestimated how many fields the state would need. We had to add local_file_path, video_metadata, and error fields after discovering the pipeline needed them midway through development.

Decision made: Used Annotated[List, operator.add] for error accumulation. This creates an implicit list concatenation when nodes return errors, ensuring no error is lost even when multiple nodes fail.

### Phase 3: Building the Extraction Pipeline with videoIndexNode

The first node handles raw data extraction. It downloads videos from YouTube using yt-dlp, validates URLs, and passes the video to the extraction service.

Mistake made: Initially, the download configuration passed the filename with .mp4 extension to yt-dlp's outtmpl parameter, then stripped it away with a replace operation. This caused yt-dlp to save the file without the extension, leading to file not found errors downstream when Whisper and OpenCV couldn't locate the video.

Fix: Changed the outtmpl to preserve the filename exactly as specified. This required understanding yt-dlp's filename template system and how it handles format codes.

Decision made: Separated the download logic into a dedicated VideoIndexerService class. This abstraction lets us test the download logic independently, swap implementations later (for example, switch to direct file upload instead of YouTube downloads), and keep the LangGraph node focused on orchestration.

### Phase 4: Building the Extraction Service with VideoIndexerService

The VideoIndexerService contains three methods:

download_youtube_video handles yt-dlp configuration, selecting the best available format as MP4, and returns the local file path. Error handling lets us catch network issues or invalid URLs gracefully.

extract_video_data is where the heavy lifting happens. It loads the Whisper model (140MB on first run, cached after that), transcribes the entire audio track to text, then opens the video file with OpenCV, samples every 10th frame, and runs Tesseract OCR on each sampled frame. The frame sampling balances speed against completeness: sampling every frame would be accurate but slow, while sampling too sparsely might miss visible text overlays.

extract_data normalizes the results to match the state schema, ensuring downstream nodes receive data in expected format.

Mistake made: Downloaded Whisper model with FP16 precision, which failed on CPU-only systems. Whisper automatically fell back to FP32 with a warning, but this caused on-system with no GPU to run extremely slowly.

Learning: Always consider target deployment environment when selecting model precision. For CPU-only systems, FP32 is necessary despite being slower.

### Phase 5: Compliance PDF Indexing and Vector Store Creation

Before any audit can run, the system must have compliance guidelines indexed. We built index_documents.py to handle this preprocessing step.

Mistake made: Initially created the FAISS vector store at module level before loading any documents, passing an empty list. When the script tried to add actual documents later, FAISS threw cryptic errors because you cannot add documents to an already-initialized empty index.

Fix: Moved FAISS initialization inside the function, after verifying documents exist. This gives us an empty list error (clear) instead of an incompatible index error (cryptic).

Another mistake: Called vector_store.add_documents() inside a for loop, once per document chunk. With 37 chunks, this generated 37 separate API calls to Mistral, each waiting for a response. This was inefficient.

Fix: Collected all chunks into a single list, then called FAISS.from_documents() once with all chunks. This reduced API calls from 37 to 1, making indexing roughly 37 times faster.

Decision made: Store the FAISS vector index to disk via save_local(). This lets the audit pipeline load the pre-computed index without re-embedding on every run. The trade-off: requires a preprocessing step before running audits, but makes individual audits much faster.

### Phase 6: Building the Compliance Analysis Node

The audit_content_node performs RAG analysis. It initializes the Mistral LLM and embeddings, loads the FAISS vector store from disk, combines the transcript and OCR text into a search query, retrieves the top-3 similar compliance rules, and sends everything to the LLM with a detailed system prompt.

The LLM analyzes whether the transcript/text violates any rules and returns structured JSON containing violations, pass/fail status, and summary.

Mistake made: Used FAISS.load_local() without the allow_dangerous_deserialization parameter. LangChain raised an exception with a lengthy warning about pickle security, even though the vector store was created locally by our own script.

Fix: Added allow_dangerous_deserialization=True flag. For locally-created stores that you control, this is safe and necessary.

Another mistake: Passed video_metadata to the LLM in an f-string with double braces like {state.get('video_metadata',{{}})}. Python treated these as escaped braces meant for output, causing unhashable type errors when the f-string tried to parse the dict literal syntax.

Fix: Changed to single braces {state.get('video_metadata',{})} which meant a blank dict in the f-string.

### Phase 7: Orchestration with LangGraph Workflow

The workflow.py file assembles everything into a DAG. We define a StateGraph with videoState as the contract, add two nodes (videoIndexNode and audit_content_node), set the entry point to videoIndexNode, add edges (videoIndexNode -> audit_content_node -> END), and compile the graph.

The compiled app object handles state passing between nodes automatically. When videoIndexNode returns a dict, LangGraph merges those fields into the state. When audit_content_node gets invoked, it receives the merged state as input.

Decision made: Sequential pipeline for MVP, designed for easy parallelization. LangGraph could schedule both transcript extraction and OCR in parallel, making audits faster. This architecture change requires no code changes to individual nodes, just routing changes in workflow.py.

### Phase 8: System Dependencies and Environment Issues

We encountered multiple missing system dependencies that caused cryptic runtime errors.

FFmpeg missing: Whisper uses FFmpeg internally to decode video to audio. Without it, transcription failed with WinError 2 (file not found). We discovered FFmpeg was already installed by MiniTool MovieMaker at a non-standard path, added its bin directory to the system PATH.

Tesseract missing: pytesseract couldn't find the Tesseract executable despite it being installed. The issue was that Tesseract wasn't in the system PATH. After adding C:\Program Files\Tesseract-OCR to PATH and restarting the terminal, it worked.

Package installation confusion: Streamlit and other tools were installing to global Python instead of the virtual environment. Tracked the issue to multiple Python interpreters being available. Fixed by ensuring the virtual environment was activated before any pip install commands, and using `python -m pip install` to force pip to use the current Python executable's environment.

### Phase 9: API Compatibility and Dependency Management

When we upgraded langchain and related packages, the API changed:

MistralEmbeddings class was renamed to MistralAIEmbeddings. ChatMistral became ChatMistralAI. These changes broke existing code that imported the old class names.

Rather than pinning old versions, we updated all imports across index_documents.py and nodes.py to use the new class names. This is better long-term because we get bug fixes and improvements from newer versions.

Decision made: Specification requires-python>=3.12 instead of 3.13 after discovering the system used Python 3.12. The project works equally on both versions.

### Phase 10: Rate Limiting for the Web Interface

When building the Streamlit frontend, we needed to enforce usage limits: maximum 5 minute videos and 5 audits per user per day.

Duration validation queries video metadata via yt-dlp extract_info without actually downloading, checking the duration field quickly.

Rate limiting stores user activity in backend/data/rate_limit.json with a simple structure: user_id, current date, and audit count. Before allowing an audit, we check if today's count exceeds the limit. If not, we increment and save.

Decision made: JSON file instead of database for simplicity. This works great for single-instance deployments. Multi-instance deployments would need a database with locking to prevent race conditions.

### Phase 11: Streamlit Web Interface Implementation

The frontend provides a user-friendly alternative to the CLI. Users enter a YouTube URL, the system validates duration and rate limits, then runs the audit and displays results.

Mistake made: Nested the start audit button inside the check video button block. When users clicked start audit, Streamlit reran the script but the check video button wasn't pressed, so that entire code block was skipped and start audit was never evaluated.

Fix: Moved the start audit button outside the check video block. Now both buttons persist independently. Used streamlit.session_state to track state across page reruns: video_checked tells us if validation passed, ready_to_audit tells us to start processing.

The UI flow: enter URL -> click Check Video -> validation happens, Start Audit button appears -> click Start Audit -> audit runs with spinner -> results displayed.

### Phase 12: Integration and Testing

We tested end-to-end by running CLI (python main.py) and web interface (streamlit run frontend.py) against sample YouTube videos.

Test results: video downloads succeeded, transcription succeeded for videos with audio, OCR succeeded for videos with on-screen text, LLM analysis correctly parsed violations from compliance guidelines, rate limiting correctly blocked excessive requests, summary reports displayed properly.

Error handling confirmed: when transcript was empty, the audit gracefully returned fail status instead of crashing. When OCR found no text, the analysis continued with empty OCR results instead of erroring.

## Lessons from Production Development

Build around failures, not just successes. Every node returns state, never raises exceptions. Errors accumulate but the pipeline completes. This resilience means missing transcript or empty OCR don't crash the entire system.

Free services are production-ready. Mistral free tier handled our workload easily. FAISS vector search is genuinely fast for small to medium rule sets. Whisper transcription on CPU takes time but works correctly. The total cost is zero.

Batch operations matter. Processing 37 chunks at once instead of one by one made our indexing roughly 37 times faster. Any time you're in a loop hitting an API, ask yourself if you can batch.

State machines prevent subtle bugs. LangGraph's explicit state transitions and TypedDict validation catch mismatched field names at development time. You can't accidentally forget to return a field or misspell a key.

Environment isolation is essential. Virtual environments prevent package conflicts that take hours to debug. Clear PATH configuration prevents hours searching for why an executable isn't found.

Free doesn't mean infinite. Rate limiting was necessary to prevent abuse of the free Mistral API. Our 5 audits per day limit is conservative but protects against runaway usage.

## System Status

The system is fully operational. It correctly downloads videos, extracts transcripts and text overlays, performs compliance analysis, and produces accurate audit reports. It provides both CLI and web interfaces. Setup is automated via single pip install command. Code is production-ready with error handling throughout.

The architecture is extensible. Parallel extraction (transcript and OCR simultaneously), batch processing (audit multiple videos), and REST API endpoints can all be added without changing existing components. Database persistence can replace JSON rate limiting. More sophisticated LLMs can replace Mistral without changing node structure.

## Technical Debt and Future Work

Future improvements: implement REST API wrapper using FastAPI, add database persistence for audit history, add support for private videos and livestreams, implement webhook notifications, add GPU acceleration for Whisper on high-volume deployments, support multi-language compliance rules, add custom model fine-tuning for specific industries.

