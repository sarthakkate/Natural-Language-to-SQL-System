"""
Test Script for NL2SQL System
Runs the 20 test questions and validates responses
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# Configuration
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# Test questions
TEST_QUESTIONS = [
    "How many patients do we have?",
    "List all doctors and their specializations",
    "Show me appointments for last month",
    "Which doctor has the most appointments?",
    "What is the total revenue?",
    "Show revenue by doctor",
    "How many cancelled appointments last quarter?",
    "Top 5 patients by spending",
    "Average treatment cost by specialization",
    "Show monthly appointment count for the past 6 months",
    "Which city has the most patients?",
    "List patients who visited more than 3 times",
    "Show unpaid invoices",
    "What percentage of appointments are no-shows?",
    "Show the busiest day of the week for appointments",
    "Revenue trend by month",
    "Average appointment duration by doctor",
    "List patients with overdue invoices",
    "Compare revenue between departments",
    "Show patient registration trend by month",
]


def check_api_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API Status: {data['status']}")
            print(f"  Database: {data['database']}")
            print(f"  Memory Items: {data['agent_memory_items']}")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Is the server running on port 8000?")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_question(question: str, question_num: int) -> Tuple[bool, Dict]:
    """Test a single question"""
    try:
        start_time = time.time()
        
        response = requests.post(
            CHAT_ENDPOINT,
            json={"question": question},
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return True, {
                "status": "PASS",
                "time": elapsed,
                "rows": data.get("row_count", 0),
                "sql": data.get("sql_query", "N/A")[:100],
                "has_chart": data.get("chart") is not None
            }
        else:
            return False, {
                "status": "FAIL",
                "time": elapsed,
                "error": response.json().get("error", "Unknown error")
            }
    
    except requests.exceptions.Timeout:
        return False, {
            "status": "TIMEOUT",
            "error": "Request timed out (>30s)"
        }
    
    except Exception as e:
        return False, {
            "status": "ERROR",
            "error": str(e)
        }


def run_tests():
    """Run all test questions"""
    print("\n" + "="*70)
    print("  NL2SQL System - Test Suite")
    print("="*70 + "\n")
    
    # Check API health
    print("Checking API Health...")
    if not check_api_health():
        print("\n✗ API is not available. Please start the server first:")
        print("  uvicorn main:app --port 8000")
        return
    
    print("\n" + "="*70)
    print("Running 20 Test Questions...")
    print("="*70 + "\n")
    
    results: List[Tuple[int, str, bool, Dict]] = []
    passed = 0
    failed = 0
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"[{i:2d}/20] {question[:60]}...", end=" ", flush=True)
        
        success, result = test_question(question, i)
        
        if success:
            print(f"✅ ({result['time']:.2f}s, {result['rows']} rows)")
            passed += 1
        else:
            print(f"❌ ({result.get('error', 'Unknown error')})")
            failed += 1
        
        results.append((i, question, success, result))
        
        # Small delay to avoid overwhelming API
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "="*70)
    print("  Test Summary")
    print("="*70)
    
    print(f"\nTotal Tests: {len(TEST_QUESTIONS)}")
    print(f"Passed:      {passed}/{len(TEST_QUESTIONS)} ({100*passed/len(TEST_QUESTIONS):.1f}%)")
    print(f"Failed:      {failed}/{len(TEST_QUESTIONS)}")
    
    # Print failures
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        for i, question, success, result in results:
            if not success:
                print(f"  [{i:2d}] {question[:50]}")
                if "error" in result:
                    print(f"       Error: {result['error'][:60]}")
    
    # Print summary by category
    print("\n✅ Detailed Results:")
    print("-" * 70)
    print(f"{'#':<3} {'Question':<50} {'Status':<8} {'Time':<8} {'Rows':<6}")
    print("-" * 70)
    
    for i, question, success, result in results:
        status = "PASS" if success else "FAIL"
        time_str = f"{result.get('time', 0):.2f}s" if 'time' in result else "N/A"
        rows_str = str(result.get('rows', '?'))
        
        print(f"{i:<3} {question[:47]:<50} {status:<8} {time_str:<8} {rows_str:<6}")
    
    print("-" * 70)
    
    # Export results
    export_results(results)


def export_results(results: List[Tuple[int, str, bool, Dict]]):
    """Export results to JSON file"""
    export_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": len(results),
        "passed": sum(1 for _, _, success, _ in results if success),
        "failed": sum(1 for _, _, success, _ in results if not success),
        "results": [
            {
                "question_number": i,
                "question": question,
                "success": success,
                "details": result
            }
            for i, question, success, result in results
        ]
    }
    
    with open("test_results.json", "w") as f:
        json.dump(export_data, f, indent=2)
    
    print(f"\n✓ Results exported to test_results.json")


if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
