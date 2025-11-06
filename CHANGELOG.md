## 1.0.0 (2025-11-06)


### ⚠ BREAKING CHANGES

* Tests now mock OpenAI by default. Use -m integration to run real API tests.

Features:
- Automated versioning based on commit messages
- Automatic CHANGELOG.md generation
- Automatic GitHub releases
- Mock OpenAI API by default in tests
- Integration test marker for real API testing

Documentation:
- SEMANTIC-RELEASE.md: Complete semantic release guide
- .github/COMMIT_CONVENTION.md: Commit message guidelines
- Updated README with testing instructions

### Features

* add semantic release and mock OpenAI API calls by default ([9327dfe](https://github.com/AnthusAI/speaker-role-classifier/commit/9327dfe7b9b2fd582e30e2a7bd869601b7d9ced4))
