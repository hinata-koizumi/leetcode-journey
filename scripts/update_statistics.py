#!/usr/bin/env python3
"""Generate LeetCode statistics and optionally update README.

This script scans difficulty directories and counts solution files.
It is designed to be simple to extend by editing the DIFFICULTY_DIRS mapping.
"""

from __future__ import annotations

import argparse
import re
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


def format_progress_markdown(stats: Stats) -> str:
    """GFM table for README: scannable counts without charts."""
    e, m, h = [stats.by_difficulty[d] for d in DIFFICULTY_DIRS]
    total = stats.total
    return "\n".join(
        [
            "| 難易度 | 件数 |",
            "|:------|----:|",
            f"| Easy | {e} |",
            f"| Medium | {m} |",
            f"| Hard | {h} |",
            f"| **合計** | **{total}** |",
        ]
    )


def render_readme_stats_block(progress_markdown: str) -> str:
    """Insert GitHub-rendered Markdown between markers (no code fence so tables work)."""
    return "\n".join(
        [
            STATS_START_MARKER,
            "",
            progress_markdown,
            "",
            STATS_END_MARKER,
        ]
    )


def _read_readme(path: Path) -> str:
    """Read README; utf-8-sig strips BOM so <!-- STATS --> markers are found on CI."""
    return path.read_bytes().decode("utf-8-sig")


def _replace_stats_section(readme_text: str, new_block: str) -> str | None:
    """Apply STATS markers replacement, or replace ## Progress body until next ##."""
    start_index = readme_text.find(STATS_START_MARKER)
    end_index = readme_text.find(STATS_END_MARKER)
    if start_index != -1 and end_index != -1 and end_index > start_index:
        end_index += len(STATS_END_MARKER)
        return readme_text[:start_index] + new_block + readme_text[end_index:]

    match = re.search(
        r"(^## Progress\s*\n)([\s\S]*?)(?=^## |\Z)",
        readme_text,
        flags=re.MULTILINE,
    )
    if match:
        return (
            readme_text[: match.start()]
            + match.group(1)
            + new_block
            + "\n\n"
            + readme_text[match.end() :]
        )
    return None


def update_readme(repo_root: Path, progress_markdown: str) -> bool:
    """Replace README statistics block and return True when file changed."""
    readme_path = repo_root / "README.md"
    readme_text = _read_readme(readme_path)
    new_block = render_readme_stats_block(progress_markdown)

    updated_text = _replace_stats_section(readme_text, new_block)
    if updated_text is None:
        raise ValueError(
            "README.md must contain <!-- STATS:START --> ... <!-- STATS:END --> "
            "or a ## Progress section to inject statistics under."
        )

    if updated_text == readme_text:
        return False

    readme_path.write_text(updated_text, encoding="utf-8", newline="\n")
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
        help="Print progress Markdown only without modifying README.md.",
    )
    return parser.parse_args()


def main() -> int:
    """Run statistics generation flow."""
    args = parse_args()
    repo_root = args.repo_root.resolve()

    stats = collect_stats(repo_root)
    progress_markdown = format_progress_markdown(stats)
    print(progress_markdown)

    if args.no_write_readme:
        return 0

    changed = update_readme(repo_root, progress_markdown)
    if changed:
        print("\nREADME statistics updated.")
    else:
        print("\nREADME statistics already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
