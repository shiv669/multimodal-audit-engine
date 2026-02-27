# Multimodal Video Compliance Engine

## What This Project Does

This is a production-ready system that automatically analyzes YouTube videos against company compliance guidelines. You provide a YouTube link, and the system downloads the video, extracts everything said and written on screen, analyzes it against your compliance rules, and produces a detailed report indicating whether the video complies or lists specific violations.

The system handles the entire workflow: downloading the video directly from YouTube, extracting audio and converting it to text through speech recognition, extracting any visible text overlays or graphics from the video frames, comparing this content against compliance guidelines, and generating a clear pass or fail determination with detailed violation descriptions.

## Why This Approach

Most compliance checking systems require expensive cloud subscriptions to services like Azure Video Analyzer or AWS Rekognition. This system uses only free services: Mistral AI free tier for language processing, Whisper for speech recognition, Tesseract for optical character recognition, and FAISS for local vector search. The entire system costs nothing to run.

I deliberately chose open source and free services because they are production-ready for this use case, well-tested, and reliable. The system can analyze any YouTube video without rate limiting concerns. You maintain complete control over your compliance rules and audit data.

## Architecture Overview

The system operates as a three-stage pipeline:

Stage 1 downloads the video from YouTube and extracts raw content. It transcribes all speech to text using Whisper, then samples video frames and extracts any visible text using Tesseract OCR.

Stage 2 compares this extracted content against compliance guidelines. It uses semantic similarity search to find relevant rules from your compliance documents, then passes both the video content and the matched rules to an LLM with a detailed analysis prompt.

Stage 3 returns results. The LLM identifies specific violations, categorizes them, assigns severity levels, and provides explanations. The system displays these results immediately through either a command line interface or web interface.

This architecture is resilient. If a video has no audio, transcription produces empty text and the analysis continues. If a video has no visible text, OCR produces empty results and analysis continues. No component failure stops the entire system.

## Prerequisites

You will need the following software installed on your system:

1. Python version 3.12 or newer. Download from python.org if not already installed.

2. Git version control system for cloning the repository. Download from git-scm.com.

3. FFmpeg multimedia framework for video processing. On Windows, download from ffmpeg.org. On Mac, use Homebrew by running "brew install ffmpeg". On Linux, use your package manager such as "apt-get install ffmpeg".

4. Tesseract OCR engine for text extraction from images. On Windows, download the installer from GitHub (UB-Mannheim/tesseract/releases). On Mac, use "brew install tesseract". On Linux, use "apt-get install tesseract-ocr".

5. Two API keys for free services. Create a Mistral API key at console.mistral.ai (free tier includes substantial usage). Optionally, create a LangSmith API key at smith.langchain.com for debugging and tracing, though this is optional.

6. A YouTube URL to audit. The system analyzes any public YouTube video up to 5 minutes in length.

All of these are free to install and free to use. No credit card required for FFmpeg or Tesseract. Free tier Mistral includes hundreds of API calls per month.

## Getting Started

Step 1: Clone the Repository

Open your terminal or command prompt and run:

git clone https://github.com/shiv669/multimodal-audit-engine.git
cd multimodal-audit-engine

Step 2: Set Up Python Environment

Create a Python virtual environment to isolate project dependencies. Run:

python -m venv venv

Activate the virtual environment. On Windows, run:

venv\Scripts\activate

On Mac and Linux, run:

source venv/bin/activate

Step 3: Install System Dependencies

Install FFmpeg and Tesseract for your operating system using the instructions from the prerequisites section.

For Windows, after installing Tesseract, make sure it is in your system PATH. Verify by opening a new command prompt and running "tesseract --version". You should see version information displayed.

Step 4: Set Environment Variables

Create a file named .env in the project root directory with the following content:

MISTRAL_API_KEY=your_mistral_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here

Replace "your_mistral_api_key_here" with your actual Mistral API key obtained from console.mistral.ai. The LangSmith key is optional but useful for debugging.

Step 5: Install Python Dependencies

While your virtual environment is activated, run:

pip install -e .

This installs all project dependencies specified in pyproject.toml. Installation takes 2 to 5 minutes depending on your internet connection and system speed.

Step 6: Index Compliance Guidelines

Before running your first audit, you must index your compliance rules so the system can search them. Place PDF files containing your compliance guidelines in the backend/data/ directory. Then run:

python backend/scripts/index_documents.py

This processes all PDF files, extracts text, splits it into logical chunks, embeds the text into vectors using Mistral embeddings, and stores them in a FAISS index for fast searching during audits. You will see output showing how many chunks were created and indexed. On first run, this downloads the Mistral embedding model which takes about 2 minutes.

Step 7: Run an Audit

You can now run audits through either the command line interface or the web interface.

For the command line interface, run:

python main.py

The system will prompt you for a YouTube URL. Enter a URL like "https://www.youtube.com/watch?v=VIDEO_ID". The system downloads the video, extracts content, analyzes it, and displays a compliance report showing pass or fail status with detailed violation information.

For the web interface, run:

streamlit run frontend.py

A browser window opens automatically showing a web interface. You can enter a YouTube URL, validate video duration, then start an audit. The interface displays results in a structured, readable format.

## How to Use the System

### Using the Command Line Interface

Run "python main.py". The system asks for a YouTube video URL. Provide the full URL starting with https. The system then:

1. Downloads the video (this takes 30 to 60 seconds depending on video length and your internet connection)
2. Extracts transcript from audio (this takes 20 to 90 seconds on CPU without GPU)
3. Extracts text from video frames (this takes 10 to 30 seconds if video has visible text)
4. Analyzes content against compliance rules (this takes 10 to 20 seconds)
5. Outputs a compliance report showing pass or fail status

The report displays the video ID that was analyzed, the final pass or fail determination, a list of any violations with category, severity, and description, and a summary explaining the compliance status.

### Using the Web Interface

Run "streamlit run frontend.py". A web browser opens showing the interface.

Enter a YouTube URL in the text field and click the "Check Video" button. The system validates that the video exists and is not longer than 5 minutes. If valid, you will see a "Start Audit" button appear. If invalid, an error message explains why (for example, "Video too long" or "Invalid URL").

Click "Start Audit" to begin analysis. A spinner shows "Running compliance audit..." while processing. After 1 to 3 minutes depending on video length, results display including pass or fail status, detailed violation information, and an audit summary.

The system enforces rate limits: each user can audit maximum 5 videos per day. If you exceed this limit, an error message indicates how many audits remain today.

## System Behavior and Output

### Successful Compliance

If the audio and visible text in the video do not violate any compliance rules, the system outputs a pass determination. You see the message "Compliance Status: PASS" along with a summary like "This video complies with all company guidelines. No violations detected."

### Compliance Violations

If violations are detected, the system outputs a fail determination. You see "Compliance Status: FAIL" followed by a list of violations. Each violation includes:

Category: The type of rule violated, such as "Policy Violation", "Content Safety", "Brand Guidelines", or "Disclosure Requirements".

Severity: How serious the violation is. Critical means immediate action required. High means significant issue. Medium means notable but less urgent. Low means minor issue.

Description: Explanation of what content violated the rule and why it matters.

For example, you might see:

Category: Policy Violation
Severity: High
Description: Video contains discussion of confidential product roadmap without proper disclaimer.

### Empty or Minimal Content

If the video has no audio or no visible text, the system handles this gracefully. It analyzes whatever content is present and may output a pass (if present content complies) or note that insufficient content exists for thorough compliance checking.

## Rate Limiting

The system enforces usage limits to prevent excessive API calls:

Daily limit: Each unique user ID can audit maximum 5 videos per 24-hour period. The system tracks usage in a JSON file and resets counts daily.

Video length limit: Videos longer than 5 minutes are rejected during validation. This prevents excessive processing of long content. You can change this limit in frontend.py if needed.

These limits are enforced automatically and prevent accidentally exceeding free API quotas.

## Compliance Rule Customization

Your compliance rules are stored as PDF files in the backend/data/ directory. To add or modify rules:

1. Create PDF documents containing your compliance guidelines, company policies, brand guidelines, or other rules you want to enforce.

2. Place these PDF files in the backend/data/ directory.

3. Run "python backend/scripts/index_documents.py" to process the PDFs and update the compliance rule index.

4. Run audits normally. The system now uses the updated rules.

You can add multiple PDF files. The system processes all of them together and makes their content available for compliance checking. Rules are referenced by semantic similarity, meaning the system finds rules conceptually related to the video content rather than exact keyword matches.

## Troubleshooting

If you encounter problems, this section explains common issues and solutions.

Issue: ImportError when running main.py or frontend.py

Solution: Ensure your virtual environment is activated. Run "python main.py" again to confirm. If import errors persist, reinstall dependencies by running "pip install -e ." while the virtual environment is active.

Issue: "tesseract is not installed or it is not in your PATH"

Solution: Tesseract is installed but not accessible. On Windows, verify Tesseract is installed in the default location (C:\Program Files\Tesseract-OCR). If installed elsewhere, add its bin directory to your system PATH environment variable and restart your terminal.

Issue: "FFmpeg not found"

Solution: Similar to Tesseract, FFmpeg must be installed and in your system PATH. On Windows, install FFmpeg and ensure its bin directory is in your PATH. Run "ffmpeg -version" in a terminal to verify.

Issue: Video download fails with network error

Solution: Check your internet connection. Verify the YouTube URL is correct and points to a public video. Try again. YouTube sometimes limits or blocks automated downloads. If a specific video consistently fails, that video may have restrictions on automated access.

Issue: Transcription hangs or takes very long time

Solution: Whisper downloads a 140MB model on first run, which may take several minutes. Subsequent runs use the cached model and are faster. If transcription hangs beyond 10 minutes, the video may have very long audio. You can interrupt with Ctrl-C and try a shorter video.

Issue: LLM analysis returns parse errors

Solution: This occasionally happens when the LLM returns responses in an unexpected format. The system includes fallback parsing logic and should eventually succeed. If errors persist, verify your Mistral API key is correct and has not exceeded free tier limits.

## Architecture and Design

This section provides technical details for developers.

The system uses LangGraph, a state-driven orchestration framework, to build a directed acyclic graph (DAG) representing the pipeline. Each stage is a node that receives state, processes it, and returns modified state.

VideoIndexNode handles extraction. It calls VideoIndexerService to download videos from YouTube using yt-dlp, transcribe audio using Whisper, and extract text from frames using Tesseract OCR. It returns video metadata, transcript, and OCR results added to the state.

AuditContentNode handles compliance analysis. It loads a Mistral LLM and embeddings model, searches the FAISS vector database for compliance rules most relevant to the video content, and sends the extracted content plus matched rules to the LLM for analysis. The LLM returns violations in structured JSON format.

VideoIndexerService is a utility class that handles the details of video downloading, transcription, and OCR. It abstracts these details from the main nodes, making them testable independently and easily replaceable.

The compliance rule indexing process, run by index_documents.py, loads all PDFs from backend/data/, extracts text, splits into 1000-token chunks with 200-token overlap, embeds each chunk using Mistral embeddings, and stores embeddings in a FAISS vector index on disk.

Error handling is pervasive. Nodes return state dictionaries and accumulate errors in a state field. They never raise exceptions. If extraction fails, the node returns empty transcript and OCR. If LLM analysis fails, the node returns fail status. This design ensures the entire pipeline completes even if individual components experience failures.

The frontend uses Streamlit to provide a web interface. Streamlit runs on localhost:8501 by default. It validates user input, enforces rate limits, and calls the LangGraph workflow synchronously, displaying results upon completion.

## Performance Characteristics

Video download: 30 to 60 seconds for a 5-minute video depending on YouTube network conditions and your connection speed.

Whisper transcription: 20 to 90 seconds for a 5-minute video on CPU. Faster with GPU acceleration.

Tesseract OCR: 10 to 30 seconds depending on how much visible text the video contains. Samples every 10th frame to balance accuracy and speed.

LLM analysis: 10 to 20 seconds for running compliance check with Mistral LLM and semantic search.

Total end-to-end time: 1 to 3 minutes for a 5-minute video depending on content complexity and system specifications.

## Deployment Options

### Local or Single-Server Deployment

This system is designed for local or small-team deployment. The CLI and web interfaces run on your local machine or a single server. To scale to production with multiple users accessing simultaneously, consider these options:

1. Wrap the workflow in a FastAPI application to expose it as a REST API. Multiple requests can be queued and processed.

2. Deploy the system in Docker containers using the provided Dockerfile and docker-compose.yml configuration.

3. Replace the JSON-based rate limiting with a database to handle concurrent access cleanly.

4. Add a results database to store audit history and results for later analysis.

5. Implement a task queue (like Celery) to handle long-running audits asynchronously when accessed via REST API.

The architecture supports all these extensions without major changes to existing code.

### AWS EC2 Deployment (Free Tier)

This system has been successfully deployed on AWS EC2 using the free tier instance.

**Live Deployment URL:**
```
will be shared soon...
```

**Deployment Configuration:**
- Instance: AWS EC2 t2.micro (1GB RAM - free tier eligible)
- Operating System: Ubuntu 22.04 LTS
- Storage: 19GB EBS volume
- Python: 3.12
- Framework: Streamlit (listening on port 8501)

**Deployment Steps:**

1. Launch an Ubuntu 22.04 LTS EC2 instance (t2.micro for free tier)
2. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3.12 python3.12-venv python3-pip git ffmpeg tesseract-ocr
   ```
3. Clone the repository and set up virtual environment
4. Install Python dependencies: `pip install -e .`
5. Configure environment variables in .env file
6. Index compliance guidelines: `python backend/scripts/index_documents.py`
7. Start Streamlit: `streamlit run frontend.py --server.port=8501 --server.address=0.0.0.0`
8. Open AWS Security Group and add inbound rule for port 8501
9. Access via public IP at `http://[public-ip]:8501`

**Current Limitations of Live Deployment:**

1. **YouTube Download Restrictions**: YouTube's anti-bot protection currently blocks automated video downloads via yt-dlp on AWS, even with configuration workarounds applied. This is a YouTube security measure, not an application limitation. Workarounds:
   - Test with non-YouTube videos (e.g., direct MP4 URLs)
   - Submit YouTube cookies extracted from a logged-in browser session
   - Use videos that don't have bot protection enabled

2. **Video Input Validation**: The application currently validates that URLs contain "youtube.com" or "youtu.be". To support other video sources, set `local_file_path` to a direct video URL or upload a local file.

3. **Storage Constraints**: Free tier instances have limited storage (19GB). The system uses roughly:
   - 2GB for Python virtual environment and packages
   - 500MB for Whisper model (cached after first run)
   - 300MB for system dependencies
   - Remaining space for video processing (temporary files are cleaned up after processing)

4. **Performance**: Whisper transcription on t2.micro without GPU is slower (20-90 seconds for 5-minute videos). This is acceptable for free tier but not production.

5. **Concurrent Users**: Single instance can handle one audit at a time. Multiple simultaneous requests queue and process sequentially.

6. **Persistence**: Audit history is not persisted. Restarts clear the rate limiting counter and any in-progress requests.


**Testing Without YouTube Downloads:**

Use this direct video URL to test the full pipeline without YouTube restrictions:
```
https://archive.org/download/BigBuckBunny_124/Content/big_buck_bunny_720p_surround.mp4
```

However, note that the current code validates for YouTube URLs. To test with non-YouTube URLs, temporarily modify the validation in frontend.py (line checking for "youtube.com" or "youtu.be").

## License and Contributing

This project is open source. Feel free to modify it for your needs. If you make improvements you think others would benefit from, consider submitting a pull request.

## Questions and Support

Consult DESIGN.md for detailed technical documentation about system architecture, the complete development journey including all issues encountered and how they were solved, and design rationale for key decisions.

For questions about using the system, check the troubleshooting section above. For detailed architecture questions, read DESIGN.md.
