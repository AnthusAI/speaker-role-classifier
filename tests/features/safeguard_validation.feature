Feature: Safeguard Validation with Tool Calling

  Scenario: Safeguard validates correctly classified transcript
    Given a correctly classified transcript with "Agent" and "Customer"
    When the safeguard validation runs
    Then no corrections should be made
    And the log should show safeguard completed successfully

  Scenario: Safeguard corrects a single misclassified utterance
    Given a transcript with one misclassified utterance
    When the safeguard validation runs
    Then the misclassified utterance should be corrected
    And the log should show one correction
    And the corrected transcript should have proper role labels

  Scenario: Safeguard corrects multiple misclassified utterances
    Given a transcript with multiple misclassified utterances
    When the safeguard validation runs
    Then all misclassified utterances should be corrected
    And the log should show multiple corrections
    And the corrected transcript should have proper role labels

  Scenario: Safeguard handles utterance not found gracefully
    Given a transcript requiring corrections
    When the safeguard tool call cannot locate an utterance
    Then the safeguard should log the failure
    And the safeguard should continue with remaining corrections

  Scenario: Safeguard respects max iterations limit
    Given a transcript with many potential corrections
    When the safeguard validation runs
    Then the safeguard should not exceed max iterations
    And the log should show iteration count

  Scenario: Safeguard works with custom role names
    Given a correctly classified transcript with "Sales" and "Lead"
    When the safeguard validation runs with custom roles
    Then no corrections should be made
    And the log should show the custom target roles

  Scenario: End-to-end classification with safeguard enabled
    Given a diarized transcript with generic speaker labels
    When the classifier processes with safeguard enabled
    Then the transcript should be classified correctly
    And the safeguard should validate the classification
    And the log should show both classification and safeguard steps
