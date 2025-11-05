# Testing Guide

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=speaker_role_classifier --cov-report=html
```

### Run specific test scenario
```bash
pytest tests/step_defs/test_classification_steps.py::test_successfully_classify_speakers_in_a_standard_transcript -v
```

## Test Scenarios

The project includes 7 BDD test scenarios:

1. **Successfully classify speakers in a standard transcript** - Verifies basic functionality
2. **Handle invalid JSON response from API** - Tests error handling for malformed API responses
3. **Handle missing speaker mapping** - Tests when API doesn't map all speakers
4. **Handle speaker not found in transcript** - Tests when API maps non-existent speakers
5. **Successfully classify multi-line transcript** - Tests multiple occurrences of speakers
6. **Handle transcript with three speakers** - Tests edge case with >2 speakers
7. **Preserve transcript formatting** - Tests that line breaks and spacing are maintained

## Test Coverage

Current coverage: ~68% for classifier.py (API call paths are mocked)

The tests use mocking to avoid making actual API calls during testing, which:
- Makes tests fast and deterministic
- Doesn't require API keys during testing
- Allows testing error conditions

## Manual Testing

### Test the CLI
```bash
# Create a test file
cat > test.txt << EOF
Speaker 0: Hello, thanks for calling ABC Plumbing Services, how may I help you?
Speaker 1: Hi, I have a big emergency! My faucet broke and it's flowing and it won't stop!
EOF

# Run the classifier (requires OPENAI_API_KEY in .env)
speaker-role-classifier test.txt output.txt

# Check the output
cat output.txt
```

### Test the library
```python
from speaker_role_classifier import classify_speakers

transcript = """Speaker 0: Hello, thanks for calling ABC Plumbing Services, how may I help you?
Speaker 1: Hi, I have a big emergency! My faucet broke and it's flowing and it won't stop!"""

result = classify_speakers(transcript)
print(result)
```

## Continuous Integration

To set up CI/CD, add these commands to your pipeline:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=speaker_role_classifier --cov-report=xml

# Check coverage threshold (optional)
pytest tests/ --cov=speaker_role_classifier --cov-fail-under=60
```

