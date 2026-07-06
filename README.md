# Shipcheck

Shipcheck（交付体检）是一套给 Vibe Coding 项目用的交付流程 Skill。

它适合非程序员、产品经理、AI 工具使用者在 Trae 或 Codex 里做真实项目时使用：从需求分析、项目拆解、前端、后端、数据库、联调、测试、验收到上线复盘，每个阶段都留下可交接的 Markdown 记录。

## 安装到 Codex

```bash
bash install.sh
```

安装后在 Codex 里使用：

```text
使用 $shipcheck 帮我初始化一个项目交付流程
```

## 在 Trae 使用

Trae 不一定直接读取 Codex Skill 格式。推荐做法：

1. 打开 `agents/trae.md`
2. 复制里面的规则到 Trae 项目规则、自定义指令或项目说明里
3. 让 Trae 在项目根目录维护 `project-delivery/`

## 初始化项目

```bash
python3 scripts/init_delivery_project.py --name "婚庆案例小程序" --output /path/to/project
```

## 检查阶段

```bash
python3 scripts/check_delivery_stage.py --path /path/to/project/project-delivery
```

## 记录版本或改动

```bash
python3 scripts/record_delivery_event.py \
  --path /path/to/project/project-delivery \
  --type version \
  --phase "09_上线准备" \
  --summary "提交候选版本" \
  --branch "main" \
  --commit "abc1234" \
  --version "v0.1.0" \
  --go GO
```

## 核心阶段

1. 项目初始化
2. 需求分析
3. 项目拆解
4. 前端检查
5. 后端检查
6. 数据库检查
7. 联调
8. 测试记录
9. 客户验收
10. 上线准备
11. 复盘沉淀

