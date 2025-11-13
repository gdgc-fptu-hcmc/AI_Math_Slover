import os
import uuid
from pathlib import Path
from typing import Optional

from app.services.vision_service import vision_service
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

router = APIRouter()


class ImageAnalysisResponse(BaseModel):
    success: bool
    text: Optional[str] = None
    has_math: Optional[bool] = None
    confidence: Optional[float] = None
    message: str
    error: Optional[str] = None


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file for processing

    Accepts: JPEG, PNG, WebP, GIF
    Returns: Extracted text and math detection results
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}",
            )

        # Read image content
        image_content = await file.read()

        # Validate image can be opened
        try:
            img = Image.open(file.file)
            img.verify()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

        # Reset file pointer after verify
        file.file.seek(0)
        image_content = await file.read()

        # Process with Google Vision
        result = vision_service.detect_math_content(image_content)

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=result.get("message", "Processing failed")
            )

        return JSONResponse(
            content={
                "success": True,
                "filename": file.filename,
                "text": result["text"],
                "has_math": result["has_math"],
                "confidence": result["confidence"],
                "blocks": result.get("blocks", []),
                "message": result["message"],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Comprehensive image analysis including OCR and object detection

    Returns: Full analysis with text, labels, and metadata
    """
    try:
        # Read image content
        image_content = await file.read()

        # Process with Google Vision
        result = vision_service.analyze_image(image_content)

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=result.get("message", "Analysis failed")
            )

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


@router.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from image using OCR

    Returns: Extracted text with bounding boxes
    """
    try:
        # Read image content
        image_content = await file.read()

        # Extract text with Google Vision
        result = vision_service.extract_text(image_content)

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=result.get("message", "Text extraction failed")
            )

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for image processing service"""
    return {"status": "healthy", "service": "image processing"}
