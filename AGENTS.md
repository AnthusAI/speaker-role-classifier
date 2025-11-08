# AGENTS.md

## Project Overview

Speaker Role Classifier is a Python library and CLI tool that uses OpenAI's GPT API to classify speakers in diarized call center transcripts as "Agent" or "Customer" (or custom roles). The project follows BDD (Behavior-Driven Development) with pytest-bdd and uses Semantic Release for automated versioning.

**Key Technologies:**
- Python 3.11+
- OpenAI API (GPT models)
- pytest-bdd for BDD testing
- AWS Lambda deployment via CDK
- Semantic Release with Conventional Commits

## Development Philosophy

### Test-First BDD Approach

**CRITICAL**: This project follows strict test-first development using BDD:

1. **Start with the feature file** - Write or modify `.feature` files in `tests/features/` first
2. **Run tests to see failures** - Let the missing step definitions guide you
3. **Implement step definitions** - Add steps in `tests/step_defs/`
4. **Implement the feature** - Only then write the actual code in `src/speaker_role_classifier/`
5. **Verify tests pass** - Ensure all scenarios pass before considering the work complete

**Never implement features before writing the tests.** The `.feature` files are the specification.

## Setup Commands

```bash
# Install dependencies (development mode)
pip install -e ".[dev]"

# Set up environment
echo "OPENAI_API_KEY=your_key_here" > .env

# Verify installation
pytest -m "not integration" -v
```

## Testing Instructions

### Test Types and Execution

**IMPORTANT**: The test suite has two distinct types:

1. **Mocked tests** (14 tests, ~0.3 seconds, no API calls)
   - Default for development and CI/CD
   - Use mocked OpenAI responses
   - Run with: `pytest -m "not integration"`

2. **Integration tests** (10 tests, ~3 minutes, real API calls)
   - Require valid `OPENAI_API_KEY`
   - Make real OpenAI API calls (incur costs ~$0.10-0.50)
   - Run with: `pytest -m integration`
   - Run all tests: `pytest` (includes integration tests)

### Running Tests

```bash
# Fast mocked tests (RECOMMENDED for development)
pytest -m "not integration"

# With coverage
pytest -m "not integration" --cov=speaker_role_classifier --cov-report=html

# Integration tests only (requires API key, costs money)
pytest -m integration

# All tests including integration (slow, ~3 minutes)
pytest

# Specific test file
pytest tests/step_defs/test_classification_steps.py -v

# Specific scenario
pytest tests/step_defs/test_classification_steps.py::test_successfully_classify_speakers_in_a_standard_transcript -v
```

### Test Organization

- `tests/features/*.feature` - Gherkin BDD scenarios (human-readable specifications)
- `tests/step_defs/test_*.py` - pytest-bdd step definitions
- `tests/conftest.py` - Shared fixtures and test configuration
- Tests marked with `@pytest.mark.integration` require real API calls

### Adding New Tests

1. Write the scenario in a `.feature` file using Gherkin syntax
2. Run tests to see which steps are missing
3. Implement step definitions in appropriate `test_*.py` file
4. Implement the actual feature code
5. Verify all tests pass with `pytest -m "not integration"`

## Code Style and Conventions

### Python Style

- Python 3.11+ syntax
- Type hints where beneficial
- Docstrings for public functions
- Follow PEP 8 conventions
- Keep functions focused and testable

### Project Structure

```
src/speaker_role_classifier/
├── __init__.py           # Public API exports
├── classifier.py         # Core classification logic
├── cli.py               # Command-line interface
└── safeguard.py         # Safeguard validation (integration tests only)

tests/
├── features/            # BDD feature files (Gherkin)
│   ├── speaker_classification.feature
│   ├── advanced_classification.feature
│   └── safeguard_validation.feature
├── step_defs/          # pytest-bdd step definitions
│   ├── test_classification_steps.py
│   ├── test_advanced_classification_steps.py
│   └── test_safeguard_steps.py
└── conftest.py         # Test fixtures and mocking

infrastructure/         # AWS CDK deployment code
lambda_handler/        # AWS Lambda entry point
```

### Module Responsibilities

- `classifier.py` - Main `classify_speakers()` function, speaker mapping logic
- `safeguard.py` - Validation and correction logic (requires real API, integration tests only)
- `cli.py` - Command-line interface, file I/O
- `conftest.py` - Smart mocking of OpenAI API, test fixtures

## Commit Message Format

**CRITICAL**: This project uses Semantic Release with Conventional Commits for automated versioning.

### Commit Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types (determines version bump)

- `feat:` - New feature (minor version bump: 0.1.0 → 0.2.0)
- `fix:` - Bug fix (patch version bump: 0.1.0 → 0.1.1)
- `security:` - Security fix (patch version bump: 0.1.0 → 0.1.1)
- `docs:` - Documentation only changes (patch version bump)
- `test:` - Adding or updating tests (no version bump)
- `refactor:` - Code refactoring (patch version bump)
- `chore:` - Maintenance tasks (no version bump)
- `feat!:` or `fix!:` - Breaking change (major version bump: 0.1.0 → 1.0.0)

### Examples

```bash
# Feature (minor bump)
git commit -m "feat: add support for custom role names"

# Bug fix (patch bump)
git commit -m "fix: handle empty transcript gracefully"

# Security fix (patch bump)
git commit -m "security: upgrade openai package to fix CVE-2024-1234"

# Breaking change (major bump)
git commit -m "feat!: change classify_speakers return format to dict

BREAKING CHANGE: classify_speakers now returns a dict with 'transcript' and 'log' keys instead of just the transcript string"

# Documentation (patch bump)
git commit -m "docs: update README with new examples"

# Tests (no bump)
git commit -m "test: add scenario for three-speaker transcripts"
```

### Scopes (optional but helpful)

- `classifier` - Core classification logic
- `safeguard` - Safeguard validation
- `cli` - Command-line interface
- `lambda` - AWS Lambda deployment
- `ci` - CI/CD pipeline

See `.github/COMMIT_CONVENTION.md` for detailed guidelines.

## CI/CD and Deployment

### Unified Pipeline Architecture

**CRITICAL**: This project uses a unified CI/CD pipeline where all validation happens in GitHub Actions BEFORE version advancement and AWS deployment.

```
Push to main
    ↓
Security Scanning (parallel)
    ├─ CodeQL (GitHub semantic analysis)
    ├─ Bandit (Python security linter)
    ├─ Safety (dependency vulnerabilities)
    └─ pip-audit (PyPA vulnerability scanner)
    ↓
Tests (parallel with security)
    └─ pytest with mocked tests + coverage
    ↓
Unified Pipeline (sequential)
    ├─ Wait for security + tests to pass
    ├─ Run semantic-release (version bump, tag, changelog)
    ├─ Trigger AWS CodePipeline deployment
    ├─ Wait for AWS deployment to complete
    └─ Report success/failure
```

**Key Principle**: Version is only advanced after ALL validation passes. AWS CodePipeline is deployment-only (no tests or security scans that could cause it to fail).

### GitHub Actions Workflows

1. **`.github/workflows/test.yml`** - Runs on push/PR
   - Installs dependencies
   - Runs mocked tests (`pytest -m "not integration"`)
   - Uploads coverage to Codecov
   - Fast feedback (~30 seconds)

2. **`.github/workflows/security.yml`** - Runs on push/PR
   - Bandit: Python security linter (SQL injection, hardcoded passwords, etc.)
   - Safety: Dependency vulnerability scanner (CVSSv3 >= 7.0)
   - pip-audit: PyPA official vulnerability scanner
   - Uploads SARIF reports to GitHub Security tab
   - Blocks deployment on HIGH/CRITICAL findings

3. **`.github/workflows/codeql.yml`** - Runs on push/PR/schedule
   - GitHub's semantic code analysis
   - Security-extended query suite
   - AI-powered Copilot Autofix for vulnerabilities
   - Runs weekly on schedule

4. **`.github/workflows/unified-pipeline.yml`** - Runs on push to main only
   - Waits for security and test workflows to pass
   - Runs semantic-release (version bump, tag, changelog, GitHub release)
   - Triggers AWS CodePipeline via AWS CLI
   - Waits for AWS deployment to complete (15 min timeout)
   - Reports final status

### AWS CodePipeline (Deployment-Only)

The AWS CodePipeline is **simplified to deployment-only** with no tests or security scans:

- **Source stage**: Pull from GitHub (webhook DISABLED - manual trigger only)
- **Build stage**: Package Lambda dependencies (no tests, cannot fail)
- **Deploy stage**: CDK deploy (only infrastructure issues can fail)

**Important**: CodePipeline is triggered by GitHub Actions AFTER version is tagged. This ensures version advancement only happens after all validation passes.

### Manual AWS Deployment

```bash
# Test Lambda locally first
python test_lambda_local.py

# Deploy to AWS (if needed outside of CI/CD)
cd infrastructure
pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key_here
cdk deploy SpeakerRoleClassifierStack

# Or manually trigger CodePipeline
aws codepipeline start-pipeline-execution --name SpeakerRoleClassifierPipeline
```

### AWS Setup for GitHub Actions

To enable GitHub Actions to trigger AWS CodePipeline, configure:

1. **IAM User**: `github-actions-deployer`
2. **IAM Policy**: Minimal permissions for CodePipeline trigger
3. **GitHub Secrets**:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `AWS_CODEPIPELINE_NAME` (value: `SpeakerRoleClassifierPipeline`)

See `infrastructure/README.md` for detailed setup instructions.

## Environment Variables

- `OPENAI_API_KEY` - Required for real API calls (integration tests and production)
- Set in `.env` file for local development
- Set in AWS Secrets Manager for Lambda deployment
- Set as GitHub Secret for CI/CD (not currently used for deployment)

## Common Tasks

### Add a new feature

1. Write scenario in `tests/features/*.feature`
2. Run `pytest -m "not integration"` to see missing steps
3. Add step definitions in `tests/step_defs/test_*.py`
4. Implement feature in `src/speaker_role_classifier/`
5. Verify tests pass
6. Commit with `feat:` prefix

### Fix a bug

1. Write failing test scenario first (if not exists)
2. Run tests to confirm failure
3. Fix the bug in source code
4. Verify tests pass
5. Commit with `fix:` prefix

### Update documentation

1. Update relevant `.md` files
2. Commit with `docs:` prefix (no version bump)

### Add integration test

1. Write scenario in `.feature` file
2. Add step definitions
3. Mark test with `@pytest.mark.integration` or add to `test_safeguard_steps.py`
4. Test with `pytest -m integration`

## Security Considerations

### Automated Security Scanning

This project uses comprehensive automated security scanning:

1. **Dependabot** (`.github/dependabot.yml`)
   - Automated dependency updates for Python and GitHub Actions
   - Daily checks for security vulnerabilities
   - Auto-creates PRs for security updates

2. **CodeQL** (`.github/workflows/codeql.yml`)
   - GitHub's semantic code analysis
   - Security-extended query suite
   - AI-powered Copilot Autofix for vulnerabilities
   - Runs on every push/PR and weekly schedule

3. **Bandit** (`.bandit.yml`)
   - Python security linter
   - Checks for: SQL injection, hardcoded passwords, shell injection, insecure crypto
   - Severity threshold: MEDIUM and above
   - Excludes test directories

4. **Safety** (`.safety-policy.yml`)
   - Dependency vulnerability scanner
   - Fails on CVSSv3 >= 7.0 (HIGH/CRITICAL)
   - Scans both direct and transitive dependencies

5. **pip-audit**
   - PyPA official vulnerability scanner
   - Uses OSV (Open Source Vulnerabilities) database
   - Fails on any known vulnerability

### Running Security Scans Locally

```bash
# Install security tools
pip install -e ".[dev]"

# Run Bandit
bandit -r src/

# Run Safety
safety check --policy-file .safety-policy.yml

# Run pip-audit
pip-audit

# Run all security scans (same as CI)
bandit -r src/ && safety check && pip-audit
```

### Security Findings in CI/CD

- Security scans run on every push and PR
- HIGH/CRITICAL findings block deployment
- Results uploaded to GitHub Security tab (SARIF format)
- Copilot can suggest automatic fixes for vulnerabilities

### Handling Security Findings

1. **Review the finding** in GitHub Security tab or workflow logs
2. **Assess severity** (LOW/MEDIUM/HIGH/CRITICAL)
3. **Fix the issue**:
   - Update dependency: `pip install --upgrade <package>`
   - Refactor code to remove vulnerability
   - Use Copilot Autofix suggestions
4. **Ignore false positives** (with justification):
   - Add to `.safety-policy.yml` for dependency issues
   - Add to `.bandit.yml` for code issues
5. **Commit with `security:` prefix** for release notes

### API Keys and Secrets

- Never commit `.env` file or API keys
- API keys stored in AWS Secrets Manager for Lambda
- GitHub Secrets used for CI/CD (AWS credentials, tokens)
- Lambda has minimal IAM permissions
- Integration tests incur API costs - use sparingly

## Gotchas and Important Notes

### Testing

- **Running `pytest` alone takes ~3 minutes** because it includes integration tests
- Always use `pytest -m "not integration"` for fast development
- Integration tests require `OPENAI_API_KEY` and make real API calls
- Mock is "smart" - it parses the system prompt to extract target roles
- Safeguard tests (`test_safeguard_steps.py`) are ALL integration tests

### BDD with pytest-bdd

- Feature files use Gherkin syntax (Given/When/Then)
- Step definitions use `@scenario`, `@given`, `@when`, `@then` decorators
- Use `scenarios()` to load all scenarios from a feature file
- Or use `@scenario()` decorator for individual scenarios
- Fixtures can be used in step definitions

### Semantic Release

- Release happens automatically on push to main
- Version determined by commit messages since last release
- CHANGELOG.md updated automatically
- GitHub Release created automatically
- **Never manually edit version numbers**

### Lambda Deployment

- Lambda uses Python 3.11 runtime
- Dependencies bundled automatically by CDK
- Function URL provides public HTTPS endpoint
- OpenAI API key injected from Secrets Manager
- Cold start can take 2-3 seconds

## Troubleshooting

### Security Scan Failures

**Problem**: Security workflow fails with HIGH/CRITICAL findings

**Solution**:
1. Check GitHub Actions logs for specific findings
2. Review GitHub Security tab for detailed vulnerability information
3. Update vulnerable dependencies: `pip install --upgrade <package>`
4. For code issues, refactor using Copilot Autofix suggestions
5. For false positives, add to `.safety-policy.yml` or `.bandit.yml` with justification

### AWS Deployment Fails After Version Bump

**Problem**: Version is tagged (e.g., v1.0.3) but AWS deployment failed

**Impact**: Version 1.0.3 exists in GitHub but NOT deployed to AWS Lambda

**Solution**:
1. Check AWS CodePipeline console for error details
2. Fix infrastructure issue (IAM permissions, CDK config, etc.)
3. Manually trigger deployment:
   ```bash
   aws codepipeline start-pipeline-execution --name SpeakerRoleClassifierPipeline
   ```
4. Or push a new commit to trigger full pipeline again

**Why this is acceptable**: Infrastructure failures are rare (not code quality issues). Version tag accurately reflects code state.

### Unified Pipeline Timeout

**Problem**: Unified pipeline times out waiting for AWS deployment

**Solution**:
1. Check AWS CodePipeline console - deployment may still be running
2. If deployment succeeded, the timeout is just a monitoring issue
3. If deployment failed, see "AWS Deployment Fails" above
4. Increase timeout in `.github/workflows/unified-pipeline.yml` if needed (default: 15 minutes)

### Tests Pass Locally But Fail in CI

**Problem**: `pytest -m "not integration"` passes locally but fails in GitHub Actions

**Solution**:
1. Ensure all dependencies are in `pyproject.toml`
2. Check Python version matches (3.11)
3. Review GitHub Actions logs for specific error
4. Try running in clean environment: `python -m venv clean_env && source clean_env/bin/activate && pip install -e .[dev] && pytest -m "not integration"`

### Manual Trigger of AWS CodePipeline

**To manually trigger AWS deployment**:
```bash
# Trigger pipeline
aws codepipeline start-pipeline-execution --name SpeakerRoleClassifierPipeline

# Check status
aws codepipeline get-pipeline-state --name SpeakerRoleClassifierPipeline
```

## Before Committing

**Checklist:**

1. ✅ Tests written first (BDD feature file)
2. ✅ All mocked tests pass: `pytest -m "not integration"`
3. ✅ Security scans pass locally: `bandit -r src/ && safety check && pip-audit`
4. ✅ If touching safeguard, integration tests pass: `pytest -m integration`
5. ✅ Commit message follows Conventional Commits format (include `security:` for security fixes)
6. ✅ No API keys or secrets in code
7. ✅ Documentation updated if needed

## Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Release](https://semantic-release.gitbook.io/)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)
- [Gherkin Syntax](https://cucumber.io/docs/gherkin/reference/)
- [Project README](README.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Testing Guide](TESTING.md)

