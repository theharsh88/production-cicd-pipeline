# Contributing

1. Branch from current `main` as `feature/<short-description>`.
2. Keep changes focused and add tests for changed behavior.
3. Run `ruff check .`, `black --check .`, `mypy app`, and `pytest --cov=app --cov-report=term-missing`.
4. Open a pull request to `main`; do not bypass protection rules.
5. Resolve review comments and require the PR validation workflow to pass before merge.

Never commit generated databases, `.env` files, credentials, or deployment state. Changes to deploy or rollback behavior must update documentation and add an executable verification path.
