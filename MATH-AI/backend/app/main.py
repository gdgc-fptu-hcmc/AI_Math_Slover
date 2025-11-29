import os
from pathlib import Path

from app.routers import animation, image
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.staticfiles import StaticFiles
# Load environment variables
load_dotenv()

# Create FastAPI app
# Create FastAPI app
app = FastAPI(
    title="Math Animation AI",
    description="AI-powered math animation generator using Google Vision and Manim",
    version="1.0.0",
)

# CORS middleware
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp directory if not exists
temp_dir = Path(os.getenv("TEMP_DIR", "./temp"))
temp_dir.mkdir(exist_ok=True)

# Create videos subdirectory
videos_dir = temp_dir / "videos"
videos_dir.mkdir(exist_ok=True)

app.mount("/videos", StaticFiles(directory=str(videos_dir)), name="videos")

# Also mount /media for Manim's default location
media_dir = Path("./media/videos")
if media_dir.exists():
    app.mount("/media/videos", StaticFiles(directory=str(media_dir)), name="media_videos")

# Include routers
app.include_router(image.router, prefix="/api/image", tags=["image"])
app.include_router(animation.router, prefix="/api/animation", tags=["animation"])


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back for now
            await manager.send_message({"message": "Connected"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    return {"message": "Math Animation AI API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
