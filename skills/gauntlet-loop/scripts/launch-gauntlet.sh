#!/usr/bin/env bash
# Launch a Gauntlet Loop in a clean-room Claude Code session.
#
#   launch-gauntlet.sh <run-dir> [permission-mode] [model]
#
# Clean room means: no MCP servers, no skills, no global CLAUDE.md. Rule one of
# the method is "let the agent choose the route", and every skill or MCP server
# in scope is a route already chosen for it.
#
# Defaults: permission-mode auto (classifier-gated, survives a walk-away run),
# model opus (the article's pick for visual and creative work).

set -euo pipefail

RUN_DIR="${1:-}"
MODE="${2:-auto}"
MODEL="${3:-opus}"

if [ -z "$RUN_DIR" ]; then
  echo "usage: launch-gauntlet.sh <run-dir> [permission-mode] [model]" >&2
  echo "  permission-mode: auto (default) | acceptEdits | bypassPermissions" >&2
  exit 64
fi

RUN_DIR="$(cd "$RUN_DIR" 2>/dev/null && pwd)" || {
  echo "error: no such directory: ${1}" >&2
  exit 66
}

PROMPT_FILE="$RUN_DIR/GAUNTLET.md"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "error: $PROMPT_FILE not found." >&2
  echo "The gauntlet prompt is the deliverable. Write it before launching." >&2
  exit 66
fi

if [ ! -d "$RUN_DIR/reference" ] || [ -z "$(ls -A "$RUN_DIR/reference" 2>/dev/null)" ]; then
  echo "warning: $RUN_DIR/reference is missing or empty." >&2
  echo "A bar the critic cannot open is not a bar, and the run will stop early." >&2
  printf "Launch anyway? [y/N] " >&2
  read -r reply
  case "$reply" in
    [yY]*) ;;
    *) echo "Aborted." >&2; exit 1 ;;
  esac
fi

if ! grep -qi 'ultracode' "$PROMPT_FILE"; then
  echo "warning: 'ultracode' is not in GAUNTLET.md." >&2
  echo "That word is the keyword trigger for multi-agent workflows, not decoration." >&2
fi

if [ "$MODE" = "bypassPermissions" ]; then
  cat >&2 <<'WARN'

  bypassPermissions: nothing in this run will be gated. For hours. Unattended.
  Only continue if this directory holds nothing you would mind losing, and is
  not $HOME or a real repository.

WARN
  printf "  Continue? [y/N] " >&2
  read -r reply
  case "$reply" in
    [yY]*) ;;
    *) echo "Aborted." >&2; exit 1 ;;
  esac
fi

cat >&2 <<BANNER

  Gauntlet Loop
  ─────────────────────────────────────────────
  run       $RUN_DIR
  model     $MODEL
  effort    xhigh + ultracode
  perms     $MODE
  isolation no MCP, no skills, no global CLAUDE.md

  Progress page (once it exists): $RUN_DIR/progress.html
  Stop the run with Esc. It will still be improving when you do.
  ─────────────────────────────────────────────

BANNER

cd "$RUN_DIR"

exec claude \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --disable-slash-commands \
  --setting-sources project,local \
  --effort xhigh \
  --permission-mode "$MODE" \
  --model "$MODEL" \
  "$(cat "$PROMPT_FILE")"
