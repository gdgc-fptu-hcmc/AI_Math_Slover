import os
from typing import Optional

import requests
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()


class VisionService:
    """Service for Google Cloud Vision API operations using REST API"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        self.api_url = (
            f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
        )

    def extract_text(self, image_content: bytes) -> dict:
        """
        Extract text from image using Google Vision OCR

        Args:
            image_content: Image bytes

        Returns:
            dict with extracted text and metadata
        """
        try:
            import base64

            # Encode image to base64
            image_base64 = base64.b64encode(image_content).decode("utf-8")

            # Prepare request
            request_body = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [{"type": "TEXT_DETECTION"}],
                    }
                ]
            }

            # Make API call
            response = requests.post(self.api_url, json=request_body)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                raise Exception(
                    f"Vision API Error: {result['error'].get('message', 'Unknown error')}"
                )

            responses = result.get("responses", [])
            if not responses or "textAnnotations" not in responses[0]:
                return {
                    "success": False,
                    "text": "",
                    "message": "No text found in image",
                }

            texts = responses[0]["textAnnotations"]

            # First annotation contains the full text
            full_text = texts[0]["description"] if texts else ""

            # Extract individual text blocks with positions
            text_blocks = []
            for text in texts[1:]:  # Skip first (full text)
                vertices = [
                    (vertex.get("x", 0), vertex.get("y", 0))
                    for vertex in text.get("boundingPoly", {}).get("vertices", [])
                ]
                text_blocks.append({"text": text["description"], "bounds": vertices})

            return {
                "success": True,
                "text": full_text,
                "blocks": text_blocks,
                "message": "Text extracted successfully",
            }

        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e),
                "message": f"Error extracting text: {str(e)}",
            }

    def detect_math_content(self, image_content: bytes) -> dict:
        """
        Detect if image contains mathematical content

        Args:
            image_content: Image bytes

        Returns:
            dict with detection results
        """
        try:
            # First extract text
            text_result = self.extract_text(image_content)

            if not text_result["success"]:
                return text_result

            text = text_result["text"]

            # Common math symbols and patterns
            math_indicators = [
                "=",
                "+",
                "-",
                "×",
                "÷",
                "²",
                "³",
                "√",
                "∫",
                "∑",
                "π",
                "α",
                "β",
                "γ",
                "∞",
                "sin",
                "cos",
                "tan",
                "log",
                "ln",
                "dx",
                "dy",
                "d/dx",
                "lim",
                "∆",
                "∂",
            ]

            # Check for math content
            has_math = any(indicator in text for indicator in math_indicators)

            # Calculate confidence based on math symbol density
            math_count = sum(text.count(indicator) for indicator in math_indicators)
            confidence = min(1.0, math_count / max(1, len(text) / 20))

            return {
                "success": True,
                "has_math": has_math,
                "confidence": confidence,
                "text": text,
                "blocks": text_result.get("blocks", []),
                "message": "Math content detected"
                if has_math
                else "No math content detected",
            }

        except Exception as e:
            return {
                "success": False,
                "has_math": False,
                "confidence": 0.0,
                "error": str(e),
                "message": f"Error detecting math content: {str(e)}",
            }

    def analyze_image(self, image_content: bytes) -> dict:
        """
        Comprehensive image analysis including labels, objects, and text

        Args:
            image_content: Image bytes

        Returns:
            dict with full analysis
        """
        try:
            import base64

            # Encode image to base64
            image_base64 = base64.b64encode(image_content).decode("utf-8")

            # Prepare request with multiple features
            request_body = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [
                            {"type": "TEXT_DETECTION"},
                            {"type": "LABEL_DETECTION"},
                            {"type": "DOCUMENT_TEXT_DETECTION"},
                        ],
                    }
                ]
            }

            # Make API call
            response = requests.post(self.api_url, json=request_body)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                raise Exception(
                    f"Vision API Error: {result['error'].get('message', 'Unknown error')}"
                )

            responses = result.get("responses", [])
            if not responses:
                return {
                    "success": False,
                    "error": "No response from API",
                    "message": "Failed to analyze image",
                }

            response_data = responses[0]

            # Extract text
            text = ""
            if "textAnnotations" in response_data and response_data["textAnnotations"]:
                text = response_data["textAnnotations"][0]["description"]

            # Extract labels
            labels = [
                label["description"]
                for label in response_data.get("labelAnnotations", [])
            ]

            # Extract document text (better for structured content)
            document_text = ""
            if "fullTextAnnotation" in response_data:
                document_text = response_data["fullTextAnnotation"].get("text", "")

            return {
                "success": True,
                "text": text or document_text,
                "labels": labels,
                "has_text": bool(text or document_text),
                "message": "Image analyzed successfully",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error analyzing image: {str(e)}",
            }


# Singleton instance
vision_service = VisionService()
