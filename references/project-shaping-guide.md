# Project Shaping Guide

Use this guide during the 00 stage before requirements analysis. Ask in small batches. For non-technical users, recommend defaults and explain tradeoffs in plain language.

## Required Question Groups

### 1. Project Identity

- 项目名称是什么？
- 项目面向谁：ToB、ToC、内部工具、SaaS、平台型、内容/电商、政府/事业单位、其他？
- 目标是验证想法、内部使用、商业交付、正式上线，还是长期运营？

### 2. Carrier and Platform

- 主要载体：Web 后台、官网、H5、小程序、App、桌面端、API 服务、多端组合？
- 是否必须同时支持 App 和小程序？
- 是否需要移动端适配、弱网、离线、推送、扫码、支付、地图、IM、音视频？

### 3. Scale and Complexity

- 项目级别：demo、MVP、标准商业项目、复杂项目、企业级/私有化。
- 预计用户量、并发、数据量、文件量、访问地域。
- 是否有多角色、多租户、审批流、报表、审计日志、权限隔离？

### 4. Data and Backend

- 核心数据对象是什么？
- 数据更像订单/客户/库存这类关系型数据，还是内容/文档/素材这类非结构化数据？
- 是否需要导入导出、统计分析、定时任务、消息通知、第三方接口？

### 5. Server and Deployment

- 部署方式：云服务器、Serverless、容器、Kubernetes、客户内网、私有化部署。
- 是否有域名、证书、备案、对象存储、CDN、备份、监控要求？
- 是否对网络、合规、数据安全、权限有特殊要求？

### 6. Language, Team, and Version Control

- 团队熟悉的语言或框架是什么？
- 前后端是否分离？
- 版本管理用 Git、SVN，还是暂时没有？
- 是否需要分支规范、提交规范、发布版本号？

### 7. UI, Motion, and Quality

- 视觉要求：简单可用、专业后台、品牌化、强动效、高端展示、游戏化？
- 动效要求：无、轻量、较高、高性能复杂动效？
- 测试要求：仅人工走查、完整 QA、自动化测试、移动端兼容、性能压测？

## Recommendation Heuristics

- ToB / internal tools: prefer clear role permissions, audit logs, relational database, admin UI, import/export, deployment and backup records.
- ToC / public products: prioritize mobile experience, analytics, privacy, CDN/static assets, monitoring, error reporting, and growth/运营 data.
- Mini program only: prefer mature mini-program frameworks or native mini-program implementation when platform APIs are deep.
- App only: prefer native when device APIs/performance are critical; prefer React Native or Flutter when cross-platform speed matters.
- App + mini program + H5: consider Taro or uni-app when one codebase matters more than custom native feel; consider separate native/app code only when quality or device APIs justify cost.
- Web admin: use a stable React/Vue stack with mature component libraries, RBAC, table/form standards, and predictable layout.
- High animation/brand display: separate marketing/showcase surfaces from operational admin surfaces; choose frameworks that support animation without hurting core workflow.
- MVP/demo: optimize for speed and clarity; SQLite or managed services may be acceptable if migration is documented.
- Standard commercial project: prefer MySQL/PostgreSQL, backend API service, Git, environment variables, backup and rollback notes.
- Enterprise/private deployment: document deployment topology, intranet constraints, data backup, logs, permissions, compliance, and maintenance handoff.

## Output After Questioning

After enough answers are collected, produce:

- project level and target audience,
- recommended carrier/platform strategy,
- recommended frontend/backend/database/deployment approach,
- repository and version-control structure,
- first delivery folder structure,
- top risks and assumptions,
- whether 00 stage can enter requirements analysis.
