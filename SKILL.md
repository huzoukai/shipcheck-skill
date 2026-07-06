---
name: shipcheck
description: Check and record AI-assisted project delivery. Use when Codex or Trae needs to guide a non-technical or semi-technical user from product idea to delivery, run kickoff questions, recommend a simple architecture, initialize a local project-delivery folder, record Git/code/version changes, enforce strict stage gates, run testing and acceptance checks, or decide whether a Vibe Coding project is ready for the next phase.
---

# Shipcheck

Shipcheck is a project delivery check system for Vibe Coding work. It is not a code generator. It helps Trae, Codex, and the human operator turn a client idea into a trackable delivery folder with clear stages, phase summaries, testing records, Git/version notes, and strict go/no-go gates.

Public-facing Chinese name: `交付体检`.

Core behavior:

- Record after every meaningful action.
- Audit before every phase transition.
- Remind the user when required actions are still incomplete.
- Treat `project-delivery/` as the source of truth.

## Operating Modes

### 0. Choose Runtime

Use the same delivery rules in both runtimes:

- **Codex**: run the bundled scripts directly and update files in `project-delivery/`.
- **Trae**: copy the rules from `agents/trae.md` into the project rule/prompt area, then let Trae maintain the same `project-delivery/` folder.

When both tools are used on the same project, the folder is the source of truth. Do not rely on chat memory as the delivery record.

### 1. Shape the Project

Before requirements analysis, run a structured kickoff questionnaire. Ask enough questions to fill:

- `00_项目启动问答.md`
- `00_技术方案推荐.md`

Use `references/project-shaping-guide.md` for the question set and recommendation heuristics. Ask in small batches, especially for non-technical users. Do not jump straight into implementation. First identify:

- project type: ToB, ToC, internal tool, SaaS, content/ecommerce, platform, etc.
- carrier: web admin, website, H5, mini program, native app, cross-platform app, API service, multi-end.
- scale: demo, MVP, standard commercial project, complex project, enterprise/private deployment.
- network/server needs: public cloud, private deployment, serverless, container, high concurrency, offline/weak-network, CDN.
- data needs: relational data, documents, files, audit logs, privacy, permissions, reporting.
- frontend/backend split, database direction, version control, language preference, design/animation needs.

The 00 stage is a gate: project shaping must be confirmed before entering `01_需求分析.md`.

### 2. Initialize

Create a local Markdown handoff folder:

```bash
python3 /Users/huzoukai/.codex/skills/shipcheck/scripts/init_delivery_project.py --name "项目名" --output /path/to/project
```

This creates `/path/to/project/project-delivery/` unless `--output` already ends with `project-delivery`. Never overwrite an existing delivery folder unless the user explicitly asks for replacement.

### 3. Record Execution Events

Whenever code changes, a version is submitted, a major decision is made, or a 10/20-turn checkpoint is reached, append a process record:

```bash
python3 /Users/huzoukai/.codex/skills/shipcheck/scripts/record_delivery_event.py --path /path/to/project-delivery --type change --phase "03_前端检查" --summary "完成登录页状态修复" --files "src/login.tsx" --decision "继续联调前修复接口错误态" --go NO-GO --next "补齐错误提示截图"
```

Use:

- `--type progress` for normal project progress, task completion, user feedback, phase work, or non-code delivery movement.
- `--type change` for code/file changes.
- `--type version` for commits, releases, deploys, or milestone submissions.
- `--type checkpoint` for every 10 or 20 rounds of conversation/work.
- `--type decision` for architecture, scope, or delivery decisions.

Record after every meaningful action, including small actions. Examples:

- a page or component was adjusted,
- an API was created or changed,
- a database field/table was changed,
- a test pass was run,
- a client gave feedback,
- a bug was fixed,
- a Git commit/version/deploy happened,
- a phase document was updated.

If the action does not fit code/version/decision/checkpoint, use `--type progress`.

If Git is available, include branch/commit/version fields:

```bash
python3 /Users/huzoukai/.codex/skills/shipcheck/scripts/record_delivery_event.py --path /path/to/project-delivery --type version --phase "09_上线准备" --summary "提交候选版本" --branch "main" --commit "abc1234" --version "v0.1.0" --go GO --next "客户验收后打正式 tag"
```

### 4. Audit

Inspect existing delivery records before making any judgment:

```bash
python3 /Users/huzoukai/.codex/skills/shipcheck/scripts/check_delivery_stage.py --path /path/to/project-delivery
```

Base the answer on the files in `project-delivery/`, not memory or assumptions. If files are missing, treat that as a delivery gap.

Always audit before moving to a new phase. When the user says "下一步", "继续", "进入下一阶段", "可以了", or similar, do not silently advance. First run the audit. If the audit returns NO-GO, stop and tell the user which required actions are incomplete.

### 5. Update a Phase

When the user provides new progress, update the matching phase document and append a new entry to `progress-log.md`. Do not rewrite or summarize away previous log entries. Preserve history.

Every delivery phase document must keep these sections:

- `本阶段输入`
- `本阶段做了什么`
- `反复修改了什么`
- `阶段产出物`
- `阶段风险`
- `下一阶段需要什么`
- `是否允许进入下一阶段`

## Strict Gate Rules

Use strict gates by default:

- 项目画像和技术方案未确认，不进入需求分析。
- 需求不清，不进入项目拆解。
- 项目拆解不清，不进入前后端实现。
- 前端、后端、数据库未检查，不进入联调。
- 联调未通过，不进入测试。
- 测试未通过，不进入客户验收。
- 客户验收未通过，不进入上线。
- 上线没有记录，不进入复盘。
- 复盘没有沉淀，不算交付完成。

Phase-transition reminder rules:

- Before changing the current phase, run `check_delivery_stage.py`.
- If the result is NO-GO, explicitly say the phase cannot move forward yet.
- Name the missing files, missing sections, missing tests, missing Git/version records, or missing GO decision.
- Give the user the next 3 concrete actions needed to unlock the phase.
- Do not continue implementation under the next phase label until the missing actions are recorded or the user explicitly overrides the gate.

Git/version rules:

- A delivery milestone should have a matching Git commit or version note.
- Do not claim a version is submitted unless `change-log.md` contains the branch, commit, tag, release, or deploy evidence.
- Ask before committing or tagging. Recording a suggested version is allowed; changing Git history is not.
- If Git is unavailable, record `Git 未接入` as a delivery risk.

Testing is always a standalone phase. Do not merge testing into integration or acceptance. `07_测试记录.md` must separately cover:

- 功能测试
- 边界测试
- 权限测试
- 移动端测试
- 异常测试
- 回归测试

## Required Output

After every audit, update, or checkpoint, answer in this structure:

```markdown
## 当前阶段判断
当前处于：[阶段编号和名称]
结论：[go/no-go，一句话说明]

## 完成度
[当前阶段]完成度：[百分比]

## 过程监控
- 代码/版本记录：[数量和最近一次摘要]
- 轮次检查：[数量和最近一次摘要]
- 监控缺口：[缺口或无]

## 风险和缺口
- [风险或缺口 1]
- [风险或缺口 2]
- [风险或缺口 3]

## 下一步 3 个动作
1. [动作 1]
2. [动作 2]
3. [动作 3]

## 阶段总结
[用 2-4 句话总结当前阶段真实状态]

## progress-log 更新
[给出应该追加到 progress-log.md 的日志块；如果已经写入，说明已追加]

## Go / No-Go
[GO 或 NO-GO]
原因：[严格闸门原因]
```

Keep the output practical. Name missing files, missing sections, blocked gates, monitoring gaps, and the concrete evidence needed to unlock the next stage.

## Project Folder Contract

The delivery folder must contain:

```text
project-delivery/
├── 00_项目总览.md
├── 00_项目启动问答.md
├── 00_技术方案推荐.md
├── 01_需求分析.md
├── 02_项目拆解.md
├── 03_前端检查.md
├── 04_后端检查.md
├── 05_数据库检查.md
├── 06_联调.md
├── 07_测试记录.md
├── 08_客户验收.md
├── 09_上线准备.md
├── 10_复盘沉淀.md
├── change-log.md
├── turn-checkpoints.md
└── progress-log.md
```

Use `assets/project-delivery-template/` as the canonical template source.

## Logging Rules

`progress-log.md` is append-only and records phase-level progress.

`change-log.md` is append-only and records code changes, file changes, commits, version submissions, deploys, and release candidates.

`turn-checkpoints.md` is append-only and records every 10- or 20-turn checkpoint. At each checkpoint:

1. run an audit,
2. summarize context drift and unresolved decisions,
3. confirm current stage,
4. name the next 3 actions,
5. record go/no-go.

If the user asks for a handoff-ready status, include the latest stage summary plus the latest process-monitoring entries so another person can continue immediately.

After completing any requested task under this skill, check whether a log entry should be appended. If the user did not ask to skip logging, write or provide the log entry before finishing the response.
