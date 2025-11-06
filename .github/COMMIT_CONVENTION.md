# Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types

- **feat**: A new feature (triggers MINOR version bump)
- **fix**: A bug fix (triggers PATCH version bump)
- **perf**: Performance improvement (triggers PATCH version bump)
- **docs**: Documentation changes (triggers PATCH version bump)
- **refactor**: Code refactoring (triggers PATCH version bump)
- **build**: Build system changes (triggers PATCH version bump)
- **ci**: CI/CD changes (no version bump)
- **test**: Test changes (no version bump)
- **chore**: Other changes (no version bump)

## Breaking Changes

Add `BREAKING CHANGE:` in the footer or `!` after type to trigger MAJOR version bump:

```
feat!: remove deprecated API endpoint

BREAKING CHANGE: The /v1/classify endpoint has been removed. Use /v2/classify instead.
```

## Examples

### Feature (Minor Version Bump)
```
feat(classifier): add support for custom role names

Allow users to specify custom role names instead of just Agent/Customer.
This enables more flexible classification for different use cases.
```

### Bug Fix (Patch Version Bump)
```
fix(lambda): handle empty transcript gracefully

Previously would crash with KeyError when transcript was empty.
Now returns appropriate error message.

Fixes #123
```

### Performance Improvement (Patch Version Bump)
```
perf(classifier): optimize speaker detection algorithm

Reduced API calls by 30% through better caching.
```

### Documentation (Patch Version Bump)
```
docs(readme): add CI/CD setup instructions

Added comprehensive guide for setting up CodePipeline and GitHub Actions.
```

### Breaking Change (Major Version Bump)
```
feat!: change API response format

BREAKING CHANGE: The API now returns a structured object instead of plain text.
Response format changed from string to {"transcript": string, "log": array}.

Migration guide:
- Old: result = classify_speakers(text)
- New: result = classify_speakers(text)['transcript']
```

### No Version Bump
```
ci: update CodeBuild image to STANDARD_7_0

chore: update dependencies

test: add tests for safeguard feature
```

## Scopes

Common scopes for this project:
- `classifier`: Core classification logic
- `lambda`: Lambda function handler
- `ci`: CI/CD pipeline
- `tests`: Test suite
- `docs`: Documentation
- `api`: API interface

## Tips

1. **Use imperative mood**: "add feature" not "added feature"
2. **Keep subject under 72 characters**
3. **Capitalize first letter of subject**
4. **No period at end of subject**
5. **Separate subject from body with blank line**
6. **Wrap body at 72 characters**
7. **Use body to explain what and why, not how**

## Automated Versioning

Based on commits since last release:
- `feat:` → 0.1.0 → 0.2.0 (minor)
- `fix:` → 0.1.0 → 0.1.1 (patch)
- `feat!:` or `BREAKING CHANGE:` → 0.1.0 → 1.0.0 (major)

## Changelog

The changelog is automatically generated and includes:
- Features
- Bug Fixes
- Performance Improvements
- Breaking Changes
- Documentation updates
- Code refactoring

## Skip CI

To skip CI/CD pipeline, add `[skip ci]` to commit message:
```
docs: update README [skip ci]
```

Note: Release commits automatically include `[skip ci]` to prevent infinite loops.
