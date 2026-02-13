FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    langchain-core \
    langchain-community \
    langchain-mistralai \
    yt-dlp \
    pypdf \
    langchain-text-splitters \
    python-dotenv \
    fastapi \
    uvicorn \
    langsmith \
    langgraph \
    faiss-cpu \
    opencv-python \
    openai-whisper \
    pytesseract

# Create data directory for PDFs and vector index
RUN mkdir -p /app/backend/data

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1
ENV MISTRAL_API_KEY=""
ENV LANGSMITH_API_KEY=""

# Expose port for API (future)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command: index PDFs then run pipeline
CMD ["python", "main.py"]
