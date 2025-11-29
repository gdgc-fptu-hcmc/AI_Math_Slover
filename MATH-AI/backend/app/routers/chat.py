import uuid
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body # Add Body
from pydantic import BaseModel
from app.services.ai_service import ai_service
from app.services.manim_service import manim_service

router = APIRouter()

# In-memory session storage (Replace with Redis/DB for production)
sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str
    animate: bool = False

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"success": True, "message": "Session deleted"}
    raise HTTPException(status_code=404, detail="Session not found")

@router.patch("/session/{session_id}")
async def rename_session(session_id: str, title: str = Body(..., embed=True)):
    # Note: In a real DB, you would update a 'title' field. 
    # Since we are using in-memory list for history, we can't store metadata easily 
    # without changing the data structure.
    # For this demo, we will accept the request to keep frontend happy, 
    # but in a real app, you must upgrade 'sessions' to be a dict of dicts.
    
    if session_id in sessions:
        # Placeholder for DB update
        return {"success": True, "title": title}
    raise HTTPException(status_code=404, detail="Session not found")

@router.post("/session/new")
async def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = []
    return {"session_id": session_id, "history": []}

@router.get("/session/{session_id}")
async def get_history(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"history": sessions[session_id]}

@router.post("/send")
async def send_message(
    session_id: str = Form(...),
    message: str = Form(""),
    animate: str = Form("false"), # Received as string from FormData
    files: List[UploadFile] = File(None)
):
    if session_id not in sessions:
        sessions[session_id] = []
    
    # 1. Process Files
    processed_files = []
    if files:
        for file in files:
            content = await file.read()
            processed_files.append({
                "data": content,
                "mime_type": file.content_type
            })

    # 2. Update User History
    user_entry = {"role": "user", "content": message}
    sessions[session_id].append(user_entry)

    # 3. Call AI Service
    is_animate = animate.lower() == "true"
    result = ai_service.chat_turn(
        history=sessions[session_id],
        files=processed_files,
        animate=is_animate
    )

    # 4. Handle Result
    response_entry = {"role": "assistant"}
    
    if result["type"] == "code":
        # It's an animation request, render it immediately
        response_entry["content"] = "Generating animation..."
        sessions[session_id].append(response_entry)
        
        # Render
        render_result = manim_service.render_animation(result["content"])
        
        if render_result["success"]:
            final_response = {
                "type": "animation",
                "video_url": render_result["video_url"],
                "code": result["content"],
                "text": "Here is your animation."
            }
        else:
            final_response = {
                "type": "error",
                "text": f"Rendering failed: {render_result['message']}"
            }
    else:
        # Standard text/explanation
        final_response = {
            "type": "text",
            "text": result["content"]
        }

    # Update history with final assistant response
    sessions[session_id][-1]["content"] = final_response.get("text", "")
    sessions[session_id][-1]["metadata"] = final_response

    return final_response