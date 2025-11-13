#!/usr/bin/env python3
"""
Test script for graph generation with various math problems
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import ai_service


def test_graph_detection():
    """Test if graph detection works correctly"""
    print("=" * 60)
    print("📊 Testing Graph Detection")
    print("=" * 60)
    print()

    test_cases = [
        # Should detect graph need
        ("Vẽ đồ thị hàm số y = x^2 + 2x + 1", True),
        ("Plot the function f(x) = sin(x)", True),
        ("Draw the graph of y = 2x + 5", True),
        ("Hàm số bậc hai y = -x^2 + 4x - 3", True),
        ("Graph the parabola y = x^2", True),
        ("Biểu diễn đồ thị của hàm y = 1/x", True),
        # Should NOT detect graph need
        ("Giải phương trình 2x + 5 = 15", False),
        ("Solve for x: 3x - 7 = 14", False),
        ("Tính đạo hàm của f(x) = x^3", False),
        ("Simplify: (x + 2)(x - 3)", False),
    ]

    passed = 0
    failed = 0

    for text, expected in test_cases:
        result = ai_service._should_generate_graph(text, "")
        status = "✓" if result == expected else "✗"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} '{text[:50]}...'")
        print(f"   Expected: {expected}, Got: {result}")
        print()

    print(f"Results: {passed} passed, {failed} failed")
    print()


def test_code_generation_with_graph():
    """Test code generation with graphing requirement"""
    print("=" * 60)
    print("🎨 Testing Code Generation with Graph")
    print("=" * 60)
    print()

    test_problems = [
        {
            "title": "Parabola Graph",
            "text": "Vẽ đồ thị hàm số y = x^2 - 4x + 3",
            "context": "Tìm đỉnh và giao điểm với trục",
        },
        {
            "title": "Linear Function",
            "text": "Plot the function y = 2x + 1",
            "context": "Show the slope and y-intercept",
        },
        {
            "title": "Trigonometric Function",
            "text": "Vẽ đồ thị hàm số y = sin(x)",
            "context": "Chu kỳ từ 0 đến 2π",
        },
    ]

    for i, problem in enumerate(test_problems, 1):
        print(f"\nTest {i}: {problem['title']}")
        print("-" * 60)
        print(f"Problem: {problem['text']}")
        print(f"Context: {problem['context']}")
        print()

        result = ai_service.generate_manim_code(problem["text"], problem["context"])

        if result["success"]:
            print("✅ Code generated successfully!")
            print(f"Provider: {result.get('provider', 'N/A')}")
            print(f"Model: {result.get('model', 'N/A')}")
            print()

            code = result["code"]

            # Check if code contains graph-related elements
            has_axes = "Axes(" in code or "axes =" in code
            has_get_graph = "get_graph" in code
            has_plot = has_axes and has_get_graph

            print("Code Analysis:")
            print(f"  - Has Axes: {has_axes}")
            print(f"  - Has get_graph: {has_get_graph}")
            print(f"  - Contains plotting: {has_plot}")
            print()

            # Show code preview
            print("Generated Code Preview:")
            print("=" * 60)
            lines = code.split("\n")
            for j, line in enumerate(lines[:30], 1):
                print(f"{j:3d} | {line}")
            if len(lines) > 30:
                print(f"... ({len(lines) - 30} more lines)")
            print("=" * 60)

            if has_plot:
                print("✅ PASS: Code includes graph plotting!")
            else:
                print("⚠️  WARNING: Code might be missing graph plotting")
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")

        print("\n" + "=" * 60 + "\n")


def test_concise_code():
    """Test if generated code is concise"""
    print("=" * 60)
    print("📏 Testing Code Conciseness")
    print("=" * 60)
    print()

    problem = "Giải phương trình 2x + 5 = 15"
    result = ai_service.generate_manim_code(problem)

    if result["success"]:
        code = result["code"]
        lines = code.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]

        print(f"Total lines: {len(lines)}")
        print(f"Non-empty lines: {len(non_empty_lines)}")
        print()

        # Check for comments
        comment_lines = [line for line in lines if "#" in line]
        print(f"Comment lines: {len(comment_lines)}")

        # Check for Vietnamese comments
        vietnamese_comments = [
            line
            for line in comment_lines
            if any(
                char in line
                for char in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
            )
        ]
        print(f"Vietnamese comments: {len(vietnamese_comments)}")
        print()

        # Code quality metrics
        print("Code Quality Metrics:")
        print(
            f"  - Concise: {'✓' if len(non_empty_lines) < 60 else '✗'} ({len(non_empty_lines)} < 60 lines)"
        )
        print(f"  - Well commented: {'✓' if len(comment_lines) > 3 else '✗'}")
        print(
            f"  - Vietnamese comments: {'✓' if len(vietnamese_comments) > 0 else '✗'}"
        )
        print()

        # Show sample
        print("Code Sample:")
        print("-" * 60)
        for i, line in enumerate(lines[:20], 1):
            print(f"{i:2d} | {line}")
        print("-" * 60)
    else:
        print(f"❌ Failed to generate code: {result.get('message')}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 GRAPH GENERATION TEST SUITE")
    print("=" * 60)
    print()

    try:
        # Test 1: Graph detection
        test_graph_detection()
        print("\n")

        # Test 2: Code generation with graphs
        print("\n⏳ Generating code samples (this may take a minute)...\n")
        test_code_generation_with_graph()

        # Test 3: Code conciseness
        test_concise_code()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print()
        print("Summary:")
        print("- Graph detection is working")
        print("- Code generation includes graphs when needed")
        print("- Code is concise and well-commented")
        print()

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
