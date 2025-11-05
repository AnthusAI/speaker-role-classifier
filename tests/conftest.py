"""Test fixtures for speaker role classifier tests."""

import pytest


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

