# 🚀 Quick Start Guide - Math Animation AI

Get up and running in 5 minutes!

## 📋 Prerequisites Check

Before starting, make sure you have:

- ✅ Python 3.7+ installed: `python3 --version`
- ✅ Node.js 18+ installed: `node --version`
- ✅ FFmpeg installed: `ffmpeg -version`

If missing, install them:

**macOS:**
```bash
brew install python node ffmpeg
```

**Windows:**
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- FFmpeg: https://ffmpeg.org/download.html

**Linux:**
```bash
sudo apt install python3 python3-pip nodejs npm ffmpeg
```

## 🔑 Step 1: Get Your API Keys (5 minutes)

### Google Cloud Vision API Key

1. Go to: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable "Cloud Vision API":
   - Navigation Menu → APIs & Services → Library
   - Search "Cloud Vision API" → Enable
4. Create API Key:
   - Navigation Menu → APIs & Services → Credentials
   - Click "Create Credentials" → "API Key"
   - Copy your key (starts with `AIza...`)

### OpenAI API Key (Recommended)

1. Go to: https://platform.openai.com/
2. Sign up / Login
3. Visit: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy your key (starts with `sk-...`)

**OR** use Anthropic Claude:
- https://console.anthropic.com/
- Create API key (if you prefer Claude over GPT-4)

## 🛠️ Step 2: Install Backend (2 minutes)

```bash
cd MATH-AI/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## 🎨 Step 3: Install ManimGL (3 minutes)

```bash
cd ../manim
pip install -e .

# Verify installation
manimgl --version
```

If you see version number, you're good! ✅

## ⚙️ Step 4: Configure Environment (1 minute)

```bash
cd ../backend

# Copy example config
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use any text editor
```

**Edit `.env` file:**
```env
# Paste your Google API key here
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX

# Paste your OpenAI key here
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX

# Or use Anthropic (uncomment if using Claude)
# ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXXXXXXXXXX
# AI_PROVIDER=anthropic

# These are good defaults
AI_PROVIDER=openai
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000
MANIM_PATH=../manim
TEMP_DIR=./temp
VIDEO_QUALITY=medium
```

Save and close (Ctrl+X, Y, Enter in nano).

## 🎯 Step 5: Install Frontend (2 minutes)

```bash
cd ../frontend

# Install dependencies
npm install
```

## 🎬 Step 6: Start the Application!

Open **TWO** terminal windows:

### Terminal 1 - Backend:
```bash
cd MATH-AI/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Frontend:
```bash
cd MATH-AI/frontend
npm run dev
```

You should see:
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:3000/
```

## 🎉 Step 7: Use It!

1. Open browser: **http://localhost:3000**
2. You'll see a beautiful chat interface
3. Try one of these:

### Option A: Upload Image
- Click "Upload Image"
- Select a photo with math (equation, formula, problem)
- Click "Generate Animation"
- Wait 30-60 seconds
- Watch your animation! 🎬

### Option B: Camera Capture
- Click "Camera"
- Allow camera access
- Point at a math problem on paper
- Click "Capture" → "Use This Photo"
- Watch the magic happen! ✨

### Option C: Type Math
- Type in the chat: `x^2 + 5x + 6 = 0`
- Press Enter
- Watch it animate! 🚀

## 🧪 Test Examples

Try these math problems:

1. **Quadratic Equation:**
   ```
   Solve: x² + 5x + 6 = 0
   ```

2. **Pythagorean Theorem:**
   ```
   In a right triangle: a² + b² = c²
   ```

3. **Derivative:**
   ```
   Find derivative of f(x) = x³ + 2x² - 5x + 1
   ```

4. **Integration:**
   ```
   ∫ 2x dx = x² + C
   ```

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not found"
- Check `.env` file exists in `backend/` folder
- Make sure API key is on correct line
- No spaces around `=` sign
- Restart backend server

### "Module not found" errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check you're in correct directory

### "Manim rendering failed"
- Check ManimGL installed: `manimgl --version`
- Check FFmpeg installed: `ffmpeg -version`
- Try `VIDEO_QUALITY=low` in `.env`
- Check `temp/` folder has write permissions

### Camera not working
- Use Chrome or Firefox (Safari can be tricky)
- Allow camera permissions when prompted
- For local dev, camera works on `localhost`
- For remote access, you need HTTPS

### Port already in use
Backend (8000) or Frontend (3000) port busy?
```bash
# Find and kill process
lsof -ti:8000 | xargs kill  # macOS/Linux
lsof -ti:3000 | xargs kill

# Or change port in .env (backend) or vite.config.js (frontend)
```

### Slow rendering
- First render always takes longer (30-120 seconds)
- Use `VIDEO_QUALITY=low` for faster results
- Complex equations take longer
- Be patient! Quality animations are worth it 😊

## 📊 What's Happening Behind the Scenes?

When you upload an image:

1. **Image → Backend** (Your photo is sent)
2. **Google Vision API** (Extracts text using OCR)
3. **AI Processing** (GPT-4/Claude generates Manim code)
4. **Code Validation** (Checks if code is valid)
5. **Manim Rendering** (Creates beautiful animation)
6. **Video → Frontend** (You see the result!)

All in 30-60 seconds! ⚡

## 🎓 Next Steps

- Read full [README.md](./README.md) for advanced features
- Check out [Manim documentation](https://3b1b.github.io/manim/)
- Explore the code and customize it!
- Share your creations! 🎬

## 💡 Pro Tips

1. **Better OCR Results:**
   - Use clear, high-contrast images
   - Avoid shadows and glare
   - Center the math in frame
   - Printed text works better than handwriting

2. **Faster Rendering:**
   - Set `VIDEO_QUALITY=low` in `.env`
   - Keep equations simple at first
   - Complex animations need more time

3. **API Costs:**
   - Google Vision: 1000 free requests/month
   - OpenAI: Pay per token (usually $0.01-0.05 per animation)
   - Set budget limits in API dashboards

4. **Development:**
   - Backend logs errors to console
   - Check browser console for frontend issues
   - Videos saved temporarily in `backend/temp/`

## 🆘 Still Having Issues?

1. Check error messages carefully
2. Verify all API keys are correct
3. Make sure all prerequisites are installed
4. Try the examples above first
5. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your OS and versions

## 🎊 Success!

If you see animations rendering, **congratulations!** 🎉

You now have a powerful AI-powered math animation tool!

---

**Made with ❤️ for math education**

Happy animating! 🚀📐✨