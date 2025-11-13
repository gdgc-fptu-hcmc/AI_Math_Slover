#!/usr/bin/env python3
"""
Live demo script - Test full pipeline with image upload
Demonstrates automatic graph generation and concise code
"""

import io
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

# Configuration
API_URL = "http://localhost:8001"
TIMEOUT = 120  # seconds


def create_test_images():
    """Create test images with different math problems"""
    test_cases = [
        {
            "name": "parabola.png",
            "text": "Vẽ đồ thị hàm số\ny = x² - 4x + 3\n\nTìm đỉnh và giao điểm",
            "description": "Hàm bậc 2 - Parabol",
        },
        {
            "name": "linear.png",
            "text": "Plot the function:\ny = 2x + 1\n\nShow slope and intercept",
            "description": "Hàm bậc nhất",
        },
        {
            "name": "equation.png",
            "text": "Giải phương trình:\n2x + 5 = 15\n\nTìm x",
            "description": "Giải phương trình (không cần đồ thị)",
        },
        {
            "name": "sine.png",
            "text": "Vẽ đồ thị\ny = sin(x)\n\nTừ 0 đến 2π",
            "description": "Hàm lượng giác",
        },
    ]

    created_files = []

    for case in test_cases:
        # Create image
        img = Image.new("RGB", (500, 300), color="white")
        draw = ImageDraw.Draw(img)

        # Try to use nice font
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            font_text = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()

        # Draw text
        y_pos = 50
        for line in case["text"].split("\n"):
            if line.strip():
                draw.text((30, y_pos), line, fill="black", font=font_text)
                y_pos += 50

        # Save image
        filepath = Path(case["name"])
        img.save(filepath)
        created_files.append(
            {"path": filepath, "description": case["description"], "text": case["text"]}
        )
        print(f"✓ Created: {case['name']}")

    return created_files


def check_server():
    """Check if backend server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_and_test(image_path, description):
    """Upload image and test the full pipeline"""
    print("\n" + "=" * 70)
    print(f"📊 TEST: {description}")
    print("=" * 70)

    # Read image
    with open(image_path, "rb") as f:
        image_data = f.read()

    print(f"📁 Image: {image_path.name} ({len(image_data)} bytes)")
    print("⏳ Uploading and processing...")
    print()

    try:
        # Upload to API
        files = {"file": (image_path.name, image_data, "image/png")}
        data = {"additional_context": ""}

        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/animation/from-image",
            files=files,
            data=data,
            timeout=TIMEOUT,
        )
        elapsed = time.time() - start_time

        print(f"⏱️  Response time: {elapsed:.1f}s")
        print(f"📡 Status code: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()

            if result.get("success"):
                print("✅ SUCCESS!")
                print()

                # Display results
                print("📝 Extracted Math Text:")
                print("-" * 70)
                math_text = result.get("math_text", "N/A")
                for line in math_text.split("\n")[:5]:
                    print(f"  {line}")
                if len(math_text.split("\n")) > 5:
                    print("  ...")
                print()

                # Code analysis
                code = result.get("code", "")
                lines = code.split("\n")
                non_empty = [l for l in lines if l.strip()]

                print("💻 Generated Code Analysis:")
                print("-" * 70)
                print(f"  Total lines: {len(lines)}")
                print(f"  Non-empty lines: {len(non_empty)}")

                # Check for graph elements
                has_axes = "Axes(" in code or "axes =" in code
                has_graph = "get_graph" in code
                has_plot = has_axes and has_graph

                print(f"  Has Axes: {'✓' if has_axes else '✗'}")
                print(f"  Has get_graph: {'✓' if has_graph else '✗'}")
                print(f"  Contains plotting: {'✓' if has_plot else '✗'}")

                # Comments analysis
                comments = [l for l in lines if "#" in l]
                vietnamese_comments = [
                    l
                    for l in comments
                    if any(
                        c in l
                        for c in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
                    )
                ]
                print(f"  Comments: {len(comments)}")
                print(f"  Vietnamese comments: {len(vietnamese_comments)}")
                print()

                # Video info
                video_url = result.get("video_url", "N/A")
                print(f"🎬 Video URL: {video_url}")
                print()

                # Code preview
                print("📄 Code Preview (first 25 lines):")
                print("=" * 70)
                for i, line in enumerate(lines[:25], 1):
                    print(f"{i:3d} | {line}")
                if len(lines) > 25:
                    print(f"... ({len(lines) - 25} more lines)")
                print("=" * 70)
                print()

                # Quality assessment
                print("📊 Code Quality Assessment:")
                print("-" * 70)
                concise = "✅ Excellent" if len(non_empty) < 60 else "⚠️  Too long"
                commented = (
                    "✅ Well commented" if len(comments) > 3 else "⚠️  Needs more"
                )
                vietnamese = (
                    "✅ Has Vietnamese"
                    if len(vietnamese_comments) > 0
                    else "⚠️  No Vietnamese"
                )
                graphing = (
                    "✅ Includes graph"
                    if has_plot
                    else "ℹ️  No graph (might not be needed)"
                )

                print(f"  Conciseness: {concise} ({len(non_empty)} lines)")
                print(f"  Comments: {commented} ({len(comments)} comments)")
                print(f"  Language: {vietnamese}")
                print(f"  Graphing: {graphing}")
                print()

                return True

            else:
                print("❌ FAILED!")
                print(f"Message: {result.get('message', 'Unknown error')}")
                if "render_error" in result:
                    print(f"Render error: {result['render_error']}")
                return False

        else:
            print("❌ HTTP ERROR!")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Response: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT! Request took longer than {TIMEOUT}s")
        return False
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run live demo"""
    print("\n" + "=" * 70)
    print("🚀 LIVE DEMO - GRAPH GENERATION & CONCISE CODE")
    print("=" * 70)
    print()

    # Check server
    print("1️⃣  Checking backend server...")
    if not check_server():
        print("❌ Backend server is not running!")
        print()
        print("Please start the server first:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload --port 8001")
        print()
        return

    print("✅ Backend server is running")
    print()

    # Create test images
    print("2️⃣  Creating test images...")
    test_images = create_test_images()
    print(f"✅ Created {len(test_images)} test images")
    print()

    # Run tests
    print("3️⃣  Running tests...")
    print()

    results = []
    for test_case in test_images:
        result = upload_and_test(test_case["path"], test_case["description"])
        results.append({"description": test_case["description"], "passed": result})
        time.sleep(1)  # Pause between tests

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print()

    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    print(f"Tests run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print()

    print("Details:")
    for r in results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"  {status} - {r['description']}")

    print()
    print("=" * 70)

    if passed == total:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")

    print("=" * 70)
    print()

    # Cleanup
    print("🧹 Cleaning up test images...")
    for test_case in test_images:
        try:
            test_case["path"].unlink()
            print(f"  ✓ Deleted {test_case['path'].name}")
        except:
            pass

    print()
    print("🎉 Demo completed!")
    print()


if __name__ == "__main__":
    main()
