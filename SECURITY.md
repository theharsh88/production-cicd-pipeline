# Security

## Enforced layers

- Pull requests use Ruff, Black, MyPy, tests, coverage, and pip-audit.
- Trivy checks the repository filesystem and built image for high/critical vulnerabilities (unfixed findings are reported but do not block by default).
- The Docker image uses a small pinned Python release tag, minimal runtime dependencies, `.dockerignore`, a non-root user, and a health check.
- Workflows have least privilege: read-only content by default, `packages: write` only for publishing, and `packages: read` only for deployment.
- Dependabot creates weekly Python and GitHub Actions update pull requests.

## Secrets

GHCR publishing uses the short-lived GitHub token. `SLACK_WEBHOOK_URL` is optional and belongs in GitHub repository/environment Secrets. Workflows tolerate its absence. Never commit credentials, registry tokens, cloud keys, database passwords, or a populated deployment `.env`.

Enable GitHub Secret scanning and Push protection in **Settings → Code security and analysis**. Protect `main` with PRs, review, required checks, and restricted pushes.

## Production hardening path

Pin action versions to reviewed commit SHAs, pin the base image to its reviewed digest, generate SBOM/provenance attestations, sign images with Cosign, enforce digest-only images by policy, use OIDC identities, centralize audit logs, and keep OS/package patching current.
