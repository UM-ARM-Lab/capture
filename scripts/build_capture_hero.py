#!/usr/bin/env python3
import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUTCOME_TAIL_SECONDS = 0.8
OUTCOME_HOLD_SECONDS = 1.2
HERO_WIDTH = 3200
HERO_HEIGHT = 1440
HALF_WIDTH = HERO_WIDTH // 2


@dataclass(frozen=True)
class Segment:
    name: str
    left: Path
    right: Path
    crop: str
    source_speed: float
    target_speed: float
    outcome_tail_seconds: float
    left_outcome: str
    right_outcome: str


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def outcome_filter(*, start: float, outcome: str) -> str:
    if outcome == "success":
        symbol = "✓"
        color = "#23b95f"
        label = "Success"
    elif outcome == "pit":
        symbol = "×"
        color = "#eb3939"
        label = "Fell in Pit"
    elif outcome == "timeout":
        symbol = "×"
        color = "#eb3939"
        label = "Timed Out"
    else:
        raise ValueError(f"Unsupported outcome: {outcome}")
    return (
        f"drawbox=color=#80868e@0.51:t=fill:enable='gte(t\\,{start:.3f})',"
        f"drawtext=fontfile={FONT}:text='{symbol}':fontcolor={color}:bordercolor=white:borderw=30:"
        f"fontsize=662:x=(w-text_w)/2:y=0.42*h-text_h/2:enable='gte(t\\,{start:.3f})',"
        f"drawtext=fontfile={FONT}:text='{label}':fontcolor=#fafbfd:bordercolor=black:borderw=8:"
        f"fontsize=120:x=(w-text_w)/2:y=0.63*h:enable='gte(t\\,{start:.3f})'"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timing-output", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    peg_root = repo / "static/peg_videos/w50_odin"
    marble_root = repo / "static/hero_videos/sources/marble"
    capture_method = (
        "kth_nn_stratcp_k4_factory_shaved_bounds2_friction01_leaf200_depth8"
    )
    segments = (
        Segment(
            name="marble_center_right_04",
            left=marble_root / "center_right_episode_04_pcp.mp4",
            right=marble_root / "center_right_episode_04_capture_knn8.mp4",
            crop="1600:1440:0:0",
            source_speed=0.5,
            target_speed=0.5,
            outcome_tail_seconds=0.0,
            left_outcome="pit",
            right_outcome="success",
        ),
        Segment(
            name="marble_top_center_02",
            left=marble_root / "top_center_episode_02_pcp.mp4",
            right=marble_root / "top_center_episode_02_capture_knn8.mp4",
            crop="1600:1440:0:0",
            source_speed=0.5,
            target_speed=0.5,
            outcome_tail_seconds=0.0,
            left_outcome="pit",
            right_outcome="success",
        ),
        *(
            Segment(
                name=f"peg_state_{state}",
                left=peg_root
                / "pcp"
                / f"state_{state}"
                / "inference_trace_combined_replay.mp4",
                right=peg_root
                / capture_method
                / f"state_{state}"
                / "inference_trace_combined_replay.mp4",
                crop="984:886:240:90",
                source_speed=0.5,
                target_speed=1.0,
                outcome_tail_seconds=OUTCOME_TAIL_SECONDS,
                left_outcome="timeout",
                right_outcome="success",
            )
            for state in ("014", "027", "019", "029")
        ),
    )

    missing = [
        path
        for segment in segments
        for path in (segment.left, segment.right)
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"Missing hero source videos: {missing}")
    if not Path(FONT).is_file():
        raise FileNotFoundError(FONT)

    command = ["ffmpeg", "-hide_banner", "-y"]
    for segment in segments:
        command.extend(("-i", str(segment.left), "-i", str(segment.right)))

    left_label = (
        f"drawtext=fontfile={FONT}:text='PCP (baseline)':fontcolor=white:bordercolor=black@0.647:"
        "borderw=4:fontsize=72:box=1:boxcolor=black@0.451:boxborderw=22:x=66:y=h-text_h-58"
    )
    right_label = (
        f"drawtext=fontfile={FONT}:text='CaPTURe (ours)':fontcolor=white:bordercolor=black@0.647:"
        "borderw=4:fontsize=72:box=1:boxcolor=black@0.451:boxborderw=22:x=66:y=h-text_h-58"
    )

    filters = []
    timing = []
    timeline_cursor = 0.0
    segment_outputs = []
    for index, segment in enumerate(segments):
        left_source_duration = (
            probe_duration(segment.left) - segment.outcome_tail_seconds
        )
        right_source_duration = (
            probe_duration(segment.right) - segment.outcome_tail_seconds
        )
        if min(left_source_duration, right_source_duration) <= 0:
            raise ValueError(f"Invalid source duration for {segment.name}")
        speedup = segment.target_speed / segment.source_speed
        left_duration = left_source_duration / speedup
        right_duration = right_source_duration / speedup
        segment_duration = max(left_duration, right_duration) + OUTCOME_HOLD_SECONDS
        left_pad = segment_duration - left_duration
        right_pad = segment_duration - right_duration
        left_input = index * 2
        right_input = left_input + 1
        left_name = f"s{index}_l"
        right_name = f"s{index}_r"
        output_name = f"segment_{index}"

        filters.append(
            f"[{left_input}:v]trim=duration={left_source_duration:.3f},setpts=(PTS-STARTPTS)/{speedup:.3f},"
            f"crop={segment.crop},"
            f"scale={HALF_WIDTH}:{HERO_HEIGHT}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={HALF_WIDTH}:{HERO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=25,"
            f"tpad=stop_mode=clone:stop_duration={left_pad:.3f},trim=duration={segment_duration:.3f},"
            f"{outcome_filter(start=left_duration, outcome=segment.left_outcome)},{left_label}[{left_name}]"
        )
        filters.append(
            f"[{right_input}:v]trim=duration={right_source_duration:.3f},setpts=(PTS-STARTPTS)/{speedup:.3f},"
            f"crop={segment.crop},"
            f"scale={HALF_WIDTH}:{HERO_HEIGHT}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={HALF_WIDTH}:{HERO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=25,"
            f"tpad=stop_mode=clone:stop_duration={right_pad:.3f},trim=duration={segment_duration:.3f},"
            f"{outcome_filter(start=right_duration, outcome=segment.right_outcome)},{right_label}[{right_name}]"
        )
        speed_label = f"{segment.target_speed:g}x"
        filters.append(
            f"[{left_name}][{right_name}]hstack=inputs=2,"
            "drawbox=x=(iw-4)/2:y=0:w=4:h=ih:color=white@0.72:t=fill,"
            f"drawtext=fontfile={FONT}:text='{speed_label}':fontcolor=white:bordercolor=black@0.8:"
            "borderw=3:fontsize=50:x=w-text_w-40:y=h-text_h-34"
            f"[{output_name}]"
        )
        segment_outputs.append(f"[{output_name}]")
        timing.append(
            {
                "name": segment.name,
                "kind": "marble" if segment.name.startswith("marble") else "peg",
                "start": round(timeline_cursor, 3),
                "end": round(timeline_cursor + segment_duration, 3),
                "speed": segment.target_speed,
            }
        )
        timeline_cursor += segment_duration

    filters.append(f"{''.join(segment_outputs)}concat=n={len(segments)}:v=1:a=0[out]")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command.extend(
        (
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(args.output),
        )
    )
    subprocess.run(command, check=True)
    args.timing_output.write_text(json.dumps(timing, indent=2) + "\n")
    print(json.dumps(timing, indent=2))


if __name__ == "__main__":
    main()
