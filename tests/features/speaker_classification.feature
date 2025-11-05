Feature: Speaker Role Classification
  As a call center analyst
  I want to automatically identify which speaker is the agent and which is the customer
  So that I can properly label transcripts for analysis

  Scenario: Successfully classify speakers in a standard transcript
    Given a diarized transcript with two speakers
    When the classifier processes the transcript
    Then the output should label one speaker as "Agent"
    And the output should label the other speaker as "Customer"
    And all speaker labels should be replaced

  Scenario: Handle invalid JSON response from API
    Given a diarized transcript with two speakers
    When the API returns malformed JSON
    Then an InvalidJSONResponseError should be raised

  Scenario: Handle missing speaker mapping
    Given a diarized transcript with two speakers
    When the API response does not map all speakers
    Then a MissingSpeakerMappingError should be raised

  Scenario: Handle speaker not found in transcript
    Given a diarized transcript with two speakers
    When the API response maps a speaker that doesn't exist
    Then a SpeakerNotFoundError should be raised

  Scenario: Successfully classify multi-line transcript
    Given a diarized transcript with multiple lines per speaker
    When the classifier processes the transcript
    Then all occurrences of each speaker should be replaced correctly

  Scenario: Handle transcript with three speakers
    Given a diarized transcript with three speakers
    When the classifier processes the transcript
    Then a MissingSpeakerMappingError should be raised
    
  Scenario: Preserve transcript formatting
    Given a diarized transcript with specific formatting
    When the classifier processes the transcript
    Then the output should preserve line breaks and spacing

