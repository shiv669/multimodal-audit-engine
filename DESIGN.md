# Design Notes

## Project Overview

Multimodal-audit-engine scans video content across multiple streams—speech, on-screen text, and visuals—to detect compliance violations and flag misleading claims.

## Current Progress

### Setup Complete
- Python 3.13+ project initialized with `uv` package manager
- Git repository configured and linked to GitHub remote
- Basic project structure in place (main.py, pyproject.toml, README.md)

### Core Conceptual Understanding
- Violations can originate from multiple modalities or inconsistencies between them
- Pipeline approach: Ingestion → Extraction → Analysis → Correlation → Reporting
- Each modality requires specialized analysis (audio transcription, text extraction, visual understanding)

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
