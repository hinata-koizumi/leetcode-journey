#!/usr/bin/env python3
"""Generate LeetCode statistics and optionally update README.

This script scans difficulty directories and counts solution files.
It is designed to be simple to extend by editing the DIFFICULTY_DIRS mapping.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Centralized difficulty configuration for maintainability.
DIFFICULTY_DIRS: dict[str, str] = {
    "Easy": "easy",
    "Medium": "medium",
    "Hard": "hard",
}

# Bar colors for Mermaid xychart-beta: one color per `bar` series (see format_mermaid_section).
XY_CHART_BAR_COLORS = "#66d9ef,#ffd866,#ff6b6b"

# Extensions treated as solution files.
# Add/remove extensions here when your repository conventions evolve.
SOLUTION_EXTENSIONS: set[str] = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".cs",
    ".go",
    ".rs",
    ".kt",
    ".swift",
    ".rb",
    ".php",
    ".scala",
    ".sql",
    ".sh",
}

STATS_START_MARKER = "<!-- STATS:START -->"
STATS_END_MARKER = "<!-- STATS:END -->"


@dataclass(frozen=True)
class Stats:
    """Container for problem counts."""

    by_difficulty: dict[str, int]

    @property
    def total(self) -> int:
        """Return total solved problem count across all difficulties."""
        return sum(self.by_difficulty.values())


def is_solution_file(file_path: Path) -> bool:
    """Return True when file should be counted as a solution."""
    return file_path.is_file() and file_path.suffix.lower() in SOLUTION_EXTENSIONS


def iter_solution_files(directory: Path) -> Iterable[Path]:
    """Yield all files in a directory tree that match known solution extensions."""
    if not directory.exists():
        return
    for file_path in directory.rglob("*"):
        if is_solution_file(file_path):
            yield file_path


def collect_stats(repo_root: Path) -> Stats:
    """Collect solution counts by difficulty from repository directories."""
    counts: dict[str, int] = {}
    for label, relative_path in DIFFICULTY_DIRS.items():
        target_dir = repo_root / relative_path
        counts[label] = sum(1 for _ in iter_solution_files(target_dir))
    return Stats(by_difficulty=counts)


def format_total_summary(stats: Stats) -> str:
    """Single line: total number of recorded solutions (matches scanned files)."""
    return f"合計 {stats.total} 問"


def _counts_and_y_max(stats: Stats) -> tuple[tuple[int, int, int], int]:
    """Return (Easy, Medium, Hard) counts and y-axis upper bound.

    Single `bar [a,b,c]` is one series and often renders all bars the same color on
    GitHub. We instead emit three series so each difficulty gets its own palette color.
    """
    if stats.total > 0:
        e, m, h = [stats.by_difficulty[d] for d in DIFFICULTY_DIRS]
        max_c = max(e, m, h)
        y_max = max(5, max_c + max(2, (max_c // 10) + 1))
        return (e, m, h), y_max
    # Sample preview when there are no solutions yet.
    return (3, 2, 1), 5


def format_mermaid_section(stats: Stats) -> str:
    """Create Mermaid markdown: bar chart (xychart-beta) for progress.

    Uses real counts when total > 0; otherwise a short sample chart for layout preview.
    """
    chart_init = (
        '%%{init: {"theme":"base","themeVariables":'
        '{"xyChart":{"plotColorPalette":"'
        + XY_CHART_BAR_COLORS
        + '"}}}%%'
    )
    (easy, medium, hard), y_max = _counts_and_y_max(stats)
    labels = ", ".join(DIFFICULTY_DIRS.keys())

    lines = [
        "```mermaid",
        chart_init,
        "xychart-beta",
        '    title "Problems by difficulty"',
        f"    x-axis [{labels}]",
        f'    y-axis "Count" 0 --> {y_max}',
        # Three series so plotColorPalette applies Easy / Medium / Hard separately.
        f"    bar [{easy}, 0, 0]",
        f"    bar [0, {medium}, 0]",
        f"    bar [0, 0, {hard}]",
        "```",
    ]
    return "\n".join(lines)


def render_readme_stats_block(total_summary: str, mermaid_section: str) -> str:
    """Render README statistics block with narrative text and Mermaid chart."""
    return "\n".join(
        [
            STATS_START_MARKER,
            "```text",
            total_summary,
            "```",
            "",
            mermaid_section,
            STATS_END_MARKER,
        ]
    )


def update_readme(repo_root: Path, total_summary: str) -> bool:
    """Replace README statistics block and return True when file changed."""
    readme_path = repo_root / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    start_index = readme_text.find(STATS_START_MARKER)
    end_index = readme_text.find(STATS_END_MARKER)
    if start_index == -1 or end_index == -1:
        raise ValueError("README.md is missing STATS markers.")
    if end_index < start_index:
        raise ValueError("README.md statistics markers are in invalid order.")

    end_index += len(STATS_END_MARKER)
    mermaid_section = format_mermaid_section(collect_stats(repo_root))
    new_block = render_readme_stats_block(total_summary, mermaid_section)
    updated_text = readme_text[:start_index] + new_block + readme_text[end_index:]

    if updated_text == readme_text:
        return False

    readme_path.write_text(updated_text, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate LeetCode statistics and update README."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Path to repository root (defaults to current script's repo).",
    )
    parser.add_argument(
        "--no-write-readme",
        action="store_true",
        help="Print total line only without modifying README.md.",
    )
    return parser.parse_args()


def main() -> int:
    """Run statistics generation flow."""
    args = parse_args()
    repo_root = args.repo_root.resolve()

    stats = collect_stats(repo_root)
    total_summary = format_total_summary(stats)
    mermaid_section = format_mermaid_section(stats)
    print(total_summary)

    if args.no_write_readme:
        print("\nMermaid diagram preview:\n")
        print(mermaid_section)
        return 0

    changed = update_readme(repo_root, total_summary)
    if changed:
        print("\nREADME statistics updated.")
    else:
        print("\nREADME statistics already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
