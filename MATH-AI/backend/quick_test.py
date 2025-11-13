#!/usr/bin/env python3
"""
Quick test script to verify the /api/animation/from-image endpoint
"""

import base64
import io
import os
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont


def create_test_image():
    """Create a simple test image with math content"""
    # Create a white image
    img = Image.new("RGB", (400, 200), color="white")
    draw = ImageDraw.Draw(img)

    # Draw some math text
    try:
        # Try to use a larger font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Draw math equation
    text = "2x + 5 = 15\nSolve for x"
    draw.text((50, 60), text, fill="black", font=font)

    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return img_byte_arr.getvalue()


def test_endpoint():
    """Test the /api/animation/from-image endpoint"""
    print("=" * 60)
    print("🧪 Testing /api/animation/from-image endpoint")
    print("=" * 60)
    print()

    # API URL
    api_url = "http://localhost:8001/api/animation/from-image"

    print("1. Creating test image with math content...")
    image_data = create_test_image()
    print(f"   ✓ Created test image ({len(image_data)} bytes)")
    print()

    print("2. Sending POST request to endpoint...")
    try:
        # Prepare the request
        files = {"file": ("test_math.png", image_data, "image/png")}
        data = {"additional_context": "Please create a simple animation"}

        # Send request
        response = requests.post(api_url, files=files, data=data, timeout=60)

        print(f"   Status Code: {response.status_code}")
        print()

        if response.status_code == 200:
            print("✅ SUCCESS! The endpoint is working correctly!")
            print()
            result = response.json()

            print("Response details:")
            print(f"  - Success: {result.get('success', False)}")
            print(f"  - Math Text: {result.get('math_text', 'N/A')[:100]}...")
            print(f"  - Video URL: {result.get('video_url', 'N/A')}")
            print(f"  - Message: {result.get('message', 'N/A')}")

            if result.get("code"):
                print(f"\n  Generated Code Preview:")
                print("  " + "-" * 50)
                code_lines = result["code"].split("\n")[:10]
                for line in code_lines:
                    print(f"  {line}")
                print("  " + "-" * 50)

            return True

        else:
            print("❌ ERROR! The endpoint returned an error status code.")
            print()
            print("Response body:")
            try:
                error_data = response.json()
                print(f"  {error_data}")
            except:
                print(f"  {response.text}")

            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR! Cannot connect to the backend server.")
        print()
        print("   Please make sure the server is running:")
        print("   cd backend && uvicorn app.main:app --reload --port 8001")
        return False

    except requests.exceptions.Timeout:
        print("❌ ERROR! Request timed out after 60 seconds.")
        print()
        print("   The server might be processing the request.")
        print("   Check the server logs for more details.")
        return False

    except Exception as e:
        print(f"❌ ERROR! An unexpected error occurred:")
        print(f"   {type(e).__name__}: {str(e)}")
        return False


def main():
    print()
    print("=" * 60)
    print("🔬 QUICK ENDPOINT TEST")
    print("=" * 60)
    print()

    # Check if server is running
    print("Checking if backend server is running...")
    try:
        health_response = requests.get("http://localhost:8001/health", timeout=5)
        if health_response.status_code == 200:
            print("✓ Backend server is running")
            print()
        else:
            print("⚠ Server responded but health check failed")
            print()
    except:
        print("✗ Backend server is NOT running!")
        print()
        print("Please start the server first:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload --port 8001")
        print()
        return

    # Run the test
    success = test_endpoint()

    print()
    print("=" * 60)
    if success:
        print("✅ TEST PASSED - Everything is working!")
    else:
        print("❌ TEST FAILED - Please check the errors above")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
