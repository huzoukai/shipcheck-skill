#!/usr/bin/env python3
"""Append code/version/checkpoint/decision events to delivery logs."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


EVENT_TARGETS = {
    "change": "change-log.md",
    "version": "change-log.md",
    "decision": "change-log.md",
    "checkpoint": "turn-checkpoints.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append a process-monitoring event to a project-delivery folder."
    )
    parser.add_argument("--path", required=True, help="Path to the project-delivery folder.")
    parser.add_argument(
        "--type",
        required=True,
        choices=sorted(EVENT_TARGETS),
        help="Event type to record.",
    )
    parser.add_argument("--phase", default="未指定", help="Current delivery phase.")
    parser.add_argument("--summary", required=True, help="Short event summary.")
    parser.add_argument(
        "--files",
        action="append",
        default=[],
        help="Changed file/path. Can be provided multiple times.",
    )
    parser.add_argument(
        "--risk",
        action="append",
        default=[],
        help="Risk introduced or resolved. Can be provided multiple times.",
    )
    parser.add_argument("--decision", default="待补充", help="Decision made by this event.")
    parser.add_argument(
        "--go",
        choices=["GO", "NO-GO", "UNKNOWN"],
        default="UNKNOWN",
        help="Current go/no-go status after this event.",
    )
    parser.add_argument(
        "--next",
        action="append",
        default=[],
        help="Next action. Can be provided multiple times.",
    )
    parser.add_argument(
        "--round",
        type=int,
        default=None,
        help="Conversation/work round number for checkpoint events.",
    )
    parser.add_argument("--branch", default="", help="Git branch for version/change events.")
    parser.add_argument("--commit", default="", help="Git commit hash for version/change events.")
    parser.add_argument("--version", default="", help="Version, tag, or release candidate name.")
    return parser.parse_args()


def bullet_list(items: list[str], fallback: str) -> str:
    values = items or [fallback]
    return "\n".join(f"- {item}" for item in values)


def build_entry(args: argparse.Namespace) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    round_part = f" 第 {args.round} 轮" if args.round is not None else ""
    title = f"## {now} {args.type}{round_part} - {args.summary}"
    return "\n".join(
        [
            "",
            title,
            "",
            f"- 类型：{args.type}",
            f"- 阶段：{args.phase}",
            f"- 摘要：{args.summary}",
            "- 涉及文件：",
            bullet_list(args.files, "无或未记录"),
            "- 风险变化：",
            bullet_list(args.risk, "无或未记录"),
            f"- Git 分支：{args.branch or '未记录'}",
            f"- Git commit：{args.commit or '未记录'}",
            f"- 版本/标签：{args.version or '未记录'}",
            f"- 决策：{args.decision}",
            f"- go/no-go：{args.go}",
            "- 下一步动作：",
            bullet_list(args.next, "待补充"),
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        print(f"Delivery folder not found: {root}", file=sys.stderr)
        return 2

    target_name = EVENT_TARGETS[args.type]
    target = root / target_name
    if not target.exists():
        print(f"Log file not found: {target}", file=sys.stderr)
        return 2

    entry = build_entry(args)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(entry)

    print(f"Appended {args.type} event to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
