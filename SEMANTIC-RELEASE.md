# Semantic Release Setup

This project uses [Semantic Release](https://semantic-release.gitbook.io/) for automated versioning and releases.

## Overview

Semantic Release automatically:
- ✅ Determines the next version number based on commit messages
- ✅ Generates release notes from commits
- ✅ Updates CHANGELOG.md
- ✅ Updates version in pyproject.toml
- ✅ Creates GitHub releases
- ✅ Tags releases in Git

## How It Works

### 1. Commit Messages Drive Versioning

Using [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: new feature      → 0.1.0 → 0.2.0 (MINOR)
fix: bug fix           → 0.1.0 → 0.1.1 (PATCH)
feat!: breaking change → 0.1.0 → 1.0.0 (MAJOR)
```

### 2. Automatic Release on Push to Main

When you push to `main`:
1. GitHub Actions runs the release workflow
2. Semantic Release analyzes commits since last release
3. Determines version bump (major/minor/patch)
4. Updates version in `pyproject.toml`
5. Generates/updates `CHANGELOG.md`
6. Creates Git tag
7. Creates GitHub release with notes
8. Commits changes back to repo

## Configuration Files

### `.releaserc.json`
Main configuration file defining:
- Branches to release from (`main`)
- Plugins and their order
- Release rules (which commits trigger which version bumps)
- Changelog format
- Assets to commit

### `.github/workflows/release.yml`
GitHub Actions workflow that:
- Runs on push to `main`
- Installs semantic-release and plugins
- Executes the release process

## Commit Message Format

See [.github/COMMIT_CONVENTION.md](.github/COMMIT_CONVENTION.md) for detailed guide.

**Quick reference:**

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature (MINOR bump)
- `fix`: Bug fix (PATCH bump)
- `perf`: Performance improvement (PATCH bump)
- `docs`: Documentation (PATCH bump)
- `refactor`: Code refactoring (PATCH bump)
- `build`: Build changes (PATCH bump)
- `ci`: CI changes (no bump)
- `test`: Test changes (no bump)
- `chore`: Other changes (no bump)

**Breaking changes:**
```
feat!: remove old API

BREAKING CHANGE: Old API removed, use new API instead.
```

## Examples

### First Release (0.1.0)

When you first push commits with semantic release enabled:

```bash
git commit -m "feat: initial release with speaker classification"
git push origin main
```

Result: Version 0.1.0 created

### Feature Release (0.1.0 → 0.2.0)

```bash
git commit -m "feat(classifier): add custom role name support"
git push origin main
```

Result: Version 0.2.0 created

### Bug Fix Release (0.2.0 → 0.2.1)

```bash
git commit -m "fix(lambda): handle empty transcripts correctly"
git push origin main
```

Result: Version 0.2.1 created

### Breaking Change (0.2.1 → 1.0.0)

```bash
git commit -m "feat!: change API response format

BREAKING CHANGE: API now returns structured object instead of string."
git push origin main
```

Result: Version 1.0.0 created

### Multiple Commits

If you push multiple commits, the highest version bump wins:

```bash
git commit -m "fix: typo in error message"
git commit -m "feat: add new validation feature"
git commit -m "docs: update README"
git push origin main
```

Result: Version bump determined by `feat:` (MINOR)

## Viewing Releases

### GitHub Releases
Go to: https://github.com/AnthusAI/speaker-role-classifier/releases

Each release includes:
- Version number (tag)
- Release date
- Auto-generated release notes grouped by type
- Links to commits

### CHANGELOG.md
View the full changelog in the repository:
- Organized by version
- Grouped by change type (Features, Bug Fixes, etc.)
- Links to commits and PRs

### Git Tags
```bash
git tag                    # List all tags
git show v1.0.0           # Show specific version
```

## Skipping Release

To commit without triggering a release:

```bash
# Use non-release commit types
git commit -m "chore: update dependencies"
git commit -m "ci: update workflow"
git commit -m "test: add more tests"

# Or add [skip ci]
git commit -m "docs: fix typo [skip ci]"
```

## Manual Release

If needed, you can trigger a release manually:

```bash
# In GitHub Actions UI
Go to Actions → Release → Run workflow
```

## Troubleshooting

### No Release Created

**Possible reasons:**
1. No commits with release-triggering types since last release
2. Only `ci:`, `test:`, or `chore:` commits
3. Commit messages don't follow conventional format

**Solution:**
```bash
# Check recent commits
git log --oneline

# Ensure at least one commit has feat:, fix:, etc.
git commit --amend -m "feat: your feature description"
git push --force origin main
```

### Release Failed

**Check GitHub Actions logs:**
1. Go to Actions tab
2. Click on failed Release workflow
3. Review error messages

**Common issues:**
- Missing GITHUB_TOKEN permissions
- Merge conflicts in CHANGELOG.md
- Invalid commit message format

### Version Not Updated in pyproject.toml

The `@semantic-release/exec` plugin updates the version using sed.

**Verify:**
```bash
# Check current version
grep 'version =' pyproject.toml

# Should match latest Git tag
git describe --tags
```

## Best Practices

### 1. Write Good Commit Messages
```bash
# Good
feat(classifier): add multi-language support
fix(api): handle timeout errors gracefully

# Bad
update code
fix bug
changes
```

### 2. Group Related Changes
```bash
# Instead of many small commits
git commit -m "fix: typo"
git commit -m "fix: another typo"

# Combine them
git commit -m "fix: correct typos in error messages"
```

### 3. Use Conventional Commits from Start
Even before merging to main, use conventional commits in feature branches:
```bash
git checkout -b feature/custom-roles
git commit -m "feat(classifier): add custom role support"
git commit -m "test(classifier): add tests for custom roles"
git commit -m "docs(classifier): document custom role feature"
```

### 4. Review Before Pushing to Main
```bash
# Check what will be released
git log origin/main..HEAD --oneline

# Ensure commit messages are correct
# Amend if needed
git commit --amend -m "feat: better description"
```

### 5. Use Pull Requests
- Create PRs for features
- Use conventional commits in PR
- Squash merge with conventional commit message
- Release happens automatically after merge

## Integration with CI/CD

The semantic release workflow runs **before** the CI/CD pipeline:

```
Push to main
    ↓
Semantic Release (creates version, tag, changelog)
    ↓
CodePipeline/GitHub Actions (tests and deploys)
```

Both workflows run, but semantic release completes first.

## Customization

### Change Version Bump Rules

Edit `.releaserc.json`:

```json
{
  "plugins": [
    [
      "@semantic-release/commit-analyzer",
      {
        "releaseRules": [
          {"type": "docs", "release": false},  // Don't release for docs
          {"type": "refactor", "release": "minor"}  // Minor bump for refactor
        ]
      }
    ]
  ]
}
```

### Customize Changelog Format

Edit `.releaserc.json`:

```json
{
  "plugins": [
    [
      "@semantic-release/release-notes-generator",
      {
        "preset": "conventionalcommits",
        "presetConfig": {
          "types": [
            {"type": "feat", "section": "🚀 Features"},
            {"type": "fix", "section": "🐛 Bug Fixes"}
          ]
        }
      }
    ]
  ]
}
```

### Add More Assets to Commit

Edit `.releaserc.json`:

```json
{
  "plugins": [
    [
      "@semantic-release/git",
      {
        "assets": ["CHANGELOG.md", "pyproject.toml", "package.json"]
      }
    ]
  ]
}
```

## Resources

- [Semantic Release Documentation](https://semantic-release.gitbook.io/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Commit Convention Guide](.github/COMMIT_CONVENTION.md)
- [GitHub Releases](https://github.com/AnthusAI/speaker-role-classifier/releases)

## Support

If you have questions about semantic release:
1. Check this documentation
2. Review [.github/COMMIT_CONVENTION.md](.github/COMMIT_CONVENTION.md)
3. Check GitHub Actions logs for errors
4. Review semantic-release documentation
