# Deployment guide

## Target setup

Use two isolated Linux VMs or Docker hosts for the portfolio demonstration. Install Docker Engine, the Compose plugin, Python 3, and a GitHub Actions self-hosted runner. Label one runner `staging`, the other `production`; workflows require `self-hosted` plus that label. Let the runner service account use Docker and read the GHCR package.

GitHub-hosted runners deliberately do not deploy here: they cannot safely access a private host Docker socket. A production cloud implementation should instead use OIDC to a narrowly scoped cloud identity.

## Staging

Main CI invokes the reusable staging workflow with the GHCR digest it just produced. It runs:

```bash
bash scripts/deploy_compose.sh staging 'ghcr.io/OWNER/taskflow-api@sha256:...'
```

This writes host-local deployment state to `deployment/staging/.env`, pulls the exact image, starts it, polls `/health`, and checks `/api/tasks`. The `.env` file is ignored by Git.

## Production approval

Create a repository Environment called `production`, open **Settings → Environments → production**, and configure **Required reviewers**. Production is `workflow_dispatch` only. The `environment: production` job cannot run commands until GitHub has received reviewer approval. Use a digest that has already passed staging.

Before candidate deployment, production saves its current digest as `state/previous-stable-image`. Successful monitoring writes `state/stable-image`. Those files are intentionally host-local for a demo; a cloud deployment controller should persist release history itself.

## Variables

Copy a deployment `.env.example` only to set a port or threshold. The workflow supplies `TASKFLOW_IMAGE`; do not add secrets to the file.

| Variable | Meaning |
| --- | --- |
| `TASKFLOW_IMAGE` | Required immutable image digest |
| `PORT` | Host port (8001 staging; 8000 production) |
| `ROLLBACK_ERROR_RATE_THRESHOLD` | 5xx percentage which triggers rollback |
| `ROLLBACK_WINDOW_SECONDS` | Pre-check observation delay |
| `SIMULATE_FAILURE` | Demo-only endpoint failure switch |

## Rollback

Any failed deploy check or monitoring threshold causes `scripts/rollback.sh` to restore the saved digest, start it, and re-run health plus smoke checks. **Emergency rollback** offers the same guard-railed action manually. It refuses missing or mutable rollback references so a failed rollback is visible and actionable.

## Cloud migration

Replace Compose commands with a Kubernetes/ECS deploy, retain the immutable digest, and let Argo Rollouts, Flagger, ECS CodeDeploy, or a load-balancer controller shift traffic. Feed Prometheus/CloudWatch alert signals into rollout promotion, place state in the platform, use managed PostgreSQL, and use OIDC rather than permanent cloud credentials.
