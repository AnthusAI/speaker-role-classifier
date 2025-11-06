"""Test fixtures for speaker role classifier tests."""

import pytest
import os
import json
from unittest.mock import Mock


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests that call real APIs (deselect with '-m \"not integration\"')"
    )


@pytest.fixture(autouse=True)
def mock_openai_by_default(monkeypatch, request):
    """Mock OpenAI API calls by default unless test is marked as integration."""
    # Skip mocking if test is marked as integration
    if 'integration' in request.keywords:
        return
    
    # Create a smart mock that responds based on the prompt
    def mock_create(**kwargs):
        """Smart mock that extracts target roles from the prompt."""
        messages = kwargs.get('messages', [])
        
        # Default roles
        roles = ["Agent", "Customer"]
        
        # Try to extract target_roles from the system message
        # System message format: "...these roles: Sales and Lead" or "...these roles: Agent and Customer"
        for msg in messages:
            if msg.get('role') == 'system':
                content = msg.get('content', '')
                # Look for "these roles: X and Y" pattern
                import re
                role_match = re.search(r'these roles:\s*([^.]+)', content)
                if role_match:
                    role_str = role_match.group(1).strip()
                    # Split by "and" to get individual roles
                    found_roles = [r.strip() for r in role_str.split(' and ')]
                    if found_roles and all(found_roles):
                        roles = found_roles
        
        # Try to extract user message for speaker detection
        user_msg = None
        for msg in messages:
            if msg.get('role') == 'user':
                user_msg = msg.get('content', '')
                break
        
        # Extract speaker labels from transcript
        speakers = []
        if user_msg:
            import re
            # Match "Speaker N" or role names (Agent, Customer, etc.) but not full sentences
            speaker_pattern = r'^(Speaker \d+|Agent|Customer|Sales|Lead|Caller|Unknown):'
            for line in user_msg.split('\n'):
                line = line.strip()
                if not line or line.startswith('Example') or line.startswith('Here is'):
                    continue
                match = re.match(speaker_pattern, line)
                if match:
                    speaker = match.group(1).strip()
                    if speaker not in speakers:
                        speakers.append(speaker)
        
        # Default to Speaker 0, Speaker 1 if not found
        if not speakers:
            speakers = ["Speaker 0", "Speaker 1"]
        
        # Create mapping: alternate speakers to roles
        mapping = {}
        for i, speaker in enumerate(speakers):
            mapping[speaker] = roles[i % len(roles)]
        
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content=json.dumps(mapping)))]
        return mock_completion
    
    # Mock the OpenAI client
    mock_client = Mock()
    mock_client.chat.completions.create = mock_create
    
    # Patch the OpenAI client creation
    from unittest.mock import patch
    with patch('speaker_role_classifier.classifier.OpenAI', return_value=mock_client):
        yield mock_client


@pytest.fixture
def context():
    """Shared context dictionary for BDD tests."""
    return {}


@pytest.fixture
def simple_transcript():
    """A simple two-speaker transcript."""
    return """Speaker 0: Hello, thanks for calling ABC Plumbing Services, how may I help you?
Speaker 1: Hi, I have a big emergency! My faucet broke and it's flowing and it won't stop!"""


@pytest.fixture
def multiline_transcript():
    """A transcript with multiple lines per speaker."""
    return """Speaker 0: Hello, thanks for calling ABC Plumbing Services, how may I help you?
Speaker 1: Hi, I have a big emergency! My faucet broke and it's flowing and it won't stop!
Speaker 0: I understand, that sounds stressful. Let me help you with that.
Speaker 1: Thank you so much! I really appreciate it."""


@pytest.fixture
def three_speaker_transcript():
    """A transcript with three speakers."""
    return """Speaker 0: Hello, thanks for calling ABC Plumbing Services.
Speaker 1: Hi, I need help.
Speaker 2: I'm also on the line."""


@pytest.fixture
def formatted_transcript():
    """A transcript with specific formatting to preserve."""
    return """Speaker 0: Hello, thanks for calling ABC Plumbing Services, how may I help you?

Speaker 1: Hi, I have a big emergency! My faucet broke and it's flowing and it won't stop!"""


@pytest.fixture
def valid_api_response():
    """A valid API response mapping speakers to roles."""
    return {
        "Speaker 0": "Agent",
        "Speaker 1": "Customer"
    }


@pytest.fixture
def malformed_json_response():
    """A malformed JSON response."""
    return "This is not valid JSON {{"


@pytest.fixture
def incomplete_mapping_response():
    """An API response that doesn't map all speakers."""
    return {
        "Speaker 0": "Agent"
        # Missing Speaker 1
    }


@pytest.fixture
def wrong_speaker_mapping_response():
    """An API response that maps a non-existent speaker."""
    return {
        "Speaker 0": "Agent",
        "Speaker 1": "Customer",
        "Speaker 5": "Customer"  # Speaker 5 doesn't exist
    }


@pytest.fixture
def expected_output():
    """Expected output for simple transcript."""
    return """Agent: Hello, thanks for calling ABC Plumbing Services, how may I help you?
Customer: Hi, I have a big emergency! My faucet broke and it's flowing and it won't stop!"""


@pytest.fixture
def expected_multiline_output():
    """Expected output for multiline transcript."""
    return """Agent: Hello, thanks for calling ABC Plumbing Services, how may I help you?
Customer: Hi, I have a big emergency! My faucet broke and it's flowing and it won't stop!
Agent: I understand, that sounds stressful. Let me help you with that.
Customer: Thank you so much! I really appreciate it."""


@pytest.fixture
def expected_formatted_output():
    """Expected output for formatted transcript."""
    return """Agent: Hello, thanks for calling ABC Plumbing Services, how may I help you?

Customer: Hi, I have a big emergency! My faucet broke and it's flowing and it won't stop!"""

