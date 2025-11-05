"""Step definitions for speaker classification BDD tests."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import patch, MagicMock
import json

from speaker_role_classifier import (
    classify_speakers,
    InvalidJSONResponseError,
    MissingSpeakerMappingError,
    SpeakerNotFoundError,
)

# Load all scenarios from the feature file
scenarios('../features/speaker_classification.feature')


# Context to store state between steps
@pytest.fixture
def context():
    """Context dictionary to share data between steps."""
    return {}


# Given steps

@given('a diarized transcript with two speakers')
def transcript_with_two_speakers(context, simple_transcript):
    """Store a simple two-speaker transcript in context."""
    context['transcript'] = simple_transcript


@given('a diarized transcript with multiple lines per speaker')
def transcript_with_multiple_lines(context, multiline_transcript):
    """Store a multiline transcript in context."""
    context['transcript'] = multiline_transcript


@given('a diarized transcript with three speakers')
def transcript_with_three_speakers(context, three_speaker_transcript):
    """Store a three-speaker transcript in context."""
    context['transcript'] = three_speaker_transcript


@given('a diarized transcript with specific formatting')
def transcript_with_formatting(context, formatted_transcript):
    """Store a formatted transcript in context."""
    context['transcript'] = formatted_transcript


# When steps

@when('the classifier processes the transcript')
def process_transcript(context, valid_api_response):
    """Process the transcript with a mocked valid API response."""
    with patch('speaker_role_classifier.classifier._call_gpt5_api') as mock_api:
        mock_api.return_value = valid_api_response
        try:
            context['result'] = classify_speakers(context['transcript'])
            context['error'] = None
        except Exception as e:
            context['error'] = e
            context['result'] = None


@when('the API returns malformed JSON')
def api_returns_malformed_json(context, malformed_json_response):
    """Mock the API to return malformed JSON."""
    with patch('speaker_role_classifier.classifier._call_gpt5_api') as mock_api:
        mock_api.side_effect = InvalidJSONResponseError("Failed to parse JSON response from API")
        try:
            context['result'] = classify_speakers(context['transcript'])
            context['error'] = None
        except Exception as e:
            context['error'] = e
            context['result'] = None


@when('the API response does not map all speakers')
def api_missing_speaker_mapping(context, incomplete_mapping_response):
    """Mock the API to return incomplete speaker mapping."""
    with patch('speaker_role_classifier.classifier._call_gpt5_api') as mock_api:
        mock_api.return_value = incomplete_mapping_response
        try:
            context['result'] = classify_speakers(context['transcript'])
            context['error'] = None
        except Exception as e:
            context['error'] = e
            context['result'] = None


@when('the API response maps a speaker that doesn\'t exist')
def api_maps_wrong_speaker(context, wrong_speaker_mapping_response):
    """Mock the API to return mapping for non-existent speaker."""
    with patch('speaker_role_classifier.classifier._call_gpt5_api') as mock_api:
        mock_api.return_value = wrong_speaker_mapping_response
        try:
            context['result'] = classify_speakers(context['transcript'])
            context['error'] = None
        except Exception as e:
            context['error'] = e
            context['result'] = None


# Then steps

@then('the output should label one speaker as "Agent"')
def check_agent_label(context):
    """Verify that the output contains 'Agent:' label."""
    assert context['result'] is not None
    assert 'Agent:' in context['result']


@then('the output should label the other speaker as "Customer"')
def check_customer_label(context):
    """Verify that the output contains 'Customer:' label."""
    assert context['result'] is not None
    assert 'Customer:' in context['result']


@then('all speaker labels should be replaced')
def check_no_generic_labels(context):
    """Verify that no generic 'Speaker N:' labels remain."""
    assert context['result'] is not None
    assert 'Speaker 0:' not in context['result']
    assert 'Speaker 1:' not in context['result']


@then('an InvalidJSONResponseError should be raised')
def check_invalid_json_error(context):
    """Verify that InvalidJSONResponseError was raised."""
    assert context['error'] is not None
    assert isinstance(context['error'], InvalidJSONResponseError)


@then('a MissingSpeakerMappingError should be raised')
def check_missing_mapping_error(context):
    """Verify that MissingSpeakerMappingError was raised."""
    assert context['error'] is not None
    assert isinstance(context['error'], MissingSpeakerMappingError)


@then('a SpeakerNotFoundError should be raised')
def check_speaker_not_found_error(context):
    """Verify that SpeakerNotFoundError was raised."""
    assert context['error'] is not None
    assert isinstance(context['error'], SpeakerNotFoundError)


@then('all occurrences of each speaker should be replaced correctly')
def check_all_occurrences_replaced(context, expected_multiline_output):
    """Verify that all speaker occurrences are replaced in multiline transcript."""
    assert context['result'] is not None
    assert context['result'] == expected_multiline_output


@then('the output should preserve line breaks and spacing')
def check_formatting_preserved(context, expected_formatted_output):
    """Verify that formatting is preserved in the output."""
    assert context['result'] is not None
    assert context['result'] == expected_formatted_output

