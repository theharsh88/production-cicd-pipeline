#!/usr/bin/env bash
# Deploy exactly the supplied immutable image reference; never build on the target host.
set -Eeuo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <staging|production> <image@sha256:...>" >&2
  exit 64
fi

environment="$1"
image="$2"
if [[ "$environment" != "staging" && "$environment" != "production" ]]; then
  echo "Environment must be staging or production" >&2
  exit 64
fi
if [[ "$image" != *@sha256:* ]]; then
  echo "Refusing non-digest image reference: $image" >&2
  exit 65
fi

deploy_dir="deployment/$environment"
compose_file="$deploy_dir/docker-compose.yml"
env_file="$deploy_dir/.env"
state_dir="$deploy_dir/state"
default_port=8000
if [[ "$environment" == "staging" ]]; then
  default_port=8001
fi
base_url="${BASE_URL:-http://localhost:${PORT:-$default_port}}"
mkdir -p "$state_dir"

if [[ "$environment" == "production" && -f "$env_file" ]]; then
  old_image="$(sed -n 's/^TASKFLOW_IMAGE=//p' "$env_file" | head -n1)"
  if [[ "$old_image" == *@sha256:* && "$old_image" != "$image" ]]; then
    printf '%s\n' "$old_image" > "$state_dir/previous-stable-image"
  fi
fi

tmp_env="$(mktemp)"
trap 'rm -f "$tmp_env"' EXIT
if [[ -f "$env_file" ]]; then
  grep -v '^TASKFLOW_IMAGE=' "$env_file" > "$tmp_env" || true
fi
printf 'TASKFLOW_IMAGE=%s\n' "$image" >> "$tmp_env"
mv "$tmp_env" "$env_file"
trap - EXIT

docker compose --env-file "$env_file" -f "$compose_file" pull taskflow
docker compose --env-file "$env_file" -f "$compose_file" up -d --remove-orphans taskflow
python3 scripts/check_deployment_health.py \
  --base-url "$base_url" --timeout "${HEALTH_TIMEOUT_SECONDS:-60}"
python3 scripts/smoke_test.py --base-url "$base_url"
echo "Deployment smoke checks passed for $environment: $image"
