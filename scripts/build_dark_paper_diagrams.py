#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = REPO_ROOT / "static" / "paper_figures"
SOURCE_DIR = FIGURE_DIR / "arxiv_v1"


@dataclass(frozen=True)
class DiagramSpec:
    source: Path
    output: Path
    display_size: tuple[int, int]
    preserve_rectangles: tuple[tuple[float, float, float, float], ...]
    white_box_borders: bool = False
    emphasize_stratum_annotations: bool = False


SPECS = (
    DiagramSpec(
        source=SOURCE_DIR / "offline_diagram_v5.pdf",
        output=FIGURE_DIR / "offline_calibration_dark_arxiv_v1.svg",
        display_size=(2843, 923),
        preserve_rectangles=(
            (12.0, 42.4, 61.2, 67.2),
            (99.6, 38.8, 60.3, 70.8),
            (160.0, 44.8, 34.4, 64.8),
        ),
        white_box_borders=True,
    ),
    DiagramSpec(
        source=SOURCE_DIR / "online_diagram_v6.pdf",
        output=FIGURE_DIR / "diagram_region_construction_dark_arxiv_v1.svg",
        display_size=(3210, 968),
        preserve_rectangles=(
            (14.0, 40.8, 60.8, 70.8),
            (108.0, 39.2, 47.2, 54.0),
            (122.4, 48.0, 43.2, 57.2),
            (132.0, 58.8, 43.6, 53.6),
            (255.6, 39.2, 46.8, 54.0),
            (270.0, 48.0, 43.2, 57.2),
            (280.0, 58.8, 44.0, 53.6),
            (350.0, 41.2, 61.2, 70.4),
        ),
        emphasize_stratum_annotations=True,
    ),
)


RGB_PATTERN = re.compile(r'(fill|stroke)="rgb\(([^)]+)\)"')
BACKGROUND_PATTERN = re.compile(
    r'\s*<path fill-rule="nonzero" fill="rgb\(100%, 100%, 100%\)" '
    r'fill-opacity="1" d="M 0 0 L [^"]+ Z M 0 0 "/>',
    flags=re.DOTALL,
)


def _format_percentage(value: float) -> str:
    rounded = round(value, 6)
    if rounded.is_integer():
        return f"{int(rounded)}%"
    return f"{rounded:g}%"


def _darken_svg_colors(svg_body: str, spec: DiagramSpec) -> str:
    def replace_color(match: re.Match[str]) -> str:
        attribute = match.group(1)
        values = tuple(
            float(value.strip().rstrip("%")) for value in match.group(2).split(",")
        )
        if len(values) != 3:
            raise ValueError(f"Unexpected SVG color: {match.group(0)}")

        if max(values) - min(values) < 1e-6:
            source_gray = values[0]
            if (
                spec.emphasize_stratum_annotations
                and abs(source_gray - 72.549438) < 1e-5
            ):
                target_gray = 55.0
            else:
                target_gray = 100.0 - source_gray
            value = _format_percentage(target_gray)
            return f'{attribute}="rgb({value}, {value}, {value})"'

        return match.group(0)

    dark_body = RGB_PATTERN.sub(replace_color, svg_body)

    if spec.white_box_borders:
        source_border = 'stroke="rgb(1.568604%, 14.117432%, 19.999695%)"'
        border_count = dark_body.count(source_border)
        if border_count != 2:
            raise ValueError(f"Expected two rounded-box borders, found {border_count}")
        dark_body = dark_body.replace(source_border, 'stroke="rgb(100%, 100%, 100%)"')

    if spec.emphasize_stratum_annotations:
        separator_count = dark_body.count('stroke-opacity="0.149"')
        if separator_count != 4:
            raise ValueError(f"Expected four separator paths, found {separator_count}")
        dark_body = dark_body.replace('stroke-opacity="0.149"', 'stroke-opacity="0.3"')

    return dark_body


def _clip_path(rectangles: tuple[tuple[float, float, float, float], ...]) -> str:
    rects = "\n".join(
        f'<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}"/>'
        for x, y, width, height in rectangles
    )
    return (
        '<clipPath id="preserve-light-regions" clipPathUnits="userSpaceOnUse">\n'
        f"{rects}\n"
        "</clipPath>"
    )


def _build_svg(source_svg: str, spec: DiagramSpec) -> str:
    width, height = spec.display_size
    source_svg, root_count = re.subn(
        r'(<svg\b[^>]*\bwidth=")[^"]+("\s+height=")[^"]+("[^>]*>)',
        rf"\g<1>{width}\g<2>{height}\g<3>",
        source_svg,
        count=1,
    )
    if root_count != 1:
        raise ValueError(f"Expected one SVG root in {spec.source}")

    defs_end = source_svg.index("</defs>")
    svg_end = source_svg.rindex("</svg>")
    header = source_svg[:defs_end]
    body = source_svg[defs_end + len("</defs>") : svg_end]

    body, background_count = BACKGROUND_PATTERN.subn("", body, count=1)
    if background_count != 1:
        raise ValueError(f"Expected one page background in {spec.source}")

    dark_body = _darken_svg_colors(body, spec)
    magenta = "rgb(100%, 0%, 99.607849%)"
    if magenta not in body or magenta not in dark_body:
        raise ValueError(
            f"Magenta score/region color was not preserved in {spec.source}"
        )

    return "\n".join(
        (
            header,
            _clip_path(spec.preserve_rectangles),
            "</defs>",
            '<rect width="100%" height="100%" fill="rgb(0%, 0%, 0%)"/>',
            '<g id="dark-content">',
            dark_body.strip(),
            "</g>",
            '<g id="preserved-light-content" clip-path="url(#preserve-light-regions)">',
            '<rect width="100%" height="100%" fill="rgb(100%, 100%, 100%)"/>',
            body.strip(),
            "</g>",
            "</svg>",
            "",
        )
    )


def build_diagram(spec: DiagramSpec) -> None:
    if not spec.source.is_file():
        raise FileNotFoundError(spec.source)

    with tempfile.TemporaryDirectory(prefix="capture_dark_diagram_") as temp_dir:
        source_svg = Path(temp_dir) / "source.svg"
        subprocess.run(
            ["pdftocairo", "-svg", str(spec.source), str(source_svg)],
            check=True,
        )
        svg = _build_svg(source_svg.read_text(encoding="utf-8"), spec)

    spec.output.write_text(svg, encoding="utf-8")


def main() -> None:
    for spec in SPECS:
        build_diagram(spec)


if __name__ == "__main__":
    main()
