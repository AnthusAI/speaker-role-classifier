"""Pytest configuration and shared fixtures."""

import pytest
import os
from unittest.mock import Mock, patch
import json


@pytest.fixture(scope="session")
def use_real_api():
    """
    Determine whether to use real OpenAI API calls or mocks.
    Set REAL_API_TESTS=1 environment variable to use real API.
    """
    return os.getenv('REAL_API_TESTS', '0') == '1'


@pytest.fixture
def context():
    """Provide a context dictionary for sharing state between steps."""
    return {}


# Mock fixtures for OpenAI responses (used by classification tests)
@pytest.fixture
def mock_api_response():
    """Standard mock API response for two-speaker classification."""
    return {
        "Speaker 0": "Agent",
        "Speaker 1": "Customer"
    }


@pytest.fixture
def incomplete_mapping_response():
    """Mock API response with incomplete mapping."""
    return {
        "Speaker 0": "Agent"
    }


@pytest.fixture
def wrong_speaker_mapping_response():
    """Mock API response with non-existent speaker."""
    return {
        "Speaker 0": "Agent",
        "Speaker 1": "Customer",
        "Speaker 5": "Customer"
    }


# Safeguard mock fixtures
def create_mock_openai_no_corrections():
    """Create a mock OpenAI client that returns no corrections needed."""
    mock_client = Mock()
    mock_response = Mock()
    mock_message = Mock()
    mock_message.tool_calls = None
    mock_message.content = "The classification looks correct. No corrections needed."
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


def create_mock_openai_single_correction():
    """Create a mock OpenAI client that makes one correction."""
    mock_client = Mock()
    
    # First call: LLM identifies one issue and calls tool
    mock_tool_call = Mock()
    mock_tool_call.id = "call_123"
    mock_tool_call.function.name = "correct_speaker_role"
    mock_tool_call.function.arguments = json.dumps({
        "current_role": "Customer",
        "utterance_prefix": "Of course, Mr. Chen. I have",
        "correct_role": "Agent",
        "reason": "This is clearly the agent responding professionally"
    })
    
    mock_message1 = Mock()
    mock_message1.tool_calls = [mock_tool_call]
    mock_message1.content = None
    
    mock_choice1 = Mock()
    mock_choice1.message = mock_message1
    
    mock_response1 = Mock()
    mock_response1.choices = [mock_choice1]
    
    # Second call: LLM confirms no more corrections needed
    mock_message2 = Mock()
    mock_message2.tool_calls = None
    mock_message2.content = "All corrections completed. The classification is now accurate."
    
    mock_choice2 = Mock()
    mock_choice2.message = mock_message2
    
    mock_response2 = Mock()
    mock_response2.choices = [mock_choice2]
    
    mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]
    return mock_client


def create_mock_openai_multiple_corrections():
    """Create a mock OpenAI client that makes multiple corrections."""
    mock_client = Mock()
    
    # First call: LLM identifies first issue
    mock_tool_call1 = Mock()
    mock_tool_call1.id = "call_1"
    mock_tool_call1.function.name = "correct_speaker_role"
    mock_tool_call1.function.arguments = json.dumps({
        "current_role": "Customer",
        "utterance_prefix": "Good afternoon, thank you for calling",
        "correct_role": "Agent",
        "reason": "Agent greets the customer"
    })
    
    mock_message1 = Mock()
    mock_message1.tool_calls = [mock_tool_call1]
    mock_message1.content = None
    
    mock_choice1 = Mock()
    mock_choice1.message = mock_message1
    
    mock_response1 = Mock()
    mock_response1.choices = [mock_choice1]
    
    # Second call: LLM identifies second issue
    mock_tool_call2 = Mock()
    mock_tool_call2.id = "call_2"
    mock_tool_call2.function.name = "correct_speaker_role"
    mock_tool_call2.function.arguments = json.dumps({
        "current_role": "Agent",
        "utterance_prefix": "Hi Sarah, this is Tom Chen",
        "correct_role": "Customer",
        "reason": "Customer introduces themselves"
    })
    
    mock_message2 = Mock()
    mock_message2.tool_calls = [mock_tool_call2]
    mock_message2.content = None
    
    mock_choice2 = Mock()
    mock_choice2.message = mock_message2
    
    mock_response2 = Mock()
    mock_response2.choices = [mock_choice2]
    
    # Third call: No more corrections
    mock_message3 = Mock()
    mock_message3.tool_calls = None
    mock_message3.content = "All corrections completed."
    
    mock_choice3 = Mock()
    mock_choice3.message = mock_message3
    
    mock_response3 = Mock()
    mock_response3.choices = [mock_choice3]
    
    mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2, mock_response3]
    return mock_client


@pytest.fixture
def mock_openai_safeguard_no_corrections():
    """Fixture for safeguard that finds no issues."""
    return create_mock_openai_no_corrections()


@pytest.fixture
def mock_openai_safeguard_single_correction():
    """Fixture for safeguard that makes one correction."""
    return create_mock_openai_single_correction()


@pytest.fixture
def mock_openai_safeguard_multiple_corrections():
    """Fixture for safeguard that makes multiple corrections."""
    return create_mock_openai_multiple_corrections()


@pytest.fixture
def maybe_mock_safeguard(use_real_api):
    """
    Context manager that conditionally mocks the safeguard OpenAI client.
    If REAL_API_TESTS=1, returns a no-op context manager.
    Otherwise, returns a patch that can be configured with a mock client.
    """
    class MaybeMock:
        def __init__(self, should_mock):
            self.should_mock = should_mock
            self.patcher = None
            
        def __call__(self, mock_client=None):
            if not self.should_mock:
                # Return a no-op context manager for real API
                from contextlib import nullcontext
                return nullcontext()
            else:
                # Return a patch with the provided mock
                if mock_client is None:
                    mock_client = create_mock_openai_no_corrections()
                return patch('speaker_role_classifier.safeguard.OpenAI', return_value=mock_client)
    
    return MaybeMock(not use_real_api)


@pytest.fixture
def maybe_mock_classifier(use_real_api):
    """
    Context manager that conditionally mocks the classifier OpenAI calls.
    If REAL_API_TESTS=1, returns a no-op context manager.
    Otherwise, returns a patch for the classifier's API call.
    """
    class MaybeMock:
        def __init__(self, should_mock):
            self.should_mock = should_mock
            
        def __call__(self, mock_response=None):
            if not self.should_mock:
                from contextlib import nullcontext
                return nullcontext()
            else:
                if mock_response is None:
                    mock_response = {"Speaker 0": "Agent", "Speaker 1": "Customer"}
                return patch('speaker_role_classifier.classifier._call_gpt5_api', return_value=mock_response)
    
    return MaybeMock(not use_real_api)
