#!/usr/bin/env python3
"""
Test script to verify video length and animation quality
Tests that generated videos are long enough to see graphs properly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import ai_service


def test_video_length_requirements():
    """Test if generated code has proper wait times"""
    print("=" * 70)
    print("⏱️  TESTING VIDEO LENGTH REQUIREMENTS")
    print("=" * 70)
    print()

    test_cases = [
        {
            "title": "Parabol với đồ thị",
            "text": "Vẽ đồ thị hàm số y = x^2 - 4x + 3",
            "context": "Tìm đỉnh và giao điểm với trục",
            "min_waits": 3,  # Số lượng self.wait() tối thiểu
            "min_total_wait": 10,  # Tổng thời gian wait tối thiểu (giây)
        },
        {
            "title": "Hàm bậc nhất",
            "text": "Vẽ đồ thị y = 2x + 1",
            "context": "Hiển thị hệ số góc và tung độ gốc",
            "min_waits": 3,
            "min_total_wait": 8,
        },
        {
            "title": "Giải phương trình",
            "text": "Giải phương trình 2x + 5 = 15",
            "context": "",
            "min_waits": 3,
            "min_total_wait": 6,
        },
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"Test {i}/{len(test_cases)}: {test['title']}")
        print("=" * 70)
        print(f"Problem: {test['text']}")
        print(f"Context: {test['context'] or 'None'}")
        print()

        # Generate code
        result = ai_service.generate_manim_code(test["text"], test["context"])

        if not result["success"]:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
            results.append({"test": test["title"], "passed": False})
            continue

        code = result["code"]
        lines = code.split("\n")

        print(f"✅ Code generated successfully")
        print(f"   Provider: {result.get('provider', 'N/A')}")
        print(f"   Lines: {len(lines)}")
        print()

        # Analyze wait times
        wait_lines = [l for l in lines if "self.wait(" in l]
        wait_times = []

        for line in wait_lines:
            try:
                # Extract wait time from self.wait(X)
                if "self.wait(" in line:
                    start = line.find("self.wait(") + len("self.wait(")
                    end = line.find(")", start)
                    wait_str = line[start:end].strip()
                    if wait_str:
                        wait_time = float(wait_str)
                        wait_times.append(wait_time)
                    else:
                        wait_times.append(1.0)  # Default wait
            except:
                wait_times.append(1.0)

        total_wait_time = sum(wait_times)
        num_waits = len(wait_lines)

        print("⏱️  Wait Time Analysis:")
        print("-" * 70)
        print(f"   Number of wait() calls: {num_waits}")
        print(f"   Total wait time: {total_wait_time:.1f} seconds")
        print(f"   Wait times: {[f'{w:.1f}s' for w in wait_times]}")
        print()

        # Check run_time parameters
        run_time_lines = [l for l in lines if "run_time=" in l]
        run_times = []

        for line in run_time_lines:
            try:
                start = line.find("run_time=") + len("run_time=")
                # Find the next comma or closing paren
                rest = line[start:]
                end = min(
                    [i for i, c in enumerate(rest) if c in [",", ")", "\n"] if i > 0]
                    or [len(rest)]
                )
                run_time_str = rest[:end].strip()
                run_time = float(run_time_str)
                run_times.append(run_time)
            except:
                pass

        total_run_time = sum(run_times)

        if run_time_lines:
            print("🎬 Animation run_time Analysis:")
            print("-" * 70)
            print(f"   Number of run_time parameters: {len(run_times)}")
            print(f"   Total run_time: {total_run_time:.1f} seconds")
            print(f"   Run times: {[f'{r:.1f}s' for r in run_times]}")
            print()

        # Estimate total video length
        estimated_length = total_wait_time + total_run_time
        print(f"📹 Estimated Video Length: {estimated_length:.1f} seconds")
        print()

        # Check requirements
        meets_waits = num_waits >= test["min_waits"]
        meets_duration = total_wait_time >= test["min_total_wait"]

        print("✅ Requirements Check:")
        print("-" * 70)
        status_waits = "✓" if meets_waits else "✗"
        status_duration = "✓" if meets_duration else "✗"

        print(f"   {status_waits} Number of waits: {num_waits} >= {test['min_waits']}")
        print(
            f"   {status_duration} Total wait time: {total_wait_time:.1f}s >= {test['min_total_wait']}s"
        )

        # Check for graph if needed
        if "đồ thị" in test["text"].lower() or "graph" in test["text"].lower():
            has_axes = "Axes(" in code
            has_graph = "get_graph" in code
            has_create_graph = (
                "Create(graph" in code or "self.play(Create(graph" in code
            )
            long_wait_after_graph = any(w >= 3 for w in wait_times)

            print()
            print("📊 Graph Requirements (for graph problems):")
            print("-" * 70)
            print(f"   {'✓' if has_axes else '✗'} Has Axes")
            print(f"   {'✓' if has_graph else '✗'} Has get_graph")
            print(f"   {'✓' if has_create_graph else '✗'} Animates graph creation")
            print(
                f"   {'✓' if long_wait_after_graph else '✗'} Has long wait (≥3s) for viewing graph"
            )

            graph_ok = has_axes and has_graph and long_wait_after_graph
        else:
            graph_ok = True

        # Overall result
        passed = meets_waits and meets_duration and graph_ok

        print()
        if passed:
            print("✅ PASSED - Video will be long enough to see everything")
        else:
            print("❌ FAILED - Video might be too short")
            if not meets_waits:
                print(
                    f"   → Need more wait() calls (have {num_waits}, need {test['min_waits']})"
                )
            if not meets_duration:
                print(
                    f"   → Need longer wait times (have {total_wait_time:.1f}s, need {test['min_total_wait']}s)"
                )
            if not graph_ok:
                print(
                    "   → Graph needs longer viewing time (use self.wait(4) after graph)"
                )

        results.append({"test": test["title"], "passed": passed})

        # Show code preview
        if not passed:
            print()
            print("📄 Code Preview (to debug):")
            print("=" * 70)
            for j, line in enumerate(lines[:35], 1):
                marker = ""
                if "self.wait(" in line:
                    marker = "  ← WAIT"
                elif "run_time=" in line:
                    marker = "  ← RUN_TIME"
                print(f"{j:3d} | {line}{marker}")
            if len(lines) > 35:
                print(f"... ({len(lines) - 35} more lines)")
            print("=" * 70)

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print()

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    print(f"Tests run: {total_count}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {total_count - passed_count}")
    print()

    for r in results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"  {status} - {r['test']}")

    print()
    print("=" * 70)

    if passed_count == total_count:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Videos will be long enough to see:")
        print("  ✓ All problem-solving steps")
        print("  ✓ Graphs being drawn")
        print("  ✓ Final results clearly")
    else:
        print(f"⚠️  {total_count - passed_count} test(s) failed")
        print()
        print("Recommendations:")
        print("  1. Increase self.wait() times (use 2-4 seconds)")
        print("  2. Add run_time parameters to animations")
        print("  3. Use self.wait(4) after drawing graphs")
        print("  4. Ensure at least 15-20 seconds total video length")

    print("=" * 70)
    print()

    return passed_count == total_count


if __name__ == "__main__":
    success = test_video_length_requirements()
    sys.exit(0 if success else 1)
