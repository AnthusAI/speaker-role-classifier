# Quick Start Guide

## Setup (One-time)

```bash
# Navigate to project
cd /Users/ryan.porter/Projects/speaker-role-classifier

# Install the package
pip install -e ".[dev]"

# Set your OpenAI API key
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=speaker_role_classifier --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Using the Library

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

## Using the CLI

```bash
# Process a file
speaker-role-classifier input.txt output.txt

# Use stdin/stdout
cat input.txt | speaker-role-classifier - -

# Read from file, write to stdout
speaker-role-classifier input.txt -

# Example with the included sample
speaker-role-classifier example_transcript.txt -
```

## Common Issues

### "No module named 'speaker_role_classifier'"
```bash
# Make sure you installed the package
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH=/Users/ryan.porter/Projects/speaker-role-classifier/src:$PYTHONPATH
```

### "OPENAI_API_KEY environment variable is not set"
```bash
# Make sure .env file exists with your API key
cat .env
# Should show: OPENAI_API_KEY=your_key_here
```

### Tests fail with import errors
```bash
# Install dev dependencies
pip install -e ".[dev]"
```

## Project Structure

```
speaker-role-classifier/
├── src/speaker_role_classifier/    # Main package
│   ├── __init__.py                 # Package exports
│   ├── classifier.py               # Core classification logic
│   └── cli.py                      # Command-line interface
├── tests/                          # Test suite
│   ├── features/                   # BDD feature files
│   ├── step_defs/                  # Test step definitions
│   └── conftest.py                 # Test fixtures
├── .env                            # API key (gitignored)
├── .gitignore                      # Git ignore rules
├── pyproject.toml                  # Package configuration
├── README.md                       # Main documentation
├── TESTING.md                      # Testing guide
├── IMPLEMENTATION_SUMMARY.md       # Implementation details
└── QUICKSTART.md                   # This file
```

## Next Steps

1. ✅ Tests are passing (7/7)
2. ✅ CLI is working
3. ✅ Library imports work
4. 🔜 Add your OpenAI API key to `.env`
5. 🔜 Test with real transcripts
6. 🔜 Deploy to AWS Lambda (when ready)

## Getting Help

- Check `README.md` for detailed documentation
- Check `TESTING.md` for testing information
- Check `IMPLEMENTATION_SUMMARY.md` for technical details
- Run `speaker-role-classifier --help` for CLI usage

