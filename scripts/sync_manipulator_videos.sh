#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src_root="$repo_root/static/isaac_videos"
dest_root="$repo_root/static/manipulator_videos/single"

if [[ ! -d "$src_root" ]]; then
    echo "Source directory not found: $src_root" >&2
    exit 1
fi

mkdir -p "$dest_root"
shopt -s nullglob

conditions=(c_01 c_02 c_03)
condition_names=(c01 c02 c03)

methods=(nocp pcp lucca ablation_k4 capture_k1 capture_k4)
method_names=(
    particle_no_cp
    pcp
    lucca
    ablation_without_strata
    capture_knn1
    capture_knn4
)

copied=0

for condition_index in "${!conditions[@]}"; do
    condition="${conditions[$condition_index]}"
    condition_name="${condition_names[$condition_index]}"

    for method_index in "${!methods[@]}"; do
        method="${methods[$method_index]}"
        method_name="${method_names[$method_index]}"

        for trace in 1 2 3 4 5; do
            episode="$(printf "%02d" "$((trace - 1))")"
            matches=("$src_root/$method/$condition/"*_run_inference_trace_"$trace"_combined_replay.mp4)

            if [[ "${#matches[@]}" -ne 1 ]]; then
                echo "Expected exactly one source for $method/$condition trace $trace, found ${#matches[@]}." >&2
                exit 1
            fi

            dest="$dest_root/${condition_name}_episode_${episode}_${method_name}.mp4"
            cp -f "${matches[0]}" "$dest"
            copied="$((copied + 1))"
        done
    done
done

if [[ "$copied" -ne 90 ]]; then
    echo "Expected to copy 90 videos, copied $copied." >&2
    exit 1
fi

echo "Copied $copied videos into $dest_root"
