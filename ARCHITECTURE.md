# Architecture

## Application boundary

TaskFlow has thin FastAPI route handlers, Pydantic input/output validation, isolated CRUD functions, SQLAlchemy request-scoped sessions, and SQLite for local setup. `DATABASE_URL` keeps it ready for PostgreSQL. Middleware records total requests, non-5xx responses, 5xx responses, uptime, status counts, and version in Prometheus text format.

## Delivery boundary

The deployment artifact is `ghcr.io/<owner>/taskflow-api@sha256:<digest>`. SHA and `latest` tags are convenience labels; the digest is used for deploys because it identifies exact image bytes. The deploy script rejects tags and refuses to build on a deployment host.

```mermaid
sequenceDiagram
  participant Dev as Developer
  participant GH as GitHub Actions
  participant Registry as GHCR
  participant Stg as Staging Runner
  participant Prod as Protected Production Runner
  Dev->>GH: Open PR
  GH->>GH: lint, type, test, audit, build, scan
  Dev->>GH: Merge reviewed PR
  GH->>Registry: Push image; capture digest
  GH->>Stg: Pull/deploy digest; health and smoke test
  Dev->>GH: Manually dispatch production
  GH->>Prod: Wait for Environment review
  GH->>Prod: Deploy same digest and observe metrics
  alt threshold breached
    Prod->>Prod: Restore previous stable digest
  else healthy
    Prod->>Prod: Record stable digest
  end
```

## Rollback model

The single Compose host is a **local blue/green approximation**. Before replacement, it records the old image as `previous-stable-image`; only after monitoring passes does it mark the candidate `stable-image`. A real rollback is performed: Docker pulls that old digest, recreates the service, polls health, and runs a smoke test. It is not zero-downtime blue/green because a single host lacks parallel traffic pools and a load balancer.

For cloud production, keep the digest and approval contract but deploy parallel revisions behind a load balancer. Kubernetes maps this to Deployments/Services/Ingress plus Argo Rollouts or Flagger; AWS maps it to ECS/EKS behind an ALB with CloudWatch or Prometheus alerts.

`SIMULATE_FAILURE=true` is deliberately bounded to `GET /api/demo/failure`. It produces a normal handled 500 only for that endpoint, does not alter task data, and is enabled only by the production workflow's explicit demo input.
