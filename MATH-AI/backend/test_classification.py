#!/usr/bin/env python3
"""
Test script for input classification
Tests the AI service's ability to classify different types of user input
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_classification(input_text: str):
    """Test classification for a given input"""
    print(f"\n{'=' * 60}")
    print(f"Input: {input_text}")
    print(f"{'=' * 60}")

    result = ai_service.classify_input(input_text)

    print(f"Is Math: {result.get('is_math')}")
    print(f"Content Type: {result.get('content_type')}")
    print(f"Suggested Action: {result.get('suggested_action')}")
    print(f"Confidence: {result.get('confidence')}")
    print(f"Reason: {result.get('reason')}")

    return result


def main():
    """Run classification tests"""
    print("\n🧪 Testing Input Classification System")
    print("=" * 60)

    test_cases = [
        # Greetings
        "Hi",
        "Hello",
        "Xin chào",
        "Chào bạn",
        # Casual conversation
        "Bạn là ai?",
        "Help me",
        "What can you do?",
        "Bạn có thể làm gì?",
        # Math questions (concepts)
        "Đạo hàm là gì?",
        "What is derivative?",
        "Giải thích tích phân",
        "Explain integration",
        # Math problems (simple)
        "Giải x^2 + 1 = 0",
        "Solve x + 2 = 5",
        "Tính 2 + 2",
        "Calculate 5 * 3",
        # Math problems (complex)
        "Giải phương trình lượng giác 2sin(x) + cos(x) = 1",
        "Tính tích phân của x^2 từ 0 đến 1",
        "Find the derivative of sin(x) * cos(x)",
        "Tìm cực trị của hàm số y = x^3 - 3x + 1",
        # Unclear
        "abc",
        "123",
        "???",
    ]

    results = []
    for test_input in test_cases:
        result = test_classification(test_input)
        results.append(
            {
                "input": test_input,
                "is_math": result.get("is_math"),
                "content_type": result.get("content_type"),
                "suggested_action": result.get("suggested_action"),
            }
        )

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    print("\n📊 Distribution by Content Type:")
    content_types = {}
    for r in results:
        ct = r["content_type"]
        content_types[ct] = content_types.get(ct, 0) + 1

    for ct, count in sorted(content_types.items()):
        print(f"  {ct}: {count}")

    print("\n🎯 Distribution by Suggested Action:")
    actions = {}
    for r in results:
        action = r["suggested_action"]
        actions[action] = actions.get(action, 0) + 1

    for action, count in sorted(actions.items()):
        print(f"  {action}: {count}")

    print("\n✅ Math vs Non-Math:")
    math_count = sum(1 for r in results if r["is_math"])
    non_math_count = len(results) - math_count
    print(f"  Math content: {math_count}/{len(results)}")
    print(f"  Non-math content: {non_math_count}/{len(results)}")

    # Test chat response for non-math input
    print(f"\n{'=' * 60}")
    print("Testing Chat Response Generation")
    print(f"{'=' * 60}")

    chat_test_cases = [
        "Hi",
        "Xin chào",
        "Bạn có thể giúp gì?",
    ]

    for test_input in chat_test_cases:
        print(f"\nInput: {test_input}")
        chat_result = ai_service.chat_response(test_input)
        if chat_result["success"]:
            print(f"Response: {chat_result['response']}")
        else:
            print(f"Error: {chat_result.get('error')}")

    print(f"\n{'=' * 60}")
    print("✅ All tests completed!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
