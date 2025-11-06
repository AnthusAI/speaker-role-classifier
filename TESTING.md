# Testing Guide

This project uses BDD (Behavior-Driven Development) testing with `pytest-bdd`.

## Test Structure

```
tests/
├── features/                    # Gherkin feature files
│   ├── speaker_classification.feature      # Basic classification scenarios
│   ├── advanced_classification.feature     # Custom roles, mixed labels
│   └── safeguard_validation.feature        # Safeguard layer scenarios
├── step_defs/                   # Step definitions (Python)
│   ├── test_classification_steps.py
│   ├── test_advanced_classification_steps.py
│   └── test_safeguard_steps.py
└── conftest.py                  # Shared fixtures and configuration
```

## Running Tests

### Run All Tests (with mocking)
```bash
pytest tests/ -v
```

### Run Specific Test Suite
```bash
pytest tests/step_defs/test_safeguard_steps.py -v
```

### Run Tests Matching Pattern
```bash
pytest tests/ -k "safeguard" -v
```

## Mocking vs Real API Tests

By default, tests **mock OpenAI API calls** for speed and reliability. This is the recommended mode for:
- Local development
- CI/CD pipelines
- Quick iteration

### Running Integration Tests with Real API

To run tests against the **real OpenAI API**:

```bash
export REAL_API_TESTS=1
pytest tests/ -v
```

**Note:** Real API tests:
- Require `OPENAI_API_KEY` in your `.env` file
- Take significantly longer (10-15 minutes vs 1-2 minutes)
- Cost money (GPT-5 API calls)
- May have non-deterministic results
- Are useful for validating actual LLM behavior

### Recommended Testing Strategy

1. **During Development**: Use mocked tests (default)
   ```bash
   pytest tests/ -v
   ```

2. **Before Commits**: Run mocked tests
   ```bash
   pytest tests/ -v
   ```

3. **Weekly/Before Releases**: Run real API tests
   ```bash
   export REAL_API_TESTS=1
   pytest tests/ -v
   ```

4. **CI/CD**: Use mocked tests for fast feedback
   ```yaml
   # .github/workflows/test.yml
   - name: Run Tests
     run: pytest tests/ -v
   ```

5. **Nightly Builds** (optional): Run real API tests
   ```yaml
   # .github/workflows/integration-tests.yml
   - name: Run Integration Tests
     env:
       REAL_API_TESTS: 1
       OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
     run: pytest tests/ -v
   ```

## Test Coverage

View test coverage:

```bash
pytest tests/ --cov=src/speaker_role_classifier --cov-report=html
open htmlcov/index.html
```

## Test Scenarios

### Basic Classification (7 scenarios)
- Successfully classify speakers in a standard transcript
- Handle invalid JSON response from API
- Handle missing speaker mapping
- Handle speaker not found in transcript
- Successfully classify multiline transcript
- Handle transcript with three speakers
- Preserve transcript formatting

### Advanced Classification (10 scenarios)
- Classify with custom role names (Sales/Lead, Agent/Caller)
- Handle mixed speaker labels (Speaker 0, Unknown, etc.)
- Handle partially labeled transcripts
- Validate and correct already-labeled transcripts
- Safeguard corrects misclassified utterances
- Safeguard handles multiple corrections
- Safeguard retries on correction failure
- Log initial speaker role mapping decision
- Lambda response includes structured logs

### Safeguard Validation (7 scenarios)
- Safeguard validates correctly classified transcript
- Safeguard corrects a single misclassified utterance
- Safeguard corrects multiple misclassified utterances
- Safeguard handles utterance not found gracefully
- Safeguard respects max iterations limit
- Safeguard works with custom role names
- End-to-end classification with safeguard enabled

**Total: 24 BDD scenarios**

## Writing New Tests

1. **Add a Gherkin scenario** in the appropriate `.feature` file:
   ```gherkin
   Scenario: My new scenario
     Given some precondition
     When some action happens
     Then some outcome occurs
   ```

2. **Implement step definitions** in the appropriate `test_*_steps.py` file:
   ```python
   @given('some precondition')
   def setup_precondition(context):
       context['data'] = "test"
   
   @when('some action happens')
   def perform_action(context):
       context['result'] = do_something(context['data'])
   
   @then('some outcome occurs')
   def check_outcome(context):
       assert context['result'] == "expected"
   ```

3. **Run the test** (it should fail - RED phase)
   ```bash
   pytest tests/ -k "my_new_scenario" -v
   ```

4. **Implement the feature** to make it pass (GREEN phase)

5. **Refactor** if needed

## Debugging Tests

### Run with verbose output
```bash
pytest tests/ -vv
```

### Run with print statements visible
```bash
pytest tests/ -s
```

### Run specific test and stop on first failure
```bash
pytest tests/ -x -k "safeguard_corrects"
```

### Drop into debugger on failure
```bash
pytest tests/ --pdb
```

## Continuous Integration

The test suite is designed to run in CI/CD with:
- Fast execution (< 2 minutes with mocking)
- No external dependencies (mocked API calls)
- Deterministic results
- Clear failure messages

Example GitHub Actions workflow:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --cov=src/speaker_role_classifier
```
