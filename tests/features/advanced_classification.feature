Feature: Advanced Speaker Role Classification
  As a call center analyst
  I want flexible speaker role classification with validation
  So that I can handle various transcript formats and ensure accuracy

  Scenario: Classify with custom role names (Sales and Lead)
    Given a diarized transcript with two speakers
    And the target roles are "Sales" and "Lead"
    When the classifier processes the transcript with custom roles
    Then the output should label one speaker as "Sales"
    And the output should label the other speaker as "Lead"

  Scenario: Classify with custom role names (Agent and Caller)
    Given a diarized transcript with two speakers
    And the target roles are "Agent" and "Caller"
    When the classifier processes the transcript with custom roles
    Then the output should label one speaker as "Agent"
    And the output should label the other speaker as "Caller"

  Scenario: Handle mixed speaker labels with Unknown
    Given a transcript with "Speaker 0", "Speaker 1", and "Unknown" labels
    And the target roles are "Agent" and "Customer"
    When the classifier processes the transcript with custom roles
    Then all non-target labels should be replaced with appropriate roles
    And the output should only contain "Agent" and "Customer" labels

  Scenario: Handle partially labeled transcript
    Given a transcript with some "Agent" labels and some "Speaker 0" labels
    And the target roles are "Agent" and "Customer"
    When the classifier processes the transcript with custom roles
    Then all "Speaker 0" labels should be replaced appropriately
    And existing "Agent" labels should remain or be corrected if wrong

  Scenario: Validate and correct already-labeled transcript
    Given a transcript already labeled with "Agent" and "Customer"
    And the target roles are "Agent" and "Customer"
    When the classifier validates the transcript
    Then the safeguard layer should check for misclassifications
    And any incorrect labels should be corrected
    And the log should show validation activity

  Scenario: Safeguard corrects single misclassified utterance
    Given a transcript with one incorrectly labeled utterance
    And the target roles are "Agent" and "Customer"
    When the safeguard layer validates the transcript
    Then it should identify the misclassified utterance
    And it should correct only that specific utterance
    And the log should show the correction made

  Scenario: Safeguard handles multiple corrections
    Given a transcript with multiple incorrectly labeled utterances
    And the target roles are "Agent" and "Customer"
    When the safeguard layer validates the transcript
    Then it should identify all misclassified utterances
    And it should correct each one individually
    And the log should show all corrections attempted

  Scenario: Safeguard retries on correction failure
    Given a transcript requiring corrections
    When a correction attempt fails to locate the utterance
    Then the safeguard should report the failure to the LLM
    And the LLM should retry with better identification
    And the log should show the retry attempt

  Scenario: Log initial speaker role mapping decision
    Given a diarized transcript with two speakers
    And the target roles are "Agent" and "Customer"
    When the classifier processes the transcript with custom roles
    Then the response should include a log entry
    And the log should show the configured role names
    And the log should show the LLM's mapping decision
    And the log should show any safeguard activity

  Scenario: Lambda response includes structured logs
    Given a Lambda invocation with a diarized transcript
    And the target roles are "Sales" and "Lead"
    When the Lambda function processes the request
    Then the response should contain the classified transcript
    And the response should contain a log array
    And the log should include configuration, mapping, and validation steps
