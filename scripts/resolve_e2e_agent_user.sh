#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 4 ]; then
  printf 'usage: %s <uid> <gid> [service-user] [preferred-user]\n' "$0" >&2
  exit 2
fi

requested_uid="$1"
requested_gid="$2"
service_user="${3:-jarvis-box}"
preferred_user="${4:-e2e-agent}"

case "$requested_uid:$requested_gid" in
  *[!0-9:]*|:*|*:)
    printf 'requested runtime-agent UID/GID must be numeric: %s:%s\n' \
      "$requested_uid" "$requested_gid" >&2
    exit 2
    ;;
esac
[ "$requested_uid" -ne 0 ] || {
  printf 'runtime-agent UID must be non-root\n' >&2
  exit 2
}
[ "$requested_gid" -ne 0 ] || {
  printf 'runtime-agent GID must be non-root\n' >&2
  exit 2
}

if id -u "$service_user" >/dev/null 2>&1 \
  && [ "$(id -u "$service_user")" = "$requested_uid" ]; then
  printf 'runtime-agent UID must differ from %s service UID\n' "$service_user" >&2
  exit 2
fi

existing_passwd="$(getent passwd "$requested_uid" || true)"
existing_user="$(printf '%s\n' "$existing_passwd" | awk -F: 'NR == 1 { print $1 }')"
if [ -n "$existing_user" ]; then
  [ "$existing_user" != "$service_user" ] || {
    printf 'runtime-agent account must differ from service account %s\n' "$service_user" >&2
    exit 2
  }
  existing_gid="$(id -g "$existing_user")"
  [ "$existing_gid" = "$requested_gid" ] || {
    printf 'existing UID %s belongs to %s with GID %s, not requested GID %s\n' \
      "$requested_uid" "$existing_user" "$existing_gid" "$requested_gid" >&2
    exit 2
  }
  printf '%s\n' "$existing_user"
  exit 0
fi

getent group "$requested_gid" >/dev/null \
  || groupadd -g "$requested_gid" "$preferred_user"

candidate="$preferred_user"
if getent passwd "$candidate" >/dev/null; then
  candidate="${preferred_user}-${requested_uid}"
fi
if getent passwd "$candidate" >/dev/null; then
  printf 'cannot allocate runtime-agent user name: %s\n' "$candidate" >&2
  exit 2
fi

useradd \
  -u "$requested_uid" \
  -g "$requested_gid" \
  -M \
  -d /e2e/home \
  -s /bin/bash \
  "$candidate"
[ "$(id -u "$candidate")" = "$requested_uid" ] \
  && [ "$(id -g "$candidate")" = "$requested_gid" ] || {
    printf 'created runtime-agent user does not match requested UID/GID\n' >&2
    exit 2
  }
printf '%s\n' "$candidate"
