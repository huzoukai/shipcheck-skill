#!/usr/bin/env python3
"""Audit a project-delivery Markdown folder and enforce strict phase gates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


REQUIRED_SECTIONS = (
    "本阶段输入",
    "本阶段做了什么",
    "反复修改了什么",
    "阶段产出物",
    "阶段风险",
    "下一阶段需要什么",
    "是否允许进入下一阶段",
)

INITIALIZATION_SECTIONS = (
    "项目基本选择",
    "体量和复杂度",
    "载体和平台",
    "网络和服务器要求",
    "数据和权限要求",
    "语言和技术偏好",
    "协作和版本管理",
    "UI、动效和质量要求",
    "推荐结论确认",
    "是否允许进入需求分析",
)

TECH_RECOMMENDATION_SECTIONS = (
    "项目级别判断",
    "载体和端形态",
    "推荐总体架构",
    "推荐前端方案",
    "推荐后端方案",
    "推荐数据库和数据结构",
    "推荐服务器和部署",
    "推荐代码和文档结构",
    "推荐版本管理",
    "关键风险和假设",
    "进入需求分析前确认",
)

TEST_CATEGORIES = (
    "功能测试",
    "边界测试",
    "权限测试",
    "移动端测试",
    "异常测试",
    "回归测试",
)

PLACEHOLDER_PATTERNS = [
    "待填写",
    "TODO",
    "TBD",
    "待补充",
    "未填写",
]


@dataclass(frozen=True)
class Phase:
    code: str
    name: str
    file_name: str
    gate_reason: str
    required_sections: tuple[str, ...] = REQUIRED_SECTIONS
    decision_heading: str = "是否允许进入下一阶段"


PHASES = [
    Phase(
        "00",
        "项目初始化",
        "00_项目启动问答.md",
        "项目画像和技术方案未确认，不进入需求分析。",
        INITIALIZATION_SECTIONS,
        "是否允许进入需求分析",
    ),
    Phase("01", "需求分析", "01_需求分析.md", "需求不清，不进入项目拆解。"),
    Phase("02", "项目拆解", "02_项目拆解.md", "项目拆解不清，不进入前后端实现。"),
    Phase("03", "前端检查", "03_前端检查.md", "前端未检查，不进入联调。"),
    Phase("04", "后端检查", "04_后端检查.md", "后端未检查，不进入联调。"),
    Phase("05", "数据库检查", "05_数据库检查.md", "数据库未检查，不进入联调。"),
    Phase("06", "联调", "06_联调.md", "联调未通过，不进入测试。"),
    Phase("07", "测试记录", "07_测试记录.md", "测试未通过，不进入客户验收。"),
    Phase("08", "客户验收", "08_客户验收.md", "客户验收未通过，不进入上线。"),
    Phase("09", "上线准备", "09_上线准备.md", "上线没有记录，不进入复盘。"),
    Phase("10", "复盘沉淀", "10_复盘沉淀.md", "复盘没有沉淀，不算交付完成。"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read project-delivery Markdown records and output a go/no-go audit."
    )
    parser.add_argument("--path", required=True, help="Path to the project-delivery folder.")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def section_text(markdown: str, heading: str, level: int = 2) -> str:
    hashes = "#" * level
    pattern = re.compile(
        rf"^{re.escape(hashes)}\s+{re.escape(heading)}\s*$"
        rf"(?P<body>.*?)(?=^#{{1,{level}}}\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    return match.group("body").strip() if match else ""


def remove_placeholder_lines(text: str) -> str:
    useful_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(token.lower() in stripped.lower() for token in PLACEHOLDER_PATTERNS):
            continue
        if stripped in {"-", "*"}:
            continue
        useful_lines.append(stripped)
    return "\n".join(useful_lines).strip()


def is_filled(text: str) -> bool:
    return bool(remove_placeholder_lines(text))


def parse_decision(text: str) -> str:
    normalized = remove_placeholder_lines(text).lower()
    if not normalized:
        return "missing"
    no_go_tokens = ["no-go", "nogo", "不允许", "未通过", "暂不", "不能进入", "否"]
    go_tokens = ["go", "允许", "通过", "可以进入", "是"]
    if any(token in normalized for token in no_go_tokens):
        return "no-go"
    if any(token in normalized for token in go_tokens):
        return "go"
    return "unclear"


def phase_audit(root: Path, phase: Phase) -> dict:
    file_path = root / phase.file_name
    markdown = read_text(file_path)
    missing: list[str] = []
    filled_count = 0

    if not markdown:
        return {
            "code": phase.code,
            "name": phase.name,
            "file": phase.file_name,
            "exists": False,
            "completion": 0,
            "decision": "missing",
            "missing": ["文件不存在"],
            "risks": [],
            "gate_reason": phase.gate_reason,
            "decision_heading": phase.decision_heading,
        }

    for heading in phase.required_sections:
        body = section_text(markdown, heading)
        if is_filled(body):
            filled_count += 1
        else:
            missing.append(heading)

    extra_denominator = 0
    if phase.code == "00":
        tech_markdown = read_text(root / "00_技术方案推荐.md")
        extra_denominator += len(TECH_RECOMMENDATION_SECTIONS)
        if not tech_markdown:
            missing.append("00_技术方案推荐.md：文件不存在")
        else:
            for heading in TECH_RECOMMENDATION_SECTIONS:
                body = section_text(tech_markdown, heading)
                if is_filled(body):
                    filled_count += 1
                else:
                    missing.append(f"00_技术方案推荐.md：{heading}")

    decision = parse_decision(section_text(markdown, phase.decision_heading))
    if decision == "go":
        filled_count += 1
    else:
        if decision == "missing":
            missing.append("go/no-go 判断缺失")
        elif decision == "unclear":
            missing.append("go/no-go 判断不明确")
        elif decision == "no-go":
            missing.append("当前阶段明确为 NO-GO")

    if phase.code == "07":
        for category in TEST_CATEGORIES:
            category_body = section_text(markdown, category, level=3)
            if is_filled(category_body):
                filled_count += 1
            else:
                missing.append(f"测试覆盖缺失：{category}")
        denominator = len(phase.required_sections) + 1 + len(TEST_CATEGORIES) + extra_denominator
    else:
        denominator = len(phase.required_sections) + 1 + extra_denominator

    risks = extract_bullets(section_text(markdown, "阶段风险"))
    completion = round((filled_count / denominator) * 100)

    return {
        "code": phase.code,
        "name": phase.name,
        "file": phase.file_name,
        "exists": True,
        "completion": completion,
        "decision": decision,
        "missing": unique(missing),
        "risks": risks,
        "gate_reason": phase.gate_reason,
        "decision_heading": phase.decision_heading,
    }


def extract_bullets(text: str) -> list[str]:
    clean = remove_placeholder_lines(text)
    if not clean:
        return []
    bullets = []
    for line in clean.splitlines():
        stripped = line.strip().lstrip("-*0123456789.、 ").strip()
        if stripped:
            bullets.append(stripped)
    return unique(bullets)


def unique(items: Iterable[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def determine_current(audits: list[dict]) -> tuple[dict, str]:
    for audit in audits:
        if audit["decision"] != "go" or audit["missing"]:
            return audit, "no-go"
    return audits[-1], "go"


def build_next_actions(current: dict) -> list[str]:
    actions = []
    for missing in current["missing"]:
        if missing == "当前阶段明确为 NO-GO":
            actions.append(f"处理 `{current['file']}` 中导致 NO-GO 的原因，并记录修复证据。")
        elif missing.startswith("00_技术方案推荐.md："):
            heading = missing.split("：", 1)[1]
            actions.append(f"补齐 `00_技术方案推荐.md` 的 `{heading}`。")
        elif missing == "文件不存在":
            actions.append(f"补建 `{current['file']}` 并按模板填写阶段记录。")
        else:
            actions.append(f"补齐 `{current['file']}` 的 `{missing}`。")

    if current["code"] == "07":
        actions.append("确认测试阶段独立完成，不把联调记录或客户验收当作测试记录。")

    actions.append(f"重新判断 `{current['file']}` 的 `{current['decision_heading']}`，并写明 GO/NO-GO 原因。")
    return (actions + ["追加 `progress-log.md`，保留本次风险、决策和下一步动作。"])[:3]


def build_risks_and_gaps(current: dict) -> list[str]:
    gaps = []
    gaps.extend(current["missing"])
    gaps.extend(current["risks"])
    if not gaps:
        gaps.append("未发现当前阶段缺口，但仍需确认下一阶段输入是否齐备。")
    return unique(gaps)[:8]


def log_entries(markdown: str) -> list[str]:
    if not markdown:
        return []
    entries = []
    ignored = {"使用方式", "检查规则"}
    for match in re.finditer(r"^##\s+(.+?)\s*$", markdown, re.MULTILINE):
        title = match.group(1).strip()
        if title not in ignored:
            entries.append(title)
    return entries


def build_monitoring_audit(root: Path, current: dict) -> dict:
    change_path = root / "change-log.md"
    checkpoint_path = root / "turn-checkpoints.md"
    change_entries = log_entries(read_text(change_path))
    checkpoint_entries = log_entries(read_text(checkpoint_path))
    gaps = []

    if not change_path.exists():
        gaps.append("缺少 `change-log.md`，无法持续记录代码更改和版本提交。")
    if not checkpoint_path.exists():
        gaps.append("缺少 `turn-checkpoints.md`，无法做 10/20 轮过程检查。")

    try:
        current_code = int(current["code"])
    except ValueError:
        current_code = 0

    if current_code >= 3 and not change_entries:
        gaps.append("已进入实现/检查阶段，但 `change-log.md` 尚无代码或版本记录。")
    if not checkpoint_entries:
        gaps.append("尚无 10/20 轮 checkpoint 记录；如果当前未满 10 轮可忽略。")

    return {
        "change_log_exists": change_path.exists(),
        "checkpoint_log_exists": checkpoint_path.exists(),
        "change_count": len(change_entries),
        "checkpoint_count": len(checkpoint_entries),
        "latest_change": change_entries[-1] if change_entries else "无",
        "latest_checkpoint": checkpoint_entries[-1] if checkpoint_entries else "无",
        "gaps": gaps,
    }


def build_summary(root: Path) -> dict:
    audits = [phase_audit(root, phase) for phase in PHASES]
    current, overall_decision = determine_current(audits)
    is_complete = overall_decision == "go" and current["code"] == "10"
    if is_complete:
        actions = [
            "归档项目交付记录，确认 `project-delivery/` 可直接交接给后续负责人。",
            "把复盘沉淀中的模板、检查清单或踩坑记录同步到团队知识库。",
            "记录后续维护、客户回访或二期需求入口。",
        ]
    else:
        actions = build_next_actions(current)
    risks_and_gaps = build_risks_and_gaps(current)
    monitoring = build_monitoring_audit(root, current)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    decision_reason = "10_复盘沉淀已通过，交付闭环完成。" if is_complete else current["gate_reason"]
    log_block = [
        f"## {now} 交付体检",
        "",
        f"- 阶段：{current['code']}_{current['name']}",
        f"- 本次更新摘要：当前阶段完成度 {current['completion']}%，结论 {overall_decision.upper()}。",
        "- 修改/返工点：待根据本次修复补充。",
        f"- 新增风险：{'；'.join(risks_and_gaps[:3])}",
        f"- 过程监控：change-log {monitoring['change_count']} 条，checkpoint {monitoring['checkpoint_count']} 条。",
        f"- 决策：{decision_reason}",
        f"- go/no-go：{overall_decision.upper()}",
        "- 下一步动作:",
    ]
    log_block.extend([f"  {index}. {action}" for index, action in enumerate(actions, start=1)])

    return {
        "path": str(root),
        "current_phase": current,
        "overall_decision": overall_decision,
        "risks_and_gaps": risks_and_gaps,
        "next_actions": actions,
        "phase_audits": audits,
        "progress_log_update": "\n".join(log_block),
        "is_complete": is_complete,
        "decision_reason": decision_reason,
        "monitoring": monitoring,
    }


def render_markdown(summary: dict) -> str:
    current = summary["current_phase"]
    decision = summary["overall_decision"]
    if summary["is_complete"]:
        decision_text = "交付闭环已完成。"
    else:
        decision_text = "可以进入下一阶段。" if decision == "go" else "暂不允许进入下一阶段。"
    risks = "\n".join(f"- {item}" for item in summary["risks_and_gaps"])
    monitoring = summary["monitoring"]
    monitoring_gaps = monitoring["gaps"] or ["无"]
    monitoring_gap_text = "\n".join(f"- {item}" for item in monitoring_gaps)
    actions = "\n".join(
        f"{index}. {action}" for index, action in enumerate(summary["next_actions"], start=1)
    )

    return f"""## 当前阶段判断
当前处于：{current['code']}_{current['name']}
结论：{decision}，{decision_text}

## 完成度
{current['name']}完成度：{current['completion']}%

## 过程监控
- 代码/版本记录：{monitoring['change_count']} 条；最近一次：{monitoring['latest_change']}
- 轮次检查：{monitoring['checkpoint_count']} 条；最近一次：{monitoring['latest_checkpoint']}
- 监控缺口：
{monitoring_gap_text}

## 风险和缺口
{risks}

## 下一步 3 个动作
{actions}

## 阶段总结
当前检查基于 `{current['file']}` 和交付文件夹内的阶段记录。严格闸门结论为 {decision.upper()}。{summary['decision_reason']}

## progress-log 更新
```markdown
{summary['progress_log_update']}
```

## Go / No-Go
{decision.upper()}
原因：{summary['decision_reason']}
"""


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        print(f"Delivery folder not found: {root}", file=sys.stderr)
        return 2

    summary = build_summary(root)
    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
