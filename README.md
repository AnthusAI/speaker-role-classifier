# Speaker Role Classifier

A Python tool that processes diarized call center transcripts and identifies which speaker is the agent and which is the customer using OpenAI's GPT-5 API.

## Features

- **Automatic Role Detection**: Uses GPT-5 to intelligently identify agent and customer speakers
- **Clean API**: Simple function interface for library usage
- **CLI Tool**: Command-line interface for processing transcript files
- **Robust Error Handling**: Comprehensive exception handling for API and validation errors
- **AWS Lambda Ready**: Designed for deployment to AWS Lambda
- **Test-Driven**: Built using BDD (Behavior-Driven Development) with pytest-bdd
- **CI/CD Pipeline**: Automated testing and deployment with CodePipeline and GitHub Actions
- **Semantic Versioning**: Automated releases based on conventional commits

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

The test suite includes both **mocked tests** (fast, no API calls) and **integration tests** (slow, real API calls).

#### Fast Mocked Tests (Recommended for Development)

```bash
# Run only mocked tests (14 tests, ~0.3 seconds)
pytest -m "not integration"

# With coverage
pytest -m "not integration" --cov=speaker_role_classifier --cov-report=html

# Run specific test file
pytest tests/step_defs/test_classification_steps.py -v
```

These tests use mocked OpenAI API responses and run in under 1 second. **This is what CI/CD runs by default.**

#### Integration Tests (Requires API Key)

```bash
# Run ONLY integration tests (10 tests, ~3 minutes, requires OPENAI_API_KEY)
pytest -m integration

# Run ALL tests including integration tests (24 tests, ~3 minutes)
pytest
```

**⚠️ Warning**: Integration tests make real OpenAI API calls and will:
- Take ~3 minutes to complete
- Incur API costs (~$0.10-0.50 per full run)
- Require a valid `OPENAI_API_KEY` environment variable

**Test Breakdown:**
- **Mocked tests**: 14 tests (classification, error handling, custom roles)
- **Integration tests**: 10 tests (safeguard validation with real API calls)

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
├── infrastructure/            # AWS CDK deployment
│   ├── app.py                 # CDK app entry point
│   ├── speaker_role_classifier_stack.py  # Lambda stack definition
│   ├── cdk.json               # CDK configuration
│   ├── requirements.txt       # CDK dependencies
│   └── README.md              # Deployment guide
├── lambda_handler/
│   └── handler.py             # AWS Lambda entry point
├── example_transcript.txt     # Sample transcript
├── test_lambda_local.py       # Local Lambda testing
├── test_deployed_lambda.sh    # Deployed Lambda testing
├── send_to_lambda.sh          # Helper script to send files to Lambda
├── requirements.txt           # Lambda runtime dependencies
├── .env                       # API key (gitignored)
├── .gitignore
├── pyproject.toml             # Project metadata and dependencies
├── LICENSE                    # MIT License
├── README.md
├── QUICKSTART.md              # Quick start guide
├── DEPLOYMENT.md              # Detailed deployment guide
└── TESTING.md                 # Testing guide
```

## AWS Lambda Deployment

Deploy as a serverless HTTP API using AWS CDK and Lambda Function URLs with optional CI/CD automation.

### Deployment Options

#### Option 1: Automated CI/CD (Recommended)

Set up automated testing and deployment that triggers on every push to main:

**AWS CodePipeline** (AWS-native):
```bash
cd infrastructure
./setup-pipeline.sh
```

**GitHub Actions** (simpler):
1. Configure GitHub Secrets (AWS credentials, OpenAI API key)
2. Push to main - workflow runs automatically

See **[CI-CD-COMPARISON.md](CI-CD-COMPARISON.md)** to choose the best option for your needs.

#### Option 2: Manual Deployment

For one-time or manual deployments:

```bash
# Test locally first
python test_lambda_local.py

# Deploy to AWS
cd infrastructure
pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key_here
cdk deploy SpeakerRoleClassifierStack
```

### Testing the Deployed Function

```bash
curl -X POST https://your-function-url.lambda-url.region.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Speaker 0: Hello\nSpeaker 1: Hi"}'
```

### Documentation

- **[infrastructure/README.md](infrastructure/README.md)** - Lambda deployment guide
- **[infrastructure/PIPELINE.md](infrastructure/PIPELINE.md)** - CI/CD pipeline setup
- **[CI-CD-COMPARISON.md](CI-CD-COMPARISON.md)** - Compare CI/CD options
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment guide

## Releases and Versioning

This project uses [Semantic Release](https://semantic-release.gitbook.io/) for automated versioning and releases.

### Viewing Releases

- **[GitHub Releases](https://github.com/AnthusAI/speaker-role-classifier/releases)** - View all releases with changelogs
- **[CHANGELOG.md](CHANGELOG.md)** - Detailed changelog
- **[SEMANTIC-RELEASE.md](SEMANTIC-RELEASE.md)** - Release documentation

### Contributing

When contributing, use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: add new feature      # Minor version bump (0.1.0 → 0.2.0)
fix: fix bug              # Patch version bump (0.1.0 → 0.1.1)
feat!: breaking change    # Major version bump (0.1.0 → 1.0.0)
```

See **[.github/COMMIT_CONVENTION.md](.github/COMMIT_CONVENTION.md)** for detailed guidelines.

## License

MIT
