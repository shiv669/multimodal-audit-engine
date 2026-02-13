# Multimodal Audit Engine

A system that scans video content across multiple modalities—speech, on-screen text, and visuals—to detect compliance violations and flag misleading claims.

## Features

- **Audio Analysis**: Extracts and analyzes speech from video content
- **Text Extraction**: Identifies on-screen captions and overlays
- **Visual Understanding**: Processes key visuals and imagery
- **Compliance Checking**: Cross-references information across modalities to detect violations
- **Reporting**: Generates compliance reports with flagged violations

## Getting Started

```bash
# Install dependencies
python -m uv pip install -r requirements.txt

# Run the engine
python main.py
```


## Design Philosophy

- Build incrementally with real content validation
- Design for correctness first, speed second
- Make invalid states difficult to represent
- Document decisions and learnings transparently

See [DESIGN.md](DESIGN.md) for architectural notes and current progress.
