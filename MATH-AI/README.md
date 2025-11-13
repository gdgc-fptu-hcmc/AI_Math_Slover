# 🎓 Math Animation AI

AI-powered mathematical animation generator using Google Vision API, OpenAI/Anthropic, and Manim. Upload or capture photos of math problems and instantly create beautiful educational animations!

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 📸 **Image Upload & Camera Capture** - Upload images or use your webcam
- 🔍 **Google Vision OCR** - Automatic text extraction from images
- 🤖 **AI-Powered Code Generation** - GPT-4 or Claude generates Manim code
- 🎬 **Instant Animation** - Manim renders beautiful math animations
- 💬 **Chat Interface** - Intuitive ChatGPT-like UI
- ⚡ **Real-time Processing** - See results immediately

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│        React Frontend (Vite + Tailwind)         │
│  - Chat UI                                       │
│  - Image Upload/Camera                           │
│  - Video Player                                  │
└───────────────┬─────────────────────────────────┘
                │ REST API
                │
┌───────────────▼─────────────────────────────────┐
│            FastAPI Backend                       │
│  - Google Vision API (OCR)                       │
│  - OpenAI/Anthropic (Code Generation)            │
│  - Manim (Animation Rendering)                   │
└─────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Python 3.7+** (for backend)
- **Node.js 18+** (for frontend)
- **FFmpeg** (for Manim video rendering)
- **ManimGL** (3Blue1Brown version)

### API Keys Required

1. **Google Cloud API Key** - For Vision API (OCR)
2. **OpenAI API Key** OR **Anthropic API Key** - For AI code generation

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd MATH-AI
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install ManimGL

```bash
# Install ManimGL
cd ../manim
pip install -e .

# Verify installation
manimgl --version
```

### 4. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
cd ../backend
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Google Cloud Vision API Key
GOOGLE_API_KEY=your-google-api-key-here

# OpenAI API Key (recommended)
OPENAI_API_KEY=your-openai-api-key-here

# OR Anthropic API Key (alternative)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Which AI provider to use: "openai" or "anthropic"
AI_PROVIDER=openai

# Server settings
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000

# Manim settings
MANIM_PATH=../manim
TEMP_DIR=./temp

# Video quality (low, medium, high)
VIDEO_QUALITY=medium
```

### 5. Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install
```

## 🔑 Getting API Keys

### Google Cloud Vision API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Cloud Vision API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"
4. Create API Key:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key
5. (Optional) Restrict API key to Vision API only for security

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy your API key (starts with `sk-`)

### Anthropic API Key (Alternative)

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Go to "API Keys"
4. Create new API key
5. Copy your API key

## 🎮 Usage

### Start the Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m app.main
```

The API will be available at: `http://localhost:8000`

### Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The app will be available at: `http://localhost:3000`

## 📱 Using the Application

### Method 1: Upload Image

1. Click "Upload Image" button
2. Drag & drop or browse for an image with math content
3. Click "Generate Animation"
4. Wait for processing (usually 30-60 seconds)
5. Watch your animation!

### Method 2: Camera Capture

1. Click "Camera" button
2. Allow camera access
3. Position math problem in frame
4. Click "Capture"
5. Click "Use This Photo"
6. Watch the animation being generated!

### Method 3: Text Input

1. Type or paste a math problem in the chat box
2. Press Enter or click Send
3. AI will generate and render the animation

## 📂 Project Structure

```
MATH-AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── routers/
│   │   │   ├── image.py         # Image processing endpoints
│   │   │   └── animation.py     # Animation generation endpoints
│   │   ├── services/
│   │   │   ├── vision_service.py    # Google Vision integration
│   │   │   ├── ai_service.py        # OpenAI/Anthropic integration
│   │   │   └── manim_service.py     # Manim rendering
│   │   └── utils/
│   ├── temp/                    # Temporary video storage
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── ImageUploader.jsx
│   │   │   ├── CameraCapture.jsx
│   │   │   └── VideoPlayer.jsx
│   │   ├── services/
│   │   │   └── api.js           # API client
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
└── manim/                       # ManimGL library
```

## 🔧 API Endpoints

### Image Processing

- `POST /api/image/upload` - Upload and analyze image
- `POST /api/image/extract-text` - Extract text from image
- `POST /api/image/analyze` - Comprehensive image analysis

### Animation Generation

- `POST /api/animation/generate` - Generate Manim code from text
- `POST /api/animation/render` - Render animation from code
- `POST /api/animation/from-image` - Complete pipeline (image → animation)
- `POST /api/animation/explain` - Explain math problem
- `POST /api/animation/improve` - Improve existing code
- `POST /api/animation/validate` - Validate Manim code

## 🎨 Customization

### Change Video Quality

In `.env`:
```env
VIDEO_QUALITY=low    # Fast rendering, lower quality
VIDEO_QUALITY=medium # Balanced (default)
VIDEO_QUALITY=high   # Slow rendering, best quality
```

### Change AI Provider

In `.env`:
```env
AI_PROVIDER=openai      # Use GPT-4
AI_PROVIDER=anthropic   # Use Claude
```

### Customize UI Colors

Edit `frontend/tailwind.config.js` to change color scheme.

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not found"
- Make sure you created `.env` file in `backend/` directory
- Verify your API key is correctly pasted
- Restart the backend server after changing `.env`

### "Manim rendering failed"
- Ensure ManimGL is installed: `manimgl --version`
- Check FFmpeg is installed: `ffmpeg -version`
- Try reducing video quality in `.env`

### Camera not working
- Allow camera permissions in browser
- Try using HTTPS (required for camera on some browsers)
- Check browser console for errors

### Slow rendering
- Use `VIDEO_QUALITY=low` for faster results
- Complex animations take longer (30-120 seconds)
- Consider upgrading server resources

## 📝 Example Math Problems

Try these examples:

1. **Quadratic Formula**: `x = (-b ± √(b²-4ac)) / 2a`
2. **Pythagorean Theorem**: `a² + b² = c²`
3. **Derivative**: `d/dx (x²) = 2x`
4. **Integration**: `∫ x dx = x²/2 + C`
5. **Trigonometry**: `sin²θ + cos²θ = 1`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [ManimGL](https://github.com/3b1b/manim) by 3Blue1Brown
- [Google Cloud Vision API](https://cloud.google.com/vision)
- [OpenAI GPT-4](https://openai.com/)
- [Anthropic Claude](https://www.anthropic.com/)

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ for math education