"""
Test script to diagnose Vision API and from-image endpoint issues
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_environment():
    """Test if environment variables are set"""
    print("=" * 60)
    print("1. Testing Environment Variables")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    ai_provider = os.getenv("AI_PROVIDER")

    print(f"GOOGLE_API_KEY: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"GOOGLE_GEMINI_API_KEY: {'✓ Set' if gemini_key else '✗ Missing'}")
    print(f"AI_PROVIDER: {ai_provider or '✗ Not set'}")
    print()

    return bool(api_key)


def test_vision_service():
    """Test Vision Service initialization"""
    print("=" * 60)
    print("2. Testing Vision Service Initialization")
    print("=" * 60)

    try:
        from app.services.vision_service import vision_service

        print("✓ Vision service initialized successfully")
        print(f"  API URL: {vision_service.api_url[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize vision service:")
        print(f"  Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_vision_api():
    """Test Vision API with a simple request"""
    print("\n" + "=" * 60)
    print("3. Testing Google Vision API Connection")
    print("=" * 60)

    try:
        import base64

        import requests

        api_key = os.getenv("GOOGLE_API_KEY")
        api_url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"

        # Create a simple test image (1x1 white pixel PNG)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

        request_body = {
            "requests": [
                {
                    "image": {"content": test_image_base64},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }

        print("Sending test request to Vision API...")
        response = requests.post(api_url, json=request_body, timeout=10)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                print(f"✗ API Error: {result['error']}")
                return False
            else:
                print("✓ Vision API is working correctly")
                return True
        else:
            print(f"✗ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Failed to connect to Vision API:")
        print(f"  Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_ai_service():
    """Test AI Service initialization"""
    print("\n" + "=" * 60)
    print("4. Testing AI Service (Gemini)")
    print("=" * 60)

    try:
        from app.services.ai_service import ai_service

        print("✓ AI service initialized successfully")
        print(f"  Provider: {ai_service.provider}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize AI service:")
        print(f"  Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_manim_service():
    """Test Manim Service initialization"""
    print("\n" + "=" * 60)
    print("5. Testing Manim Service")
    print("=" * 60)

    try:
        from app.services.manim_service import manim_service

        print("✓ Manim service initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize Manim service:")
        print(f"  Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test the complete from-image pipeline with a sample"""
    print("\n" + "=" * 60)
    print("6. Testing Complete Pipeline (if possible)")
    print("=" * 60)

    try:
        from app.services.vision_service import vision_service

        # Try to find a test image
        test_images = [
            "test.png",
            "test.jpg",
            "sample.png",
            "sample.jpg",
            "tests/test.png",
            "tests/sample.png",
        ]

        test_image_path = None
        for img in test_images:
            if Path(img).exists():
                test_image_path = img
                break

        if not test_image_path:
            print("⚠ No test image found - skipping pipeline test")
            print(
                "  You can create a test image with math content to test the full pipeline"
            )
            return None

        print(f"Using test image: {test_image_path}")

        with open(test_image_path, "rb") as f:
            image_content = f.read()

        print("Testing Vision API text extraction...")
        result = vision_service.extract_text(image_content)

        if result["success"]:
            print(f"✓ Text extraction successful")
            print(f"  Extracted text: {result['text'][:100]}...")
            return True
        else:
            print(f"✗ Text extraction failed: {result.get('message', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"✗ Pipeline test failed:")
        print(f"  Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all diagnostic tests"""
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSTIC TEST FOR MATH-AI BACKEND")
    print("=" * 60)
    print()

    results = {
        "Environment": test_environment(),
        "Vision Service": test_vision_service(),
        "Vision API": test_vision_api(),
        "AI Service": test_ai_service(),
        "Manim Service": test_manim_service(),
        "Pipeline Test": test_full_pipeline(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        print(f"{test_name:20s}: {status}")

    print("\n" + "=" * 60)

    # Recommendations
    failed_tests = [name for name, result in results.items() if result is False]

    if failed_tests:
        print("\n⚠️  ISSUES DETECTED:")
        print()

        if "Environment" in failed_tests:
            print("• Missing GOOGLE_API_KEY in .env file")
            print("  → Add your Google Cloud API key to backend/.env")
            print()

        if "Vision API" in failed_tests:
            print("• Vision API connection failed")
            print("  → Check if your API key is valid")
            print("  → Verify that Vision API is enabled in Google Cloud Console")
            print("  → Check your internet connection")
            print()

        if "AI Service" in failed_tests:
            print("• AI Service (Gemini) initialization failed")
            print("  → Check GOOGLE_GEMINI_API_KEY in .env")
            print("  → Verify AI_PROVIDER is set to 'gemini'")
            print()

        if "Manim Service" in failed_tests:
            print("• Manim Service initialization failed")
            print("  → Check if Manim is installed: pip install manim")
            print("  → Verify TEMP_DIR exists and is writable")
            print()
    else:
        print("\n✅ All tests passed! The system should be working correctly.")
        print("\nIf you're still experiencing 500 errors, check:")
        print("• The server console for detailed error messages")
        print("• The image file format (should be PNG, JPG, or JPEG)")
        print("• The image file size (should be reasonable)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
