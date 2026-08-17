#!/usr/bin/env bash
set -euo pipefail

repo_dir="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
output="${2:-${repo_dir}/static/hero_videos/capture_personal_card_preview.mp4}"
poster="${output%.mp4}_poster.jpg"

marble_dir="${repo_dir}/static/hero_videos/sources/marble"
peg_dir="${repo_dir}/static/peg_videos/w50_odin/kth_nn_stratcp_k4_factory_shaved_bounds2_friction01_leaf200_depth8"

inputs=(
    "${marble_dir}/center_right_episode_04_capture_knn8.mp4"
    "${repo_dir}/static/hero_videos/center_capture_with_particles_1x1.mp4"
    "${peg_dir}/state_004/inference_trace_combined_replay.mp4"
    "${peg_dir}/state_014/inference_trace_combined_replay.mp4"
)

for input in "${inputs[@]}"; do
    if [[ ! -f "${input}" ]]; then
        echo "Missing input: ${input}" >&2
        exit 1
    fi
done

mkdir -p "$(dirname "${output}")"

# The marble sources are already encoded at their intended display speed. The
# peg replays are 0.5x encodes, so setpts=0.5*(PTS-STARTPTS) restores 1x motion.
ffmpeg -hide_banner -y \
    -i "${inputs[0]}" \
    -i "${inputs[1]}" \
    -i "${inputs[2]}" \
    -i "${inputs[3]}" \
    -filter_complex \
    "[0:v]crop=1440:1440:80:0,scale=1080:1080:flags=lanczos,setsar=1,fps=20,tpad=stop_mode=clone:stop_duration=0.35[m0];\
     [1:v]crop=1280:1280:80:0,scale=1080:1080:flags=lanczos,setsar=1,fps=20,tpad=stop_mode=clone:stop_duration=0.50[m1];\
     [2:v]setpts=0.5*(PTS-STARTPTS),crop=886:886:289:90,scale=1080:1080:flags=lanczos,setsar=1,fps=20,tpad=stop_mode=clone:stop_duration=0.40[p0];\
     [3:v]setpts=0.5*(PTS-STARTPTS),crop=886:886:289:90,scale=1080:1080:flags=lanczos,setsar=1,fps=20,tpad=stop_mode=clone:stop_duration=0.40[p1];\
     [m0][m1][p0][p1]concat=n=4:v=1:a=0[out]" \
    -map "[out]" \
    -an \
    -c:v libx264 \
    -preset slow \
    -crf 22 \
    -pix_fmt yuv420p \
    -movflags +faststart \
    "${output}"

ffmpeg -hide_banner -loglevel error -y \
    -ss 0.8 \
    -i "${output}" \
    -frames:v 1 \
    -q:v 2 \
    "${poster}"

ffprobe -v error \
    -show_entries format=duration,size:stream=width,height,r_frame_rate,pix_fmt \
    -of default=noprint_wrappers=1 \
    "${output}"
printf 'Video: %s\nPoster: %s\n' "${output}" "${poster}"
