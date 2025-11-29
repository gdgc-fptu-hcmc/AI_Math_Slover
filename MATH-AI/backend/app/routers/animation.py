import os
import traceback
import uuid
from typing import Optional

from app.services.ai_service import ai_service
from app.services.manim_service import manim_service
from app.services.vision_service import vision_service
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

router = APIRouter()


class GenerateRequest(BaseModel):
    math_text: str
    additional_context: Optional[str] = None


class RenderRequest(BaseModel):
    code: str
    scene_name: str = "MathAnimation"


class ImproveRequest(BaseModel):
    code: str
    feedback: str


@router.post("/generate")
async def generate_animation(request: GenerateRequest):
    """
    Generate Manim code from math text

    Args:
        math_text: Mathematical content to animate
        additional_context: Optional additional instructions

    Returns:
        Generated Manim code
    """
    try:
        if not request.math_text or not request.math_text.strip():
            raise HTTPException(status_code=400, detail="Math text is required")

        # Generate code with AI
        result = ai_service.generate_manim_code(
            request.math_text, request.additional_context or ""
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=result.get("message", "Code generation failed")
            )

        # Validate generated code
        validation = manim_service.validate_code(result["code"])

        return JSONResponse(
            content={
                "success": True,
                "code": result["code"],
                "validation": validation,
                "provider": result.get("provider"),
                "model": result.get("model"),
                "message": "Code generated successfully",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")


@router.post("/render")
async def render_animation(request: RenderRequest):
    """
    Render Manim animation from code

    Args:
        code: Manim Python code
        scene_name: Name of the Scene class to render

    Returns:
        Video file URL and metadata
    """
    try:
        if not request.code or not request.code.strip():
            raise HTTPException(status_code=400, detail="Code is required")

        # Validate code first
        validation = manim_service.validate_code(request.code)
        if not validation["valid"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Code validation failed",
                    "issues": validation.get("issues", []),
                },
                status_code=400,
            )

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Render animation
        result = manim_service.render_animation(
            request.code, request.scene_name, session_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=result.get("message", "Rendering failed")
            )

        return JSONResponse(
            content={
                "success": True,
                "video_url": result["video_url"],
                "video_path": result["video_path"],
                "session_id": result["session_id"],
                "message": "Animation rendered successfully",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rendering animation: {str(e)}"
        )


@router.post("/from-image")
async def generate_from_image(
    file: UploadFile = File(...), additional_context: Optional[str] = Form(None)
):
    """
    Complete pipeline: Upload image -> Extract math -> Generate code -> Render animation

    Args:
        file: Image file containing math content
        additional_context: Optional additional instructions

    Returns:
        Video URL and all intermediate results
    """
    try:
        # Read image
        image_content = await file.read()

        # Step 1: Extract math content
        vision_result = vision_service.detect_math_content(image_content)

        if not vision_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=vision_result.get("message", "Failed to extract text"),
            )

        if not vision_result["has_math"]:
            raise HTTPException(
                status_code=400,
                detail="No mathematical content detected in image. Please upload an image with math equations or problems.",
            )

        math_text = vision_result["text"]

        # Step 2: Generate Manim code
        ai_result = ai_service.generate_manim_code(math_text, additional_context or "")

        if not ai_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=ai_result.get("message", "Failed to generate code"),
            )

        code = ai_result["code"]

        # Step 3: Validate code
        validation = manim_service.validate_code(code)

        # Step 4: Render animation
        session_id = str(uuid.uuid4())
        render_result = manim_service.render_animation(
            code, "MathAnimation", session_id
        )

        if not render_result["success"]:
            # Return partial results even if rendering fails
            return JSONResponse(
                content={
                    "success": False,
                    "math_text": math_text,
                    "code": code,
                    "validation": validation,
                    "render_error": render_result.get("error"),
                    "message": "Rendering failed, but code was generated",
                },
                status_code=500,
            )

        # Success - return everything
        return JSONResponse(
            content={
                "success": True,
                "math_text": math_text,
                "confidence": vision_result.get("confidence", 0),
                "code": code,
                "validation": validation,
                "video_url": render_result["video_url"],
                "session_id": session_id,
                "message": "Animation created successfully from image",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"ERROR in from-image: {error_trace}")
        raise HTTPException(
            status_code=500, detail=f"Error processing image to animation: {str(e)}"
        )


@router.post("/improve")
async def improve_code(request: ImproveRequest):
    """
    Improve existing Manim code based on feedback

    Args:
        code: Current Manim code
        feedback: Improvement suggestions or error messages

    Returns:
        Improved code
    """
    try:
        if not request.code or not request.feedback:
            raise HTTPException(
                status_code=400, detail="Both code and feedback are required"
            )

        # Improve code with AI
        result = ai_service.improve_code(request.code, request.feedback)

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=result.get("message", "Code improvement failed")
            )

        # Validate improved code
        validation = manim_service.validate_code(result["code"])

        return JSONResponse(
            content={
                "success": True,
                "code": result["code"],
                "validation": validation,
                "message": "Code improved successfully",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error improving code: {str(e)}")


@router.post("/explain")
async def explain_math(file: UploadFile = File(...)):
    """
    Extract and explain mathematical content from image

    Args:
        file: Image file containing math content

    Returns:
        Extracted text and step-by-step explanation
    """
    try:
        # Read image
        image_content = await file.read()

        # Extract math content
        vision_result = vision_service.detect_math_content(image_content)

        if not vision_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=vision_result.get("message", "Failed to extract text"),
            )

        if not vision_result["has_math"]:
            raise HTTPException(
                status_code=400, detail="No mathematical content detected in image"
            )

        math_text = vision_result["text"]

        # Generate explanation
        explain_result = ai_service.explain_math(math_text)

        if not explain_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=explain_result.get("message", "Failed to generate explanation"),
            )

        return JSONResponse(
            content={
                "success": True,
                "math_text": math_text,
                "explanation": explain_result["explanation"],
                "confidence": vision_result.get("confidence", 0),
                "message": "Explanation generated successfully",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining math: {str(e)}")


@router.post("/validate")
async def validate_code(code: str = Form(...)):
    """
    Validate Manim code without rendering

    Args:
        code: Manim Python code to validate

    Returns:
        Validation results
    """
    try:
        result = manim_service.validate_code(code)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating code: {str(e)}")


@router.post("/cleanup")
async def cleanup_temp_files(max_age_hours: int = 24):
    """
    Clean up old temporary files

    Args:
        max_age_hours: Maximum age of files to keep (in hours)

    Returns:
        Cleanup results
    """
    try:
        result = manim_service.cleanup_old_files(max_age_hours)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up: {str(e)}")


@router.post("/chat")
async def smart_chat(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    mode: Optional[str] = Form("auto"),
):
    """Smart chat endpoint"""
    
    print("\n🔵 /chat ENDPOINT CALLED")
    print(f"   text: {text}, mode: {mode}")
    
    try:
        print("📌 Step 1: Extract math content")
        math_text = ""
        is_image_input = False

        # Extract math content from image if provided
        if file:
            print("📌 Step 1a: Processing file")
            is_image_input = True
            image_content = await file.read()
            vision_result = vision_service.detect_math_content(image_content)

            if not vision_result["success"]:
                print(f"❌ Vision failed: {vision_result.get('message')}")
                raise HTTPException(
                    status_code=500,
                    detail=vision_result.get("message", "Failed to extract text"),
                )

            math_text = vision_result["text"]
            has_math = vision_result.get("has_math", False)

            if not has_math:
                print("❌ No math detected in image")
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "No mathematical content detected in image",
                        "type": "error",
                    },
                    status_code=400,
                )
        elif text:
            print(f"📌 Step 1b: Using text input: {text[:100]}...")
            math_text = text
        else:
            print("❌ No file or text provided")
            raise HTTPException(
                status_code=400, detail="Either file or text must be provided"
            )

        print(f"📌 Math text extracted: {math_text[:100]}...")

        # Classify input if mode is auto
        print(f"📌 Step 2: Determine mode (current mode: {mode})")
        
        if mode == "auto":
            print("📌 Step 2a: Classifying input")
            try:
                classification = ai_service.classify_input(math_text)
                print(f"📌 Classification result: {classification}")
                detected_mode = classification.get("suggested_action", "chat")
                is_math = classification.get("is_math", False)
                content_type = classification.get("content_type", "unclear")
                print(f"📌 Detected mode: {detected_mode}, is_math: {is_math}")
            except Exception as e:
                print(f"❌ Classification failed: {e}")
                import traceback
                traceback.print_exc()
                raise
        else:
            print(f"📌 Step 2b: Using explicit mode: {mode}")
            detected_mode = mode

        print(f"📌 Final detected_mode: {detected_mode}")

        # Handle different modes
        if detected_mode == "chat":
            print("📌 Step 3: Processing as CHAT")
            chat_result = ai_service.chat_response(math_text)
            if not chat_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=chat_result.get("message", "Failed to generate response"),
                )
            return JSONResponse(
                content={
                    "success": True,
                    "type": "chat",
                    "content": chat_result["response"],
                    "message": "Chat response generated successfully",
                }
            )

        elif detected_mode == "explain":
            print("📌 Step 3: Processing as EXPLAIN")
            result = ai_service.explain_math(math_text)
            if not result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=result.get("message", "Failed to generate explanation"),
                )
            return JSONResponse(
                content={
                    "success": True,
                    "type": "explanation",
                    "math_text": math_text,
                    "content": result["explanation"],
                    "message": "Explanation generated successfully",
                }
            )

        elif detected_mode == "answer":
            print("📌 Step 3: Processing as ANSWER")
            result = ai_service.quick_answer(math_text)
            if not result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=result.get("message", "Failed to generate answer"),
                )
            return JSONResponse(
                content={
                    "success": True,
                    "type": "answer",
                    "math_text": math_text,
                    "content": result["answer"],
                    "message": "Answer generated successfully",
                }
            )

        elif detected_mode == "animate":
            print("📌 Step 3: Processing as ANIMATE")
            
            # Generate code
            print("📌 Step 3a: Calling generate_manim_code")
            ai_result = ai_service.generate_manim_code(math_text)

            if not ai_result["success"]:
                print(f"❌ Code generation failed: {ai_result.get('message')}")
                raise HTTPException(
                    status_code=500,
                    detail=ai_result.get("message", "Failed to generate code"),
                )

            print(f"✅ Code generated: {len(ai_result['code'])} chars")

            # Render animation
            print("📌 Step 3b: Calling render_animation")
            session_id = str(uuid.uuid4())
            render_result = manim_service.render_animation(
                ai_result["code"], "MathAnimation", session_id
            )

            if not render_result["success"]:
                print(f"❌ Rendering failed: {render_result.get('error')}")
                return JSONResponse(
                    content={
                        "success": False,
                        "type": "animation",
                        "math_text": math_text,
                        "code": ai_result["code"],
                        "render_error": render_result.get("error"),
                        "message": "Animation rendering failed, but code was generated",
                    },
                    status_code=500,
                )

            print(f"✅ Rendering succeeded: {render_result.get('video_url')}")
            
            return JSONResponse(
                content={
                    "success": True,
                    "type": "animation",
                    "math_text": math_text,
                    "video_url": render_result["video_url"],
                    "code": ai_result["code"],
                    "session_id": session_id,
                    "message": "Animation created successfully",
                }
            )

        else:
            print(f"❌ Invalid mode: {detected_mode}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode: {mode}",
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌❌❌ EXCEPTION IN /chat:")
        import traceback
        traceback.print_exc()
        print("❌❌❌\n")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for animation service"""
    return {"status": "healthy", "service": "animation processing"}
