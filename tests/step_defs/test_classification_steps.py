"""Step definitions for speaker classification scenarios."""

import pytest
from pytest_bdd import scenarios, given, when, then
from unittest.mock import patch
from speaker_role_classifier.classifier import (
    classify_speakers,
    InvalidJSONResponseError,
    MissingSpeakerMappingError,
    SpeakerNotFoundError
)

# Load all scenarios from the feature file
scenarios('../features/speaker_classification.feature')


@pytest.fixture
def context():
    """Provide a context dictionary for sharing state between steps."""
    return {}


@pytest.fixture
def simple_transcript():
    """A simple two-speaker transcript."""
    return "Speaker 0: Hello, thanks for calling.\nSpeaker 1: Hi, I need help."


@pytest.fixture
def multiline_transcript():
    """A transcript with multiple lines per speaker."""
    return """Speaker 0: Hello, thanks for calling.
Speaker 1: Hi, I need help.
Speaker 0: Sure, what can I do for you?
Speaker 1: My account is locked."""


@pytest.fixture
def three_speaker_transcript():
    """A transcript with three speakers."""
    return """Speaker 0: Hello.
Speaker 1: Hi.
Speaker 2: Hey there."""


@pytest.fixture
def formatted_transcript():
    """A transcript with specific formatting."""
    return """Speaker 0: Hello, thanks for calling.

Speaker 1: Hi, I need help.

Speaker 0: Sure, what can I do for you?"""


@given('a standard diarized transcript')
def standard_transcript(simple_transcript, context):
    """Set up a standard transcript."""
    context['transcript'] = simple_transcript


@given('a diarized transcript with two speakers')
def diarized_transcript(simple_transcript, context):
    """Set up a diarized transcript."""
    context['transcript'] = simple_transcript


@given('a diarized transcript with multiple lines per speaker')
def multiline_transcript_given(multiline_transcript, context):
    """Set up a multi-line transcript."""
    context['transcript'] = multiline_transcript


@given('a diarized transcript with three speakers')
def three_speakers(three_speaker_transcript, context):
    """Set up a three-speaker transcript."""
    context['transcript'] = three_speaker_transcript


@given('a diarized transcript with specific formatting')
def formatted_transcript_given(formatted_transcript, context):
    """Set up a formatted transcript."""
    context['transcript'] = formatted_transcript


@given('the OpenAI API returns an invalid JSON response')
def api_returns_invalid_json(context):
    """Mock API to return invalid JSON."""
    context['transcript'] = "Speaker 0: Hello\nSpeaker 1: Hi"
    context['should_raise'] = InvalidJSONResponseError("Malformed JSON")


@given('the OpenAI API returns an incomplete speaker mapping')
def api_returns_incomplete_mapping(context):
    """Mock API to return incomplete mapping."""
    context['transcript'] = "Speaker 0: Hello\nSpeaker 1: Hi"
    context['mock_response'] = {"Speaker 0": "Agent"}


@given('the OpenAI API returns a mapping for a non-existent speaker')
def api_returns_wrong_speaker(context):
    """Mock API to return mapping for non-existent speaker."""
    context['transcript'] = "Speaker 0: Hello\nSpeaker 1: Hi"
    context['mock_response'] = {
        "Speaker 0": "Agent",
        "Speaker 1": "Customer",
        "Speaker 5": "Customer"
    }


@when('the classifier processes the transcript')
def process_transcript(context):
    """Process the transcript with mocked API."""
    with patch('speaker_role_classifier.classifier._call_gpt5_api') as mock_api:
        mock_api.return_value = {"Speaker 0": "Agent", "Speaker 1": "Customer"}
        try:
            result = classify_speakers(context['transcript'])
            context['result'] = result['transcript']
            context['error'] = None
        except Exception as e:
            context['error'] = e
            context['result'] = None


@when('the API returns malformed JSON')
def api_returns_malformed(context):
    """Process with mocked malformed JSON response."""
    with patch('speaker_role_classifier.classifier._call_gpt5_api') as mock_api:
        mock_api.side_effect = context.get('should_raise', InvalidJSONResponseError("Malformed JSON"))
        try:
            result = classify_speakers(context['transcript'])
            context['result'] = result['transcript']
            context['error'] = None
        except Exception as e:
            context['error'] = e
            context['result'] = None


@when('the API response does not map all speakers')
def api_incomplete_mapping(context):
    """Process with incomplete mapping."""
    with patch('speaker_role_classifier.classifier._call_gpt5_api') as mock_api:
        mock_api.return_value = context.get('mock_response', {"Speaker 0": "Agent"})
        try:
            result = classify_speakers(context['transcript'])
            context['result'] = result['transcript']
            context['error'] = None
        except Exception as e:
            context['error'] = e
            context['result'] = None


@when("the API response maps a speaker that doesn't exist")
def api_wrong_speaker(context):
    """Process with wrong speaker mapping."""
    with patch('speaker_role_classifier.classifier._call_gpt5_api') as mock_api:
        mock_response = context.get('mock_response', {
            "Speaker 0": "Agent",
            "Speaker 1": "Customer",
            "Speaker 5": "Customer"
        })
        mock_api.return_value = mock_response
        try:
            result = classify_speakers(context['transcript'])
            context['result'] = result['transcript']
            context['error'] = None
        except Exception as e:
            context['error'] = e
            context['result'] = None


@then('the output should label one speaker as "Agent"')
def check_agent_label(context):
    """Verify Agent label is present."""
    assert "Agent:" in context['result']


@then('the output should label the other speaker as "Customer"')
def check_customer_label(context):
    """Verify Customer label is present."""
    assert "Customer:" in context['result']


@then('all speaker labels should be replaced')
def check_all_replaced(context):
    """Verify all Speaker N labels are replaced."""
    assert "Speaker 0:" not in context['result']
    assert "Speaker 1:" not in context['result']


@then('an InvalidJSONResponseError should be raised')
def check_invalid_json_error(context):
    """Verify InvalidJSONResponseError was raised."""
    assert isinstance(context['error'], InvalidJSONResponseError)


@then('a MissingSpeakerMappingError should be raised')
def check_missing_mapping_error(context):
    """Verify MissingSpeakerMappingError was raised."""
    assert isinstance(context['error'], MissingSpeakerMappingError)


@then('a SpeakerNotFoundError should be raised')
def check_speaker_not_found_error(context):
    """Verify SpeakerNotFoundError was raised."""
    assert isinstance(context['error'], SpeakerNotFoundError)


@then('all occurrences of each speaker should be replaced correctly')
def check_all_occurrences_replaced(context):
    """Verify all occurrences are replaced."""
    assert "Speaker 0:" not in context['result']
    assert "Speaker 1:" not in context['result']
    assert "Agent:" in context['result']
    assert "Customer:" in context['result']
    # Check that we have multiple occurrences of each
    assert context['result'].count("Agent:") == 2
    assert context['result'].count("Customer:") == 2


@then('the output should preserve line breaks and spacing')
def check_formatting_preserved(context):
    """Verify formatting is preserved."""
    # Check that blank lines are preserved
    assert "\n\n" in context['result']
    # Check that content is still there
    assert "Agent:" in context['result']
    assert "Customer:" in context['result']
