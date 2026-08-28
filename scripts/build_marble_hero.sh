#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 0 ]]; then
  printf 'Usage: %s\n' "$0" >&2
  exit 2
fi

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$repo/scripts/build_capture_hero.py" \
  --repo "$repo" \
  --output "$repo/static/hero_videos/capture_vs_pcp_marble_hero.mp4" \
  --timing-output "$repo/static/hero_videos/capture_vs_pcp_marble_hero_timing.json"

ffmpeg -hide_banner -loglevel error -y \
  -i "$repo/static/hero_videos/capture_vs_pcp_marble_hero.mp4" \
  -frames:v 1 -q:v 2 \
  "$repo/static/hero_videos/capture_vs_pcp_marble_hero_poster.jpg"
