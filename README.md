# Speaker Role Classifier

A Python tool that processes diarized call center transcripts and identifies which speaker is the agent and which is the customer using OpenAI's GPT-5 API.

## Features

- **Automatic Role Detection**: Uses GPT-5 to intelligently identify agent and customer speakers
- **Clean API**: Simple function interface for library usage
- **CLI Tool**: Command-line interface for processing transcript files
- **Robust Error Handling**: Comprehensive exception handling for API and validation errors
- **AWS Lambda Ready**: Designed for deployment to AWS Lambda
- **Test-Driven**: Built using BDD (Behavior-Driven Development) with pytest-bdd

## Installation

### From Source

```bash
# Navigate to the project directory
cd /Users/ryan.porter/Projects/speaker-role-classifier

# Install the package in editable mode
pip install -e .

# For development (includes test dependencies)
pip install -e ".[dev]"
```

### Environment Setup

Create a `.env` file in the project root with your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

## Usage

### As a Library

```python
from speaker_role_classifier import classify_speakers

transcript = """Speaker 0: Good afternoon, thank you for calling Premier Plumbing Services, this is Jennifer speaking. May I have your phone number please?
Speaker 1: Hi Jennifer, yes it's 555-0147.
Speaker 0: Thank you. I see you're calling from the number on file for Riverside Apartments. Is this Mr. Chen, the building manager?
Speaker 1: Yes, that's correct. We have an emergency situation in one of our units.
Speaker 0: I'm sorry to hear that. Which unit is experiencing the problem?
Speaker 1: It's unit 3B. The tenant just called me - their kitchen sink is completely backed up and water is overflowing onto the floor."""

result = classify_speakers(transcript)
print(result)
# Output:
# Agent: Good afternoon, thank you for calling Premier Plumbing Services, this is Jennifer speaking. May I have your phone number please?
# Customer: Hi Jennifer, yes it's 555-0147.
# Agent: Thank you. I see you're calling from the number on file for Riverside Apartments. Is this Mr. Chen, the building manager?
# Customer: Yes, that's correct. We have an emergency situation in one of our units.
# Agent: I'm sorry to hear that. Which unit is experiencing the problem?
# Customer: It's unit 3B. The tenant just called me - their kitchen sink is completely backed up and water is overflowing onto the floor.
```

### As a CLI Tool

```bash
# Process a file
speaker-role-classifier input.txt output.txt

# Use stdin/stdout
cat input.txt | speaker-role-classifier - -
```

## Input Format

The tool expects a diarized transcript with speaker labels in the format:

```
Speaker 0: [text]
Speaker 1: [text]
Speaker 0: [more text]
Speaker 1: [more text]
```

The transcript can be any length with multiple turns per speaker.

## Output Format

The tool returns the transcript with speakers labeled as:

```
Agent: [text]
Customer: [text]
Agent: [more text]
Customer: [more text]
```

All occurrences of each speaker label are replaced with their identified role.

## Error Handling

The tool raises specific exceptions for different error conditions:

- `InvalidJSONResponseError`: The API returned malformed JSON
- `MissingSpeakerMappingError`: Not all speakers were mapped to roles
- `SpeakerNotFoundError`: A mapped speaker doesn't exist in the transcript

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=speaker_role_classifier --cov-report=html

# Run specific test scenarios
pytest tests/step_defs/test_classification_steps.py -v
```

### Project Structure

```
speaker-role-classifier/
├── src/
│   └── speaker_role_classifier/
│       ├── __init__.py
│       ├── classifier.py      # Core classification logic
│       └── cli.py             # CLI interface
├── tests/
│   ├── features/
│   │   └── speaker_classification.feature  # BDD scenarios
│   ├── step_defs/
│   │   └── test_classification_steps.py    # pytest-bdd step definitions
│   └── conftest.py            # Test fixtures
├── .env                       # API key (gitignored)
├── .gitignore
├── pyproject.toml             # Project metadata and dependencies
└── README.md
```

## AWS Lambda Deployment

Deploy as a serverless HTTP API using AWS CDK and Lambda Function URLs:

```bash
# Test locally first
python test_lambda_local.py

# Deploy to AWS
cd infrastructure
pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key_here
cdk deploy
```

This creates a public HTTP endpoint without needing API Gateway. See [DEPLOYMENT.md](DEPLOYMENT.md) for full details.

**Quick API Test:**
```bash
curl -X POST https://your-function-url.lambda-url.region.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Speaker 0: Hello\nSpeaker 1: Hi"}'
```

## License

MIT

