#!/usr/bin/env python3
"""Test the Lambda handler locally before deploying."""

import json
import sys
import os

# Add lambda_handler to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda_handler'))

from handler import lambda_handler


def test_success_case():
    """Test successful classification."""
    event = {
        'body': json.dumps({
            'transcript': 'Speaker 0: Good afternoon, thank you for calling Premier Plumbing Services, this is Jennifer speaking. May I have your phone number please?\nSpeaker 1: Hi Jennifer, yes it\'s 555-0147.\nSpeaker 0: Thank you. I see you\'re calling from the number on file for Riverside Apartments. Is this Mr. Chen, the building manager?\nSpeaker 1: Yes, that\'s correct. We have an emergency situation in one of our units.'
        })
    }
    
    response = lambda_handler(event, None)
    
    print("Test: Success Case")
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Response: {json.dumps(body, indent=2)}")
    print()
    
    assert response['statusCode'] == 200
    assert 'result' in body
    assert 'Agent:' in body['result']
    assert 'Customer:' in body['result']
    print("✅ PASSED\n")


def test_missing_transcript():
    """Test missing transcript field."""
    event = {
        'body': json.dumps({})
    }
    
    response = lambda_handler(event, None)
    
    print("Test: Missing Transcript")
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Response: {json.dumps(body, indent=2)}")
    print()
    
    assert response['statusCode'] == 400
    assert 'error' in body
    print("✅ PASSED\n")


def test_empty_transcript():
    """Test empty transcript."""
    event = {
        'body': json.dumps({
            'transcript': ''
        })
    }
    
    response = lambda_handler(event, None)
    
    print("Test: Empty Transcript")
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Response: {json.dumps(body, indent=2)}")
    print()
    
    assert response['statusCode'] == 400
    assert 'error' in body
    print("✅ PASSED\n")


def test_direct_invocation():
    """Test direct invocation format (no 'body' wrapper)."""
    event = {
        'transcript': 'Speaker 0: Good afternoon, thank you for calling Premier Plumbing Services.\nSpeaker 1: Hi, I need emergency service for a backed up sink.'
    }
    
    response = lambda_handler(event, None)
    
    print("Test: Direct Invocation")
    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Response: {json.dumps(body, indent=2)}")
    print()
    
    assert response['statusCode'] == 200
    assert 'result' in body
    print("✅ PASSED\n")


if __name__ == '__main__':
    print("Testing Lambda Handler Locally\n")
    print("=" * 50)
    print()
    
    try:
        test_success_case()
        test_missing_transcript()
        test_empty_transcript()
        test_direct_invocation()
        
        print("=" * 50)
        print("All tests passed! ✅")
        print("\nThe Lambda handler is working correctly.")
        print("You can now deploy with: cd infrastructure && cdk deploy")
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

