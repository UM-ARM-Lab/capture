#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  printf 'Usage: %s SOURCE_ROOT OUTPUT_ROOT\n' "$0" >&2
  exit 2
fi

source_root="$1"
output_root="$2"
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

if [[ ! -d "$source_root" ]]; then
  printf 'Missing source directory: %s\n' "$source_root" >&2
  exit 1
fi
if [[ -e "$output_root" ]]; then
  printf 'Output path already exists: %s\n' "$output_root" >&2
  exit 1
fi
if [[ ! -f "$font" ]]; then
  printf 'Missing font: %s\n' "$font" >&2
  exit 1
fi

mkdir -p "$output_root"
export source_root output_root font

find "$source_root" -type f -name '*.mp4' -print0 | sort -z | xargs -0 -P 4 -I{} bash -c '
  input="$1"
  relative="${input#"$source_root"/}"
  output="$output_root/$relative"
  mkdir -p "$(dirname "$output")"
  ffmpeg -hide_banner -loglevel error -y -i "$input" -an \
    -vf "setpts=0.5*PTS,fps=30,drawbox=x=450:y=1120:w=430:h=85:color=black:t=fill,drawtext=fontfile=${font}:text=0.5x\\ speed:fontcolor=white:fontsize=48:x=478:y=1143,tpad=stop_mode=clone:stop_duration=0.4" \
    -c:v h264_nvenc -preset p6 -tune hq -rc vbr -cq 23 -b:v 0 \
    -pix_fmt yuv420p -movflags +faststart "$output"
' _ {}

source_count="$(find "$source_root" -type f -name '*.mp4' | wc -l)"
output_count="$(find "$output_root" -type f -name '*.mp4' | wc -l)"
if [[ "$source_count" -ne 120 || "$output_count" -ne "$source_count" ]]; then
  printf 'Unexpected video counts: source=%s output=%s\n' "$source_count" "$output_count" >&2
  exit 1
fi

while IFS= read -r -d '' video; do
  dimensions="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$video")"
  if [[ "$dimensions" != '3024,1308,30/1' ]]; then
    printf 'Unexpected video format %s: %s\n' "$video" "$dimensions" >&2
    exit 1
  fi
done < <(find "$output_root" -type f -name '*.mp4' -print0)

printf 'Wrote %s validated 0.5x videos to %s\n' "$output_count" "$output_root"
