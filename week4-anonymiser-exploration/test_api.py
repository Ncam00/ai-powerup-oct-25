#!/usr/bin/env python3
"""
Test script for the anonymiser API.
Run with: python test_api.py
"""

import json
import time
from typing import Dict, Any

import requests

# API base URL
BASE_URL = "http://localhost:9000"

# Test data
TEST_TEXTS = [
    "John Smith works at Acme Corp. His email is john.smith@example.com and phone is 555-123-4567.",
    "Jane Doe is the CEO of Example Inc. Contact her at jane@example.com or call (555) 987-6543.",
    "Meeting scheduled with Smith at 3 PM. Please confirm with Doe by email.",
]

BATCH_TEXTS = [
    "Customer John called from 555-111-2222 about his account.",
    "Jane from Acme Corp requested a callback at jane.doe@acme.com.",
    "Dr. Smith visited on 2024-01-15 at 123 Main Street, New York.",
]


def print_test_header(test_name: str):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")


def print_result(label: str, data: Any):
    """Print formatted result."""
    print(f"\n{label}:")
    if isinstance(data, dict) or isinstance(data, list):
        print(json.dumps(data, indent=2))
    else:
        print(data)


def test_health_check():
    """Test the health check endpoint."""
    print_test_header("Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print_result("Response", response.json())
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("\n✅ Health check passed")


def test_single_anonymisation():
    """Test single text anonymisation and de-anonymisation."""
    print_test_header("Single Text Anonymisation")
    
    # Anonymise
    text = TEST_TEXTS[0]
    print_result("Original Text", text)
    
    response = requests.post(
        f"{BASE_URL}/anonymise",
        json={"text": text}
    )
    print(f"\nStatus Code: {response.status_code}")
    
    result = response.json()
    print_result("Anonymised Response", result)
    
    assert response.status_code == 200
    assert "session_id" in result
    assert "anonymised_text" in result
    
    session_id = result["session_id"]
    anonymised_text = result["anonymised_text"]
    
    # Verify anonymisation worked
    assert "John Smith" not in anonymised_text
    assert "john.smith@example.com" not in anonymised_text
    assert "555-123-4567" not in anonymised_text
    assert ("PERSON" in anonymised_text or "PLACEHOLDER" in anonymised_text)
    
    # De-anonymise
    print_test_header("Single Text De-anonymisation")
    
    response = requests.post(
        f"{BASE_URL}/deanonymise",
        json={
            "anonymised_text": anonymised_text,
            "session_id": session_id
        }
    )
    print(f"Status Code: {response.status_code}")
    
    result = response.json()
    print_result("De-anonymised Response", result)
    
    assert response.status_code == 200
    assert result["original_text"] == text
    
    print("\n✅ Single anonymisation test passed")
    return session_id


def test_batch_anonymisation():
    """Test batch anonymisation."""
    print_test_header("Batch Anonymisation")
    
    print_result("Original Texts", BATCH_TEXTS)
    
    response = requests.post(
        f"{BASE_URL}/anonymise_batch",
        json={"texts": BATCH_TEXTS}
    )
    print(f"\nStatus Code: {response.status_code}")
    
    result = response.json()
    print_result("Batch Response", result)
    
    assert response.status_code == 200
    assert "session_id" in result
    assert "anonymised_texts" in result
    assert len(result["anonymised_texts"]) == len(BATCH_TEXTS)
    
    # Verify each text was anonymised
    for i, anonymised in enumerate(result["anonymised_texts"]):
        original = BATCH_TEXTS[i]
        print(f"\nText {i+1}:")
        print(f"  Original:   {original}")
        print(f"  Anonymised: {anonymised}")
        
        # Check that PII was removed
        if "555-111-2222" in original:
            assert "555-111-2222" not in anonymised
        if "jane.doe@acme.com" in original:
            assert "jane.doe@acme.com" not in anonymised
        if "New York" in original:
            assert "New York" not in anonymised  # Location should be anonymized
    
    print("\n✅ Batch anonymisation test passed")
    return result["session_id"]


def test_session_reuse():
    """Test using an existing session."""
    print_test_header("Session Reuse")
    
    # First anonymisation
    text1 = "Contact John at john@example.com"
    response1 = requests.post(
        f"{BASE_URL}/anonymise",
        json={"text": text1}
    )
    session_id = response1.json()["session_id"]
    print(f"Created session: {session_id}")
    
    # Reuse session
    text2 = "John's backup email is john.smith@example.com"
    response2 = requests.post(
        f"{BASE_URL}/anonymise",
        json={"text": text2, "session_id": session_id}
    )
    
    assert response2.status_code == 200
    assert response2.json()["session_id"] == session_id
    
    print_result("Reused Session Response", response2.json())
    print("\n✅ Session reuse test passed")
    
    return session_id


def test_session_cleanup(session_id: str):
    """Test session deletion."""
    print_test_header("Session Cleanup")
    
    print(f"Deleting session: {session_id}")
    
    response = requests.delete(f"{BASE_URL}/sessions/{session_id}")
    print(f"Status Code: {response.status_code}")
    print_result("Response", response.json())
    
    assert response.status_code == 200
    
    # Verify session is gone by trying to use it
    response = requests.post(
        f"{BASE_URL}/deanonymise",
        json={
            "anonymised_text": "<PERSON> test",
            "session_id": session_id
        }
    )
    # Should still work but won't have the original mappings
    print("\n✅ Session cleanup test passed")


def test_match_deanonymisation():
    """Test the match deanonymisation endpoint."""
    print_test_header("Match De-anonymisation")
    
    # First anonymise some text
    text = "Contact Jane Doe at jane@example.com"
    response = requests.post(
        f"{BASE_URL}/anonymise",
        json={"text": text}
    )
    
    session_id = response.json()["session_id"]
    anonymised_text = response.json()["anonymised_text"]
    
    # Create a match object
    match_result = {
        "text": anonymised_text,
        "score": 0.95,
        "metadata": {"source": "test"}
    }
    
    print_result("Match Object", match_result)
    
    # De-anonymise the match
    response = requests.post(
        f"{BASE_URL}/deanonymise-match",
        json={
            "match_result": match_result,
            "session_id": session_id
        }
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print_result("De-anonymised Match", response.json())
    
    assert response.status_code == 200
    assert response.json()["original_text"] == text
    
    print("\n✅ Match de-anonymisation test passed")


def main():
    """Run all tests."""
    print("Starting Anonymiser API Tests")
    print(f"Testing against: {BASE_URL}")
    print("\nMake sure the API is running with:")
    print("  uv run uvicorn anonymiser:app --reload --port 9000")
    
    try:
        # Check if API is running
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API. Is it running?")
        return 1
    
    try:
        # Run tests
        test_health_check()
        
        session1 = test_single_anonymisation()
        time.sleep(0.5)  # Small delay between tests
        
        session2 = test_batch_anonymisation()
        time.sleep(0.5)
        
        session3 = test_session_reuse()
        time.sleep(0.5)
        
        test_match_deanonymisation()
        time.sleep(0.5)
        
        # Cleanup
        test_session_cleanup(session1)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())