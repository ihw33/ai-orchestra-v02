#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-ihw33/ai-orchestra-v02}"

# name  color   description
labels=(
  "epic BFD4F2 Epic level work"
  "priority-high D73A4A High priority"
  "mvp C2E0C6 MVP task"
  "orchestra:phase1 1D76DB Phase 1 (MVP)"
  "bug D73A4A Bug"
  "area:core 0E8A16 Core modules"
  "area:protocol 0E8A16 Protocol/handshake"
  "area:retry 0E8A16 Retry/Backoff"
  "area:idempotency 0E8A16 Idempotency"
  "area:controllers 0E8A16 Controllers"
  "area:tmux 0E8A16 tmux/iTerm2"
  "tests 5319E7 Tests"
)

for ((i=0; i<${#labels[@]}; i+=3)); do
  name="${labels[i]}"; color="${labels[i+1]}"; desc="${labels[i+2]}"
  echo "Creating/updating: ${name}"
  gh label create "$name" --color "$color" --description "$desc" -R "$REPO" 2>/dev/null || \
  gh label edit "$name" --color "$color" --description "$desc" -R "$REPO"
done