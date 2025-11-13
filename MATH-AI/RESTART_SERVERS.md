# 🔄 Restart Servers Guide

## Quick Restart

If you've made code changes and the backend is returning 404 errors, you need to restart the servers.

### Option 1: Using the start script (Recommended)

```bash
# Stop any running servers first (Ctrl+C in their terminals)
# Then run:
./start.sh
```

This will start both backend and frontend servers automatically.

### Option 2: Manual Restart

#### Restart Backend Only

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Kill any existing backend process
pkill -f "uvicorn app.main:app" || kill $(lsof -t -i:8000)

# Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Restart Frontend Only

```bash
# Terminal 2: Frontend
cd frontend

# Kill any existing frontend process
pkill -f "vite" || kill $(lsof -t -i:5173)

# Start frontend server
npm run dev
```

### Option 3: Complete Clean Restart

If you're still having issues, do a complete clean restart:

```bash
# 1. Kill all processes
pkill -f "uvicorn"
pkill -f "vite"
pkill -f "node"

# 2. Clear Python cache (optional but recommended)
cd backend
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 3. Start backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. In a new terminal, start frontend
cd frontend
npm run dev
```

## Common Issues After Code Changes

### ❌ 404 Not Found
**Cause**: Backend not restarted after adding new endpoints  
**Solution**: Restart backend server (see above)

### ❌ Module not found
**Cause**: New dependencies not installed  
**Solution**: 
```bash
cd backend
pip install -r requirements.txt
```

### ❌ Port already in use
**Cause**: Old server still running  
**Solution**:
```bash
# Kill process on port 8000 (backend)
kill $(lsof -t -i:8000)

# Kill process on port 5173 (frontend)
kill $(lsof -t -i:5173)
```

### ❌ Changes not reflecting
**Cause**: Browser cache  
**Solution**: Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

## Verify Servers Are Running

### Check Backend
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

curl http://localhost:8000/api/animation/health
# Should return: {"status":"healthy","service":"animation processing"}
```

### Check Frontend
Open browser: http://localhost:5173 or http://localhost:3000

## Development Tips

1. **Use --reload flag**: Backend auto-restarts on file changes
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Check logs**: Always monitor terminal output for errors

3. **Test endpoints**: Use curl or Postman to test new endpoints:
   ```bash
   curl -X POST http://localhost:8000/api/animation/chat \
     -F "text=Solve x^2 + 2x + 1 = 0" \
     -F "mode=answer"
   ```

4. **Frontend hot reload**: Vite automatically reloads on file changes

## Environment Variables

If endpoints are working but features aren't, check your `.env`:

```bash
cd backend
cat .env

# Should have:
# - GOOGLE_API_KEY or GOOGLE_GEMINI_API_KEY
# - OPENAI_API_KEY or ANTHROPIC_API_KEY
# - AI_PROVIDER=gemini (or openai/anthropic)
```

## Still Having Issues?

1. Check backend logs for detailed error messages
2. Check browser console (F12) for frontend errors
3. Verify all dependencies are installed
4. Make sure you're on the correct branch with latest code
5. Try `git pull` to get latest updates

---

**Pro Tip**: Keep two terminals open - one for backend, one for frontend. This makes it easy to see logs from both services and restart them quickly when needed.