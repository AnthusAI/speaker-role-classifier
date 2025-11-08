# Security Scanning Setup

This document describes the comprehensive security scanning implementation added to the Speaker Role Classifier project.

## Overview

The project now includes automated security scanning at multiple levels:

1. **GitHub-native tools**: CodeQL with AI-powered Copilot Autofix
2. **Python-specific tools**: Bandit, Safety, pip-audit
3. **Dependency management**: Dependabot for automated updates
4. **Unified CI/CD**: All validation happens before version advancement

## Security Tools

### 1. Dependabot (`.github/dependabot.yml`)

**Purpose**: Automated dependency updates

**Configuration**:
- Monitors Python dependencies in `pyproject.toml`
- Monitors GitHub Actions versions
- Daily checks for security vulnerabilities
- Auto-creates PRs for updates
- Groups minor/patch updates to reduce PR noise

**Usage**: Automatic - no manual intervention needed

### 2. CodeQL (`.github/workflows/codeql.yml`)

**Purpose**: GitHub's semantic code analysis

**Features**:
- Security-extended query suite (most comprehensive)
- AI-powered Copilot Autofix for automatic vulnerability remediation
- Runs on push/PR and weekly schedule
- Uploads SARIF results to GitHub Security tab

**Configuration**:
- Language: Python
- Excludes: `tests/`, `infrastructure/cdk.out/`, `build/`

**Usage**: Automatic on every push/PR

### 3. Bandit (`.bandit.yml`)

**Purpose**: Python security linter

**Checks for**:
- SQL injection
- Hardcoded passwords
- Shell injection
- Insecure cryptography
- And 60+ other security issues

**Configuration**:
- Severity threshold: MEDIUM and above
- Confidence threshold: MEDIUM and above
- Excludes: `tests/`, `build/`, `infrastructure/`

**Local usage**:
```bash
bandit -r src/
```

### 4. Safety (`.safety-policy.yml`)

**Purpose**: Dependency vulnerability scanner

**Features**:
- Scans both direct and transitive dependencies
- Uses CVSSv3 scoring
- Fails on HIGH/CRITICAL vulnerabilities (CVSSv3 >= 7.0)
- Allows ignoring specific CVEs with justification

**Local usage**:
```bash
safety scan
```

### 5. pip-audit

**Purpose**: PyPA official vulnerability scanner

**Features**:
- Uses OSV (Open Source Vulnerabilities) database
- Scans all installed packages
- Provides fix versions

**Local usage**:
```bash
pip-audit
```

## Unified CI/CD Pipeline

### Architecture

```
Push to main
    ↓
Security Scanning (parallel)
    ├─ CodeQL (~2 min)
    ├─ Bandit (~10 sec)
    ├─ Safety (~5 sec)
    └─ pip-audit (~5 sec)
    ↓
Tests (parallel with security)
    └─ pytest (~30 sec)
    ↓
Unified Pipeline (sequential)
    ├─ Wait for security + tests to pass
    ├─ Run semantic-release (version bump, tag, changelog)
    ├─ Trigger AWS CodePipeline deployment
    ├─ Wait for AWS deployment to complete
    └─ Report success/failure
```

### Key Principles

1. **Validation before version advancement**: Version is only bumped after ALL security scans and tests pass
2. **Fail-fast**: Security issues caught before deployment
3. **Single source of truth**: Version tag reflects deployed code state
4. **Deployment-only AWS pipeline**: AWS CodePipeline simplified to remove tests/security (cannot fail due to code quality)

## GitHub Actions Workflows

### 1. `test.yml` (formerly `deploy.yml`)

**Triggers**: Push to main, PRs
**Purpose**: Run mocked tests with coverage
**Duration**: ~30 seconds

### 2. `security.yml` (NEW)

**Triggers**: Push to main, PRs
**Purpose**: Run all security scans in parallel
**Duration**: ~2 minutes
**Outputs**: SARIF reports to GitHub Security tab

### 3. `codeql.yml` (NEW)

**Triggers**: Push to main, PRs, weekly schedule
**Purpose**: GitHub semantic code analysis
**Duration**: ~2 minutes
**Outputs**: SARIF reports to GitHub Security tab

### 4. `unified-pipeline.yml` (NEW, replaces `release.yml`)

**Triggers**: Push to main only
**Purpose**: Orchestrate validation, release, and deployment
**Duration**: ~5-20 minutes (depending on AWS deployment)

**Steps**:
1. Wait for security and test workflows to complete
2. Run semantic-release (version bump, changelog, tag)
3. Trigger AWS CodePipeline via AWS CLI
4. Wait for AWS deployment (15 min timeout)
5. Report final status

## AWS CodePipeline Changes

### Before (Old Architecture)

- **Source**: Pull from GitHub (webhook enabled)
- **Build**: Run tests, package Lambda
- **Deploy**: CDK deploy

**Problem**: Tests could fail after version bump, causing divergence

### After (New Architecture)

- **Source**: Pull from GitHub (webhook DISABLED - manual trigger only)
- **Build**: Package Lambda only (no tests, cannot fail)
- **Deploy**: CDK deploy (only infrastructure issues can fail)

**Benefit**: Version advancement only happens after ALL validation passes in GitHub

## Required GitHub Secrets

For the unified pipeline to work, configure these GitHub Secrets:

1. `AWS_ACCESS_KEY_ID` - IAM user credentials
2. `AWS_SECRET_ACCESS_KEY` - IAM user credentials
3. `AWS_REGION` - AWS region (e.g., `us-east-1`)
4. `AWS_CODEPIPELINE_NAME` - Pipeline name (value: `SpeakerRoleClassifierPipeline`)

### IAM Policy

Create an IAM user with minimal permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "codepipeline:StartPipelineExecution",
        "codepipeline:GetPipelineState",
        "codepipeline:GetPipelineExecution"
      ],
      "Resource": "arn:aws:codepipeline:*:*:SpeakerRoleClassifierPipeline"
    }
  ]
}
```

## Running Security Scans Locally

### Install Tools

```bash
pip install -e ".[dev]"
```

### Run Individual Scans

```bash
# Bandit
bandit -r src/

# Safety
safety scan

# pip-audit
pip-audit
```

### Run All Scans

```bash
bandit -r src/ && safety scan && pip-audit
```

## Handling Security Findings

### 1. Review Finding

- Check GitHub Security tab for detailed information
- Review GitHub Actions logs for specific errors
- Assess severity (LOW/MEDIUM/HIGH/CRITICAL)

### 2. Fix Issue

**For dependency vulnerabilities**:
```bash
pip install --upgrade <package>
```

**For code issues**:
- Refactor code to remove vulnerability
- Use Copilot Autofix suggestions (if available)

### 3. Ignore False Positives

**For Safety (dependency issues)**:

Edit `.safety-policy.yml`:
```yaml
security:
  ignore-vulnerabilities:
    - id: 12345
      reason: "False positive - we don't use the vulnerable function"
      expires: "2025-12-31"
```

**For Bandit (code issues)**:

Edit `.bandit.yml` or add inline comment:
```python
# nosec B101
assert condition, "This is safe in our context"
```

### 4. Commit with Security Prefix

```bash
git commit -m "security: upgrade openai package to fix CVE-2024-1234"
```

This will:
- Trigger a patch version bump (e.g., 1.0.2 → 1.0.3)
- Add entry to "Security" section in CHANGELOG.md
- Include in GitHub release notes

## Troubleshooting

### Security Workflow Fails

**Problem**: Security workflow fails with HIGH/CRITICAL findings

**Solution**:
1. Check GitHub Actions logs for specific findings
2. Review GitHub Security tab for detailed vulnerability information
3. Update vulnerable dependencies or refactor code
4. For false positives, add to `.safety-policy.yml` or `.bandit.yml`

### AWS Deployment Fails After Version Bump

**Problem**: Version is tagged but AWS deployment failed

**Impact**: Version exists in GitHub but NOT deployed to AWS

**Solution**:
1. Check AWS CodePipeline console for error details
2. Fix infrastructure issue (IAM permissions, CDK config, etc.)
3. Manually trigger deployment:
   ```bash
   aws codepipeline start-pipeline-execution --name SpeakerRoleClassifierPipeline
   ```

**Why this is acceptable**: Infrastructure failures are rare and not related to code quality. Version tag accurately reflects code state.

## Benefits

### Comprehensive Coverage

- **Multiple tools**: GitHub CodeQL + Bandit + Safety + pip-audit
- **Multiple layers**: Code analysis + dependency scanning + automated updates
- **AI-powered**: Copilot Autofix for automatic vulnerability remediation

### Fail-Fast

- Security issues caught before version advancement
- Blocks deployment on HIGH/CRITICAL findings
- Fast feedback (~2 minutes for security scans)

### No Divergence

- Version only advances after ALL validation passes
- AWS pipeline simplified to deployment-only
- Single source of truth for version and deployment status

### Audit Trail

- All security findings in GitHub Security tab
- SARIF reports uploaded for each scan
- Historical tracking of vulnerabilities

## References

- [GitHub CodeQL Documentation](https://codeql.github.com/docs/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://docs.pyup.io/docs/safety-20)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)

