# Math Animation AI - Backend

FastAPI backend server for AI-powered math animation generation.

## Features

- 📸 Image upload and processing
- 🔍 Google Cloud Vision API integration (OCR)
- 🤖 AI code generation (OpenAI GPT-4 / Anthropic Claude)
- 🎬 Manim animation rendering
- 🌐 RESTful API endpoints
- ⚡ Fast and async processing

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Google Vision API** - OCR text extraction
- **OpenAI API** - GPT-4 for code generation
- **Anthropic API** - Claude (alternative)
- **ManimGL** - Animation rendering
- **Pydantic** - Data validation

## Installation

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
nano .env
```

Required keys:
- `GOOGLE_API_KEY` - Google Cloud Vision API
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - AI provider

### 4. Install ManimGL

```bash
cd ../manim
pip install -e .
```

## Running the Server

### Method 1: Using run.py (Recommended)

```bash
python3 run.py
```

### Method 2: Using uvicorn directly

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: http://localhost:8000

## API Documentation

Once the server is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Image Processing

- `POST /api/image/upload` - Upload and analyze image
- `POST /api/image/extract-text` - Extract text from image
- `POST /api/image/analyze` - Full image analysis

### Animation Generation

- `POST /api/animation/generate` - Generate Manim code from text
- `POST /api/animation/render` - Render animation from code
- `POST /api/animation/from-image` - Complete pipeline (image → animation)
- `POST /api/animation/explain` - Explain math problem
- `POST /api/animation/improve` - Improve existing code
- `POST /api/animation/validate` - Validate Manim code

### Utilities

- `GET /health` - Health check
- `GET /videos/{filename}` - Serve rendered videos

## Environment Variables

```env
# Google Cloud Vision API
GOOGLE_API_KEY=your-key-here

# AI Provider
AI_PROVIDER=openai  # or "anthropic"
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Server Settings
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000

# Manim Settings
MANIM_PATH=../manim
TEMP_DIR=./temp
VIDEO_QUALITY=medium  # low, medium, high
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── routers/
│   │   ├── image.py         # Image endpoints
│   │   └── animation.py     # Animation endpoints
│   ├── services/
│   │   ├── vision_service.py    # Google Vision
│   │   ├── ai_service.py        # OpenAI/Anthropic
│   │   └── manim_service.py     # Manim rendering
│   └── utils/
├── temp/                    # Temporary video files
├── venv/                    # Virtual environment
├── requirements.txt
├── .env                     # Your config (git-ignored)
├── .env.example            # Template
├── run.py                  # Server runner
└── README.md               # This file
```

## Development

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Upload image
curl -X POST -F "file=@test.jpg" http://localhost:8000/api/image/upload

# Generate code
curl -X POST http://localhost:8000/api/animation/generate \
  -H "Content-Type: application/json" \
  -d '{"math_text": "x^2 + 5x + 6 = 0"}'
```

### Viewing Logs

The server outputs logs to console. To save logs:

```bash
python3 run.py > server.log 2>&1 &
tail -f server.log
```

## Troubleshooting

### "GOOGLE_API_KEY not found"
- Check `.env` file exists
- Verify API key is correct
- Restart server after changing `.env`

### "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

### "Port already in use"
```bash
lsof -ti:8000 | xargs kill
```

### "Manim rendering failed"
- Check ManimGL installed: `manimgl --version`
- Check FFmpeg installed: `ffmpeg -version`
- Verify `MANIM_PATH` in `.env`
- Check write permissions on `temp/` directory

## Performance

- **Image upload**: < 1 second
- **OCR processing**: 1-3 seconds
- **Code generation**: 5-10 seconds
- **Video rendering**: 15-60 seconds (depends on complexity)
- **Total pipeline**: 30-90 seconds

## Security

- API keys stored in `.env` (git-ignored)
- CORS configured for frontend only
- File upload validation
- Temporary files auto-cleaned
- No persistent data storage

## Dependencies

See `requirements.txt` for full list:

- fastapi>=0.104.1
- uvicorn[standard]>=0.24.0
- python-dotenv>=1.0.0
- requests>=2.31.0
- openai>=1.3.0
- anthropic>=0.18.0
- Pillow>=10.1.0
- pydantic>=2.5.0

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature-name`
6. Create Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check documentation: `../README.md`, `../QUICKSTART.md`
- Open GitHub issue
- Check server logs

---

**Made with ❤️ for math education**