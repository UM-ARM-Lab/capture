#!/usr/bin/env python3
import argparse
import csv
import json
import subprocess
from pathlib import Path


METHODS = (
    ("particle_nocp", "ParticleNoCP"),
    ("pcp", "PCP"),
    ("lucca", "LUCCa"),
    ("kth_nn_locart_k4", "Ablation w/o\nstratum label (kNN=4)"),
    ("min_stratcp_factory_shaved_bounds2", "Ablation\n(kNN=1)"),
    (
        "kth_nn_stratcp_k4_factory_shaved_bounds2_friction01_leaf200_depth8",
        "CaPTURe (kNN=4)",
    ),
)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CELL_WIDTH = 960
CELL_HEIGHT = 540
OUTCOME_TAIL_SECONDS = 0.8
OUTCOME_HOLD_SECONDS = 1.0


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


def escape_drawtext(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def load_outcomes(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    outcomes = {row["state"]: row for row in rows}
    if set(outcomes) != {f"{index:03d}" for index in range(20)}:
        raise ValueError(f"Expected outcomes for states 000-019 in {path}")
    return outcomes


def build_state(
    *,
    state: str,
    video_root: Path,
    output_root: Path,
    outcomes: dict[str, dict[str, str]],
) -> None:
    inputs = [
        video_root / method / f"state_{state}" / "inference_trace_combined_replay.mp4"
        for method, _ in METHODS
    ]
    missing = [path for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing grid inputs: {missing}")

    dynamic_durations = [probe_duration(path) - OUTCOME_TAIL_SECONDS for path in inputs]
    if min(dynamic_durations) <= 0:
        raise ValueError(
            f"Invalid source duration for state {state}: {dynamic_durations}"
        )
    grid_duration = max(dynamic_durations) + OUTCOME_HOLD_SECONDS

    filters = []
    for index, ((method, label), dynamic_duration) in enumerate(
        zip(METHODS, dynamic_durations, strict=True)
    ):
        result = outcomes[state][method]
        if result not in {"success", "timeout"}:
            raise ValueError(
                f"Invalid outcome {result!r} for state {state}, method {method}"
            )
        pad = grid_duration - dynamic_duration
        symbol = "✓" if result == "success" else "×"
        symbol_color = "#23b95f" if result == "success" else "#eb3939"
        outcome_label = "Success" if result == "success" else "Timed Out"
        filters.append(
            f"[{index}:v]trim=duration={dynamic_duration:.3f},setpts=PTS-STARTPTS,"
            f"crop=906:509:314:168,scale={CELL_WIDTH}:{CELL_HEIGHT}:flags=lanczos,fps=30,"
            f"tpad=stop_mode=clone:stop_duration={pad:.3f},trim=duration={grid_duration:.3f},"
            f"drawtext=fontfile={FONT}:text='{escape_drawtext(label)}':fontcolor=white:fontsize=31:"
            f"line_spacing=3:box=1:boxcolor=black@0.58:boxborderw=12:x=18:y=h-text_h-14,"
            f"drawbox=color=#80868e@0.51:t=fill:enable='gte(t\\,{dynamic_duration:.3f})',"
            f"drawtext=fontfile={FONT}:text='{symbol}':fontcolor={symbol_color}:bordercolor=white:borderw=13:"
            f"fontsize=245:x=(w-text_w)/2:y=0.42*h-text_h/2:enable='gte(t\\,{dynamic_duration:.3f})',"
            f"drawtext=fontfile={FONT}:text='{outcome_label}':fontcolor=white:bordercolor=black:borderw=4:"
            f"fontsize=54:x=(w-text_w)/2:y=0.64*h:enable='gte(t\\,{dynamic_duration:.3f})'[v{index}]"
        )

    filters.append(
        "[v0][v1][v2][v3][v4][v5]"
        "xstack=inputs=6:layout=0_0|960_0|1920_0|0_540|960_540|1920_540:fill=black,"
        "drawbox=x=958:y=0:w=4:h=ih:color=black@1.0:t=fill,"
        "drawbox=x=1918:y=0:w=4:h=ih:color=black@1.0:t=fill,"
        "drawbox=x=0:y=538:w=iw:h=4:color=black@1.0:t=fill,"
        f"drawtext=fontfile={FONT}:text='0.5x':fontcolor=white:bordercolor=black@0.8:"
        "borderw=2:fontsize=30:x=w-text_w-18:y=h-text_h-10[out]"
    )

    output = output_root / f"state_{state}_all_methods_physical.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for path in inputs:
        command.extend(("-i", str(path)))
    command.extend(
        (
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-an",
            "-c:v",
            "h264_nvenc",
            "-preset",
            "p6",
            "-tune",
            "hq",
            "-rc",
            "vbr",
            "-cq",
            "23",
            "-b:v",
            "0",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        )
    )
    subprocess.run(command, check=True)
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video-root", type=Path, required=True)
    parser.add_argument("--outcomes", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--state", action="append", choices=[f"{index:03d}" for index in range(20)]
    )
    args = parser.parse_args()

    if not args.video_root.is_dir():
        raise FileNotFoundError(args.video_root)
    if not args.outcomes.is_file():
        raise FileNotFoundError(args.outcomes)
    if not Path(FONT).is_file():
        raise FileNotFoundError(FONT)

    outcomes = load_outcomes(args.outcomes)
    states = args.state or [f"{index:03d}" for index in range(20)]
    for state in states:
        build_state(
            state=state,
            video_root=args.video_root,
            output_root=args.output_root,
            outcomes=outcomes,
        )


if __name__ == "__main__":
    main()
