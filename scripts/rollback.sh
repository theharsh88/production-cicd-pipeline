#!/usr/bin/env bash
# Restore the last known-good immutable image in the Docker Compose production demo.
set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-deployment/production/docker-compose.yml}"
ENV_FILE="${ENV_FILE:-deployment/production/.env}"
STATE_DIR="${STATE_DIR:-deployment/production/state}"
BASE_URL="${BASE_URL:-http://localhost:8000}"
PREVIOUS_FILE="$STATE_DIR/previous-stable-image"

if [[ ! -s "$PREVIOUS_FILE" ]]; then
  echo "Rollback failed: no previous stable image recorded at $PREVIOUS_FILE" >&2
  exit 1
fi

previous_image="$(<"$PREVIOUS_FILE")"
mkdir -p "$STATE_DIR"
tmp_env="$(mktemp)"
trap 'rm -f "$tmp_env"' EXIT

if [[ -f "$ENV_FILE" ]]; then
  grep -Ev '^(TASKFLOW_IMAGE|SIMULATE_FAILURE)=' "$ENV_FILE" > "$tmp_env" || true
fi
printf 'TASKFLOW_IMAGE=%s\n' "$previous_image" >> "$tmp_env"
printf 'SIMULATE_FAILURE=false\n' >> "$tmp_env"

echo "Rolling back to immutable image: $previous_image"
docker compose --env-file "$tmp_env" -f "$COMPOSE_FILE" pull taskflow
docker compose --env-file "$tmp_env" -f "$COMPOSE_FILE" up -d --remove-orphans taskflow
python3 scripts/check_deployment_health.py \
  --base-url "$BASE_URL" --timeout "${HEALTH_TIMEOUT_SECONDS:-60}"
python3 scripts/smoke_test.py --base-url "$BASE_URL"
mv "$tmp_env" "$ENV_FILE"
trap - EXIT
echo "Rollback succeeded: $previous_image"
