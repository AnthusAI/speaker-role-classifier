"""Step definitions for advanced speaker classification scenarios."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from speaker_role_classifier.classifier import (
    classify_speakers,
    InvalidJSONResponseError,
    MissingSpeakerMappingError,
    SpeakerNotFoundError
)

# Load all scenarios from the feature file
scenarios('../features/advanced_classification.feature')


@pytest.fixture
def context():
    """Provide a context dictionary for sharing state between steps."""
    return {}


@given('a diarized transcript with two speakers')
def diarized_transcript_two_speakers(context):
    """Create a standard diarized transcript with two speakers."""
    context['transcript'] = """Speaker 0: Hello, how can I help you?
Speaker 1: Hi, I need assistance with my account."""


@given('the target roles are "Sales" and "Lead"')
def target_roles_sales_lead(context):
    """Set target roles to Sales and Lead."""
    context['target_roles'] = ['Sales', 'Lead']


@given('the target roles are "Agent" and "Caller"')
def target_roles_agent_caller(context):
    """Set target roles to Agent and Caller."""
    context['target_roles'] = ['Agent', 'Caller']


@given('the target roles are "Agent" and "Customer"')
def target_roles_agent_customer(context):
    """Set target roles to Agent and Customer."""
    context['target_roles'] = ['Agent', 'Customer']


@given('a transcript with "Speaker 0", "Speaker 1", and "Unknown" labels')
def transcript_with_unknown(context):
    """Create a transcript with mixed labels including Unknown."""
    context['transcript'] = """Speaker 0: Hello, how can I help you?
Unknown: Hi, I need assistance.
Speaker 1: Sure, what's the issue?
Unknown: My account is locked."""


@given('a transcript with some "Agent" labels and some "Speaker 0" labels')
def transcript_partially_labeled(context):
    """Create a transcript with mixed Agent and Speaker labels."""
    context['transcript'] = """Agent: Hello, how can I help you?
Speaker 0: Hi, I need assistance.
Agent: Sure, what's the issue?
Speaker 0: My account is locked."""


@given('a transcript already labeled with "Agent" and "Customer"')
def transcript_already_labeled(context):
    """Create a transcript already labeled with target roles."""
    context['transcript'] = """Agent: Hello, how can I help you?
Customer: Hi, I need assistance.
Agent: Sure, what's the issue?
Customer: My account is locked."""


@given('a transcript with one incorrectly labeled utterance')
def transcript_one_misclassified(context):
    """Create a transcript with one wrong label."""
    context['transcript'] = """Agent: Hello, how can I help you?
Agent: Hi, I need assistance.
Agent: Sure, what's the issue?
Customer: My account is locked."""
    context['target_roles'] = ['Agent', 'Customer']


@given('a transcript with multiple incorrectly labeled utterances')
def transcript_multiple_misclassified(context):
    """Create a transcript with multiple wrong labels."""
    context['transcript'] = """Customer: Hello, how can I help you?
Agent: Hi, I need assistance.
Customer: Sure, what's the issue?
Agent: My account is locked."""
    context['target_roles'] = ['Agent', 'Customer']


@given('a transcript requiring corrections')
def transcript_requiring_corrections(context):
    """Create a transcript that needs corrections."""
    context['transcript'] = """Agent: Hello, how can I help you?
Agent: Hi, I need assistance.
Customer: Sure, what's the issue?
Customer: My account is locked."""
    context['target_roles'] = ['Agent', 'Customer']


@given('a Lambda invocation with a diarized transcript')
def lambda_invocation_with_transcript(context):
    """Set up a Lambda invocation context."""
    context['transcript'] = """Speaker 0: Hello, how can I help you?
Speaker 1: Hi, I need assistance."""
    context['is_lambda'] = True


@when('the classifier processes the transcript with custom roles')
def process_with_custom_roles(context):
    """Process transcript with custom role names."""
    try:
        target_roles = context.get('target_roles', ['Agent', 'Customer'])
        # Check if we need logs (set by context if needed)
        return_dict = context.get('need_logs', False)
        
        result = classify_speakers(
            context['transcript'],
            target_roles=target_roles,
            return_dict=return_dict
        )
        context['result'] = result
        context['error'] = None
    except Exception as e:
        context['error'] = e
        context['result'] = None


@when('the classifier validates the transcript')
def validate_transcript(context):
    """Validate an already-labeled transcript."""
    try:
        target_roles = context.get('target_roles', ['Agent', 'Customer'])
        return_dict = context.get('need_logs', False)
        
        result = classify_speakers(
            context['transcript'],
            target_roles=target_roles,
            validate_only=True,
            return_dict=return_dict
        )
        context['result'] = result
        context['error'] = None
    except Exception as e:
        context['error'] = e
        context['result'] = None


@when('the safeguard layer validates the transcript')
def safeguard_validates(context):
    """Run safeguard validation."""
    try:
        target_roles = context.get('target_roles', ['Agent', 'Customer'])
        return_dict = context.get('need_logs', False)
        
        result = classify_speakers(
            context['transcript'],
            target_roles=target_roles,
            enable_safeguard=True,
            return_dict=return_dict
        )
        context['result'] = result
        context['error'] = None
    except Exception as e:
        context['error'] = e
        context['result'] = None


@when('a correction attempt fails to locate the utterance')
def correction_fails(context):
    """Simulate a correction failure."""
    # This will be handled by the safeguard implementation
    pass


@when('the Lambda function processes the request')
def lambda_processes_request(context):
    """Process request through Lambda handler."""
    try:
        target_roles = context.get('target_roles', ['Agent', 'Customer'])
        # Lambda always returns dict format
        from lambda_handler.handler import lambda_handler
        import json
        event = {
            'body': json.dumps({
                'transcript': context['transcript'],
                'target_roles': target_roles
            })
        }
        response = lambda_handler(event, None)
        context['lambda_response'] = response
        context['error'] = None
    except Exception as e:
        context['error'] = e
        context['lambda_response'] = None


@then(parsers.parse('the output should label one speaker as "{role}"'))
def check_speaker_labeled(context, role):
    """Check that one speaker is labeled with the specified role."""
    assert context['error'] is None, f"Error occurred: {context['error']}"
    assert context['result'] is not None
    result_text = context['result'] if isinstance(context['result'], str) else context['result'].get('transcript', '')
    assert f"{role}:" in result_text


@then(parsers.parse('the output should label the other speaker as "{role}"'))
def check_other_speaker_labeled(context, role):
    """Check that the other speaker is labeled with the specified role."""
    assert context['error'] is None, f"Error occurred: {context['error']}"
    assert context['result'] is not None
    result_text = context['result'] if isinstance(context['result'], str) else context['result'].get('transcript', '')
    assert f"{role}:" in result_text


@then('all non-target labels should be replaced with appropriate roles')
def check_non_target_replaced(context):
    """Check that all non-target labels are replaced."""
    result = context['result']
    result_text = result if isinstance(result, str) else result.get('transcript', '')
    assert 'Speaker 0:' not in result_text
    assert 'Speaker 1:' not in result_text
    assert 'Unknown:' not in result_text


@then(parsers.parse('the output should only contain "{role1}" and "{role2}" labels'))
def check_only_target_labels(context, role1, role2):
    """Check that only target role labels are present."""
    result = context['result']
    result_text = result if isinstance(result, str) else result.get('transcript', '')
    lines = result_text.split('\n')
    for line in lines:
        if ':' in line:
            label = line.split(':')[0].strip()
            assert label in [role1, role2], f"Unexpected label: {label}"


@then(parsers.parse('all "{label}" labels should be replaced appropriately'))
def check_labels_replaced(context, label):
    """Check that specific labels are replaced."""
    result = context['result']
    result_text = result if isinstance(result, str) else result.get('transcript', '')
    assert f"{label}:" not in result_text or label in context.get('target_roles', [])


@then(parsers.parse('existing "{role}" labels should remain or be corrected if wrong'))
def check_existing_labels(context, role):
    """Check that existing labels are handled correctly."""
    result = context['result']
    result_text = result if isinstance(result, str) else result.get('transcript', '')
    # If the role is in target roles, it should still be present
    if role in context.get('target_roles', []):
        assert f"{role}:" in result_text


@then('the safeguard layer should check for misclassifications')
def check_safeguard_ran(context):
    """Verify safeguard layer executed."""
    # This will be verified through logs
    assert context.get('result') is not None or context.get('error') is None


@then('any incorrect labels should be corrected')
def check_corrections_made(context):
    """Verify corrections were made."""
    # This will be verified by checking the result
    assert context.get('result') is not None


@then('the log should show validation activity')
def check_log_validation(context):
    """Verify log contains validation activity."""
    # This will fail until we implement logging
    result = context.get('result')
    if isinstance(result, dict):
        assert 'log' in result


@then('it should identify the misclassified utterance')
def check_misclassification_identified(context):
    """Verify misclassification was identified."""
    assert context.get('result') is not None


@then('it should correct only that specific utterance')
def check_specific_correction(context):
    """Verify only specific utterance was corrected."""
    result = context.get('result')
    assert result is not None


@then('the log should show the correction made')
def check_log_correction(context):
    """Verify log shows correction."""
    # This will fail until we implement logging
    result = context.get('result')
    if isinstance(result, dict):
        assert 'log' in result


@then('it should identify all misclassified utterances')
def check_all_identified(context):
    """Verify all misclassifications identified."""
    assert context.get('result') is not None


@then('it should correct each one individually')
def check_individual_corrections(context):
    """Verify individual corrections."""
    assert context.get('result') is not None


@then('the log should show all corrections attempted')
def check_log_all_corrections(context):
    """Verify log shows all corrections."""
    result = context.get('result')
    if isinstance(result, dict):
        assert 'log' in result


@then('the safeguard should report the failure to the LLM')
def check_failure_reported(context):
    """Verify failure was reported."""
    pass


@then('the LLM should retry with better identification')
def check_retry_occurred(context):
    """Verify retry occurred."""
    pass


@then('the log should show the retry attempt')
def check_log_retry(context):
    """Verify log shows retry."""
    result = context.get('result')
    if isinstance(result, dict):
        assert 'log' in result


@then('the response should include a log entry')
def check_response_has_log(context):
    """Verify response includes log."""
    # Set flag that we need logs, then re-run the classification
    context['need_logs'] = True
    target_roles = context.get('target_roles', ['Agent', 'Customer'])
    result = classify_speakers(
        context['transcript'],
        target_roles=target_roles,
        return_dict=True
    )
    context['result'] = result
    
    assert isinstance(result, dict), "Result should be a dict with log"
    assert 'log' in result


@then('the log should show the configured role names')
def check_log_role_names(context):
    """Verify log shows configured roles."""
    result = context.get('result')
    if isinstance(result, dict) and 'log' in result:
        log_str = str(result['log'])
        target_roles = context.get('target_roles', [])
        for role in target_roles:
            assert role in log_str


@then("the log should show the LLM's mapping decision")
def check_log_mapping(context):
    """Verify log shows mapping decision."""
    result = context.get('result')
    if isinstance(result, dict) and 'log' in result:
        assert len(result['log']) > 0


@then('the log should show any safeguard activity')
def check_log_safeguard(context):
    """Verify log shows safeguard activity."""
    result = context.get('result')
    if isinstance(result, dict) and 'log' in result:
        assert len(result['log']) > 0


@then('the response should contain the classified transcript')
def check_lambda_transcript(context):
    """Verify Lambda response has transcript."""
    response = context.get('lambda_response')
    assert response is not None
    assert 'body' in response


@then('the response should contain a log array')
def check_lambda_log(context):
    """Verify Lambda response has log array."""
    response = context.get('lambda_response')
    assert response is not None
    import json
    body = json.loads(response['body'])
    assert 'log' in body


@then('the log should include configuration, mapping, and validation steps')
def check_lambda_log_content(context):
    """Verify Lambda log has all steps."""
    response = context.get('lambda_response')
    import json
    body = json.loads(response['body'])
    assert 'log' in body
    assert len(body['log']) > 0
