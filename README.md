# Multimodal Audit Engine

A video compliance auditing system that analyzes speech, text overlays, and visual elements to detect misleading claims and flag violations against compliance guidelines.

## Quick Summary

- Downloads YouTube videos automatically
- Extracts speech transcripts using Whisper
- Extracts on-screen text using Tesseract OCR
- Performs RAG-based compliance checking against your guidelines
- Reports pass/fail status with detailed violation descriptions
- Completely free (Mistral AI free tier + open-source tools)

## Installation & Setup

### Prerequisites

- Python 3.13 or higher
- Windows, macOS, or Linux
- Internet connection for API calls and video downloads
- Tesseract OCR installed on your system

### Step 1: Clone Repository

```bash
git clone https://github.com/shiv669/multimodal-audit-engine.git
cd multimodal-audit-engine
```

### Step 2: Create Python Virtual Environment

```bash
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install langchain-core langchain-community langchain-mistralai yt-dlp pypdf langchain-text-splitters python-dotenv fastapi uvicorn langsmith langgraph faiss-cpu opencv-python openai-whisper pytesseract
```

### Step 4: Install Tesseract OCR

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (keep default path: C:\Program Files\Tesseract-OCR)
3. Verify installation: Open PowerShell and run `tesseract --version`

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### Step 5: Get Free API Keys

**Mistral API Key:**
1. Go to https://console.mistral.ai
2. Sign up for free account (no credit card required)
3. Create API key
4. Copy your MISTRAL_API_KEY

**LangSmith API Key:**
1. Go to https://smith.langchain.com
2. Sign up for free account
3. Create API key
4. Copy your LANGSMITH_API_KEY

### Step 6: Create .env File

```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```
MISTRAL_API_KEY=your_mistral_key_here
LANGSMITH_API_KEY=your_langsmith_key_here
```

### Step 7: Add Compliance PDFs

1. Create folder: `backend/data/`
2. Add your compliance guideline PDFs here
3. Examples: FDA regulations, FTC standards, industry guidelines, terms of service

The system will automatically extract, chunk, and index these PDFs.

### Step 8: Build Vector Index

Before running audits, index your compliance PDFs:

```bash
python backend/scripts/index_documents.py
```

Expected output:
```
INFO - MISTRAL_API_KEY is set
INFO - LANGSMITH_API_KEY is set
INFO - found 2 to process: ['guideline1.pdf', 'guideline2.pdf']
INFO - uploading 37 to mistral ai embeddings
INFO - ============================================================
INFO - indexing completed knowledge base ready !
INFO - total number of chunks indexed : 37
INFO - vector store saved to disk at backend/data/faiss_index
```

### Step 9: Run Your First Audit

```bash
python main.py
```

Expected output:
```
2026-02-14 12:00:00 - INFO - starting the audit report for: <session-id>
initialsing the workflow
input payload : {
  "video_url": "https://youtu.be/...",
  "video_id": "vid_xxxxxxxx",
  ...
}

workflow execution is completed

compliance audit report
video id: vid_xxxxxxxx
final status: pass/fail

violations detected
- [critical] claim validation: Description of violation
- [high] medical claim: Another violation found
...

final summary
Found X compliance violations. Review before publishing.
```

## How It Works

### Pipeline Architecture

```
YouTube URL
    ↓
yt-dlp downloads video
    ↓
Whisper extracts audio transcript
    ↓
Tesseract extracts on-screen text (OCR)
    ↓
Mistral creates embeddings for text
    ↓
FAISS vector store retrieves similar compliance rules
    ↓
Mistral LLM analyzes transcript against rules
    ↓
System reports pass/fail with violation details
```

### State Flow

1. **Initial State**: video_url and video_id provided
2. **Extraction Phase**: videoIndexNode downloads, transcribes, extracts OCR
3. **Analysis Phase**: audit_content_node loads compliance rules, performs RAG analysis
4. **Output Phase**: Final state includes audit_result (pass/fail), compliance_result (violations), audit_report (summary)

### Error Handling

- Missing video: Caught and logged, audit marked as failed
- No transcript: Caught and logged, audit marked as skipped
- OCR extraction errors: Logged, processing continues with partial results
- API failures: Caught and reported, errors accumulate in state
- All errors non-fatal; pipeline completes with results

## Project Structure

```
multimodal-audit-engine/
├── main.py                          # Entry point, orchestrates pipeline
├── pyproject.toml                   # Python dependencies
├── .env.example                     # Template for environment variables
├── README.md                        # This file
├── DESIGN.md                        # Detailed architecture documentation
│
├── backend/
│   ├── data/                        # Compliance PDFs and vector index
│   │   ├── your_guidelines.pdf      # Add your PDFs here
│   │   └── faiss_index/             # Auto-generated vector store
│   │
│   ├── scripts/
│   │   └── index_documents.py       # PDF indexing script
│   │
│   └── src/
│       ├── graphs/
│       │   ├── state.py             # videoState and complianceIssue TypedDicts
│       │   ├── nodes.py             # videoIndexNode and audit_content_node
│       │   └── workflow.py          # LangGraph DAG orchestration
│       │
│       └── services/
│           └── video_indexer.py     # VideoIndexerService class
│
└── tests/                           # Test suite (planned)
```

## Configuration

### Modify Video URL

Edit `main.py` line 31:
```python
initial_inputs = {
    "video_url" : "https://youtu.be/YOUR_VIDEO_ID",  # Change this
    ...
}
```

### Adjust Video Sampling

Edit `backend/src/services/video_indexer.py` line 71:
```python
if frame_count % 10 == 0:  # Change 10 to sample more/fewer frames
    text = pytesseract.image_to_string(frame)
```

- Lower number = more frames analyzed = slower but more thorough
- Higher number = fewer frames = faster but might miss text

### Change Chunk Size

Edit `backend/scripts/index_documents.py` line 71:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,          # Tokens per chunk
    chunk_overlap = 200         # Overlap between chunks
)
```

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'xyz'`

**Fix**: Ensure virtual environment is activated and all dependencies installed:
```bash
pip install --upgrade pip
pip install -r requirements.txt  # If requirements.txt exists
```

Or reinstall all:
```bash
pip install langchain-core langchain-community langchain-mistralai yt-dlp pypdf langchain-text-splitters python-dotenv fastapi uvicorn langsmith langgraph faiss-cpu opencv-python openai-whisper pytesseract
```

### Tesseract Not Found

**Error**: `TesseractNotFoundError` or `pytesseract.TesseractNotFoundError`

**Fix**: Ensure Tesseract is installed and path is correct in `backend/src/services/video_indexer.py`:
```python
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
pytesseract.pytesseract.pytesseract_cmd = '/usr/bin/tesseract'  # Linux
pytesseract.pytesseract.pytesseract_cmd = '/usr/local/bin/tesseract'  # macOS
```

### API Key Issues

**Error**: `Authentication failed` or `Invalid API key`

**Fix**: 
1. Verify .env file exists and is readable
2. Check MISTRAL_API_KEY and LANGSMITH_API_KEY are correct
3. Ensure keys have necessary permissions in respective dashboards
4. Don't commit .env to git (it's in .gitignore)

### Vector Store Not Found

**Error**: `Could not load FAISS index`

**Fix**: Run PDF indexing script first:
```bash
python backend/scripts/index_documents.py
```

This creates vector store at `backend/data/faiss_index/`

### Video Download Fails

**Error**: `Failed to download video`

**Causes**: 
- Invalid YouTube URL
- Video is private or deleted
- Network connection issue
- Rate limiting from YouTube

**Fix**: Verify URL is public and accessible. Try different video. Check internet connection.

### Memory Issues

**Problem**: Script runs out of memory

**Fix**: Reduce sample rate in video_indexer.py or limit PDF size. Tesseract is memory-intensive for large PDFs.

## Performance

- First Whisper run: 2-5 minutes (downloads 140MB model)
- Subsequent runs: Use cached model
- PDF indexing: 37 chunks ~5 seconds
- FAISS search: ~100ms
- LLM analysis: 2-10 seconds depending on model load
- Total audit time: 5-15 minutes per video

## Tech Stack

- **Framework**: LangGraph, LangChain
- **LLM**: Mistral AI (free tier)
- **Embeddings**: Mistral AI embeddings
- **Vector Store**: FAISS (local, free)
- **Video Download**: yt-dlp
- **Transcription**: OpenAI Whisper
- **OCR**: Tesseract
- **Video Processing**: OpenCV
- **Debugging**: LangSmith
- **Environment**: Python 3.13+, FastAPI (planned)

## Deployment

###  Local Development
```bash
python main.py
```

### Docker Deployment (Planned)

```bash
docker build -t multimodal-audit-engine .
docker run -e MISTRAL_API_KEY=your_key -e LANGSMITH_API_KEY=your_key multimodal-audit-engine
```

## Contributing

Contributions welcome! Areas for improvement:
- API endpoint instead of CLI
- Batch processing multiple videos
- Custom LLM fine-tuning
- Visual anomaly detection
- Multi-language support
- GPU acceleration

## License

MIT License - see LICENSE file

## Support

For issues, bugs, or questions:
1. Check DESIGN.md for architecture details
2. Review error messages in logs
3. Check troubleshooting section above
4. Open GitHub issue with error stack trace

## Roadmap

- Week 1: Dockerize application
- Week 2: REST API with FastAPI
- Week 3: Batch processing and job queue
- Week 4: Webhook notifications
- Month 2: AWS Lambda deployment
- Month 3: GPU acceleration with CUDA
- Month 4: Multi-language support
- Month 6: Visual anomaly detection
