#!/usr/bin/env python3
"""Initialize a project-delivery Markdown handoff folder."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "assets" / "project-delivery-template"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a project-delivery folder from the bundled Markdown template."
    )
    parser.add_argument("--name", required=True, help="Project name to place in templates.")
    parser.add_argument(
        "--output",
        required=True,
        help="Parent project directory, or the project-delivery directory itself.",
    )
    return parser.parse_args()


def resolve_target(output: str) -> Path:
    output_path = Path(output).expanduser().resolve()
    if output_path.name == "project-delivery":
        return output_path
    return output_path / "project-delivery"


def replace_placeholders(target: Path, project_name: str) -> None:
    now = datetime.now()
    values = {
        "{{PROJECT_NAME}}": project_name,
        "{{DATE}}": now.strftime("%Y-%m-%d"),
        "{{DATETIME}}": now.strftime("%Y-%m-%d %H:%M:%S"),
    }
    for md_file in target.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for key, value in values.items():
            content = content.replace(key, value)
        md_file.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    target = resolve_target(args.output)

    if not TEMPLATE_DIR.exists():
        print(f"Template directory not found: {TEMPLATE_DIR}", file=sys.stderr)
        return 2

    if target.exists():
        print(
            f"Refusing to overwrite existing delivery folder: {target}",
            file=sys.stderr,
        )
        print("Move it aside or choose another --output path.", file=sys.stderr)
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_DIR, target)
    replace_placeholders(target, args.name)

    print(f"Created delivery folder: {target}")
    print("Next step: fill 00_项目启动问答.md and 00_技术方案推荐.md, then run check_delivery_stage.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
