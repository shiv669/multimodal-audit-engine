# Multimodal Audit Engine

Video compliance auditing system analyzing speech, text overlays, and visual elements to detect misleading claims and flag compliance violations. Completely free using Mistral AI free tier.

## Features

Download YouTube videos automatically. Extract speech transcripts using Whisper. Extract on-screen text using Tesseract OCR. Perform RAG-based compliance checking against your guidelines. Report pass/fail status with detailed violation descriptions.

## System Requirements

Python 3.13 or higher. Windows, macOS, or Linux. Internet connection for API calls and video downloads.

## Complete Setup Guide

### Step 1: Clone Repository

git clone https://github.com/shiv669/multimodal-audit-engine.git
cd multimodal-audit-engine

### Step 2: Create Virtual Environment

Windows:
python -m venv .venv
.venv\Scripts\activate

macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate

### Step 3: Install Python Dependencies

pip install --upgrade pip
pip install -e .

This installs all dependencies from pyproject.toml: langchain-core, langchain-community, langchain-mistralai, yt-dlp, pypdf, langchain-text-splitters, python-dotenv, fastapi, uvicorn, langsmith, langgraph, faiss-cpu, opencv-python, openai-whisper, pytesseract.

### Step 4: Install FFmpeg

FFmpeg is required for Whisper to process video files.

Windows (if you have Chocolatey):
choco install ffmpeg

Windows (if you have Winget):
winget install --id FFmpeg.FFmpeg

Windows (Manual):
1. Download from https://www.gyan.dev/ffmpeg/builds/
2. Extract ffmpeg-release-essentials.zip to C:\ffmpeg
3. Add C:\Program Files\MiniTool MovieMaker\bin or C:\ffmpeg\bin to system PATH
4. Restart PowerShell
5. Verify: ffmpeg -version

macOS:
brew install ffmpeg

Linux (Ubuntu/Debian):
sudo apt-get install ffmpeg

### Step 5: Install Tesseract OCR

Tesseract is required for extracting on-screen text from video frames.

Windows:
1. Download from https://github.com/UB-Mannheim/tesseract/wiki
2. Run tesseract-ocr-w64-setup-v5.x.x.exe
3. Install to C:\Program Files\Tesseract-OCR (default)
4. Add C:\Program Files\Tesseract-OCR to system PATH
5. Restart PowerShell
6. Verify: tesseract --version

macOS:
brew install tesseract

Linux (Ubuntu/Debian):
sudo apt-get install tesseract-ocr

### Step 6: Get Free API Keys

Mistral API Key:
1. Go to https://console.mistral.ai
2. Sign up for free (no credit card required)
3. Create API key at https://console.mistral.ai/api-tokens/
4. Copy your MISTRAL_API_KEY

LangSmith API Key (optional, for debugging):
1. Go to https://smith.langchain.com
2. Sign up for free
3. Create API key
4. Copy your LANGSMITH_API_KEY

### Step 7: Configure Environment Variables

cp .env.example .env

Edit .env and add your keys:

MISTRAL_API_KEY=your_mistral_key_here
LANGSMITH_API_KEY=your_langsmith_key_here

### Step 8: Add Compliance Guideline PDFs

Create folder: backend/data/

Add your compliance guideline PDFs in this folder. Examples: FDA regulations, FTC guidelines, industry standards, company policies, terms of service.

The system will automatically extract, chunk, and index these PDFs into a vector store.

### Step 9: Index Compliance PDFs

Before running audits, build the vector index:

python backend/scripts/index_documents.py

You should see output like:

INFO - found 2 to process: ['guideline1.pdf', 'guideline2.pdf']
INFO - uploading 37 to mistral ai embeddings
INFO - indexing completed knowledge base ready
INFO - total number of chunks indexed : 37
INFO - vector store saved to disk at backend/data/faiss_index

### Step 10: Run Your First Audit

python main.py

The system will:
1. Download the YouTube video
2. Extract speech transcript using Whisper
3. Extract on-screen text using Tesseract OCR
4. Load compliance guidelines from vector store
5. Perform RAG analysis using Mistral LLM
6. Report pass/fail status with violation details

Expected output shows video ID, final status (pass/fail), violations detected with category, severity, and description, and final audit summary.

## How It Works

Pipeline Flow:
1. YouTube URL input
2. yt-dlp downloads video as MP4
3. Whisper extracts audio transcript
4. Tesseract extracts on-screen text via OCR on video frames
5. Mistral creates embeddings for transcript and OCR text
6. FAISS vector store retrieves top-3 matching compliance rules
7. Mistral LLM analyzes transcript and OCR against retrieved rules
8. System generates pass/fail verdict with violation details

State Transitions:
1. Initial state receives video_url and video_id
2. videoIndexNode extracts local_file_path, video_transcript, ocr_text
3. audit_content_node loads compliance rules and performs analysis
4. Final state contains audit_result (pass/fail), compliance_result (list of violations), audit_report (summary text)

Error Handling:
- Missing video or incorrect URL: caught and logged, audit marked failed
- Transcription failure: caught and logged, audit marked skipped
- OCR extraction errors: logged, processing continues with available data
- API failures: caught and logged in error accumulator
- All errors non-fatal, pipeline completes with partial results

## Customizing Compliance Rules

Replace or add PDFs in backend/data/ folder. Run index_documents.py to rebuild vector store. Each PDF is split into 1000-token chunks with 200-token overlap. Mistral embeddings create searchable vectors for similarity matching.

## Docker (Optional)

docker-compose up

This runs the system in a container with FFmpeg and Tesseract pre-installed, avoiding system dependency issues.

## Troubleshooting

FFmpeg not found: Add C:\Program Files\MiniTool MovieMaker\bin or C:\ffmpeg\bin to system PATH, then restart PowerShell.

Tesseract not found: Add C:\Program Files\Tesseract-OCR to system PATH, then restart PowerShell.

MISTRAL_API_KEY missing: Verify .env file exists and contains MISTRAL_API_KEY=your_key_here

Vector store errors: Run python backend/scripts/index_documents.py to rebuild FAISS index from PDFs

Video download fails: Check internet connection, verify YouTube URL is valid and public

Whisper/FFmpeg errors: Ensure FFmpeg is installed and in system PATH, restart terminal

Tesseract/OCR errors: Ensure Tesseract is installed at C:\Program Files\Tesseract-OCR and in PATH

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

## License

MIT License - see LICENSE file



