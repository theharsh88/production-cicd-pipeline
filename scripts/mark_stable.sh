#!/usr/bin/env bash
# Record the live production digest only after post-deploy monitoring has passed.
set -Eeuo pipefail

env_file="${ENV_FILE:-deployment/production/.env}"
state_dir="${STATE_DIR:-deployment/production/state}"
image="$(sed -n 's/^TASKFLOW_IMAGE=//p' "$env_file" | head -n1)"
if [[ "$image" != *@sha256:* ]]; then
  echo "Cannot mark stable: production image is not a digest" >&2
  exit 1
fi
mkdir -p "$state_dir"
printf '%s\n' "$image" > "$state_dir/stable-image"
echo "Marked stable image: $image"
