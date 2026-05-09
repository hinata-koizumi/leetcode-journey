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


def format_progress_text(stats: Stats) -> str:
    """Human-readable Japanese progress copy for README (counts only, no placeholders)."""
    e, m, h = [stats.by_difficulty[d] for d in DIFFICULTY_DIRS]
    return "\n".join(
        [
            f"これまでに記録した問題は合計 {stats.total} 問です。",
            f"内訳は Easy が {e} 問、Medium が {m} 問、Hard が {h} 問です。",
        ]
    )


def render_readme_stats_block(progress_text: str) -> str:
    """Render README statistics block as plain prose inside a text fence."""
    return "\n".join(
        [
            STATS_START_MARKER,
            "```text",
            progress_text,
            "```",
            STATS_END_MARKER,
        ]
    )


def update_readme(repo_root: Path, progress_text: str) -> bool:
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
    new_block = render_readme_stats_block(progress_text)
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
        help="Print progress text only without modifying README.md.",
    )
    return parser.parse_args()


def main() -> int:
    """Run statistics generation flow."""
    args = parse_args()
    repo_root = args.repo_root.resolve()

    stats = collect_stats(repo_root)
    progress_text = format_progress_text(stats)
    print(progress_text)

    if args.no_write_readme:
        return 0

    changed = update_readme(repo_root, progress_text)
    if changed:
        print("\nREADME statistics updated.")
    else:
        print("\nREADME statistics already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
