# Codex 公司式交付工作流 v0.10.0

`codex-company-swarm` 以“单位 Token 的可接受产品交付”为第一目标。当前主任务就是唯一规划者、调度者和累计集成者；正式子角色全部为侧栏可见的 Codex 任务，禁止隐藏 subagent 和下级委派。

## 默认组织与容量

- 1 个主任务 TD-01；最多 3 个文件、数据和契约互斥的产品开发任务。
- 1 个共享独立测试任务；Reviewer 按风险启动；PK-01 仅在门禁批量写 Notion。
- active child hard cap 为 6，registered hard cap 为 8。
- `productive` 只计算正在产生产品代码、独立测试或必要交付物的 active 子任务；等待、报告、重复上下文和环境阻塞不计入。
- 正常模式下，`product_code / productive >= 70%`，且非产品角色不得多于产品开发角色。

## Token 与收敛

Task Packet 不超过 1200 个中文字符，只能包含功能 ID、冻结需求、owned files/modules、基础 SHA、验收条件、禁止事项和必要 Notion 链接。后续只发增量；Settlement 不超过 600 个中文字符。

协调、报告和 Notion 估算超过总 Token 的 30%，或连续 120 分钟没有新累计候选/接受功能时，进入 `CONSOLIDATION_MODE`：停止新任务和新功能，只允许集成、修复、测试、部署与必要门禁回写。

每一代只有一个累计候选。开发任务完成自测后，TD-01 立即集成到同一候选，不等待所有 lane。严格评审连续退回两次也会触发收敛。

## 验证与外部边界

开发者在移交共享测试任务前必须提供准确推送 SHA、remote-12 clean checkout、定向测试、类型检查/构建；Web 变更还需要正式公网域名和真实 `cy6909` Chrome 自测。Windows 本机仅用于编辑、静态 Git 和调度，禁止运行服务、测试、Docker 或私有 origin；禁止 GitHub Actions。

CI 在启动前用最多 10 分钟检查控制器、执行节点、凭据、作业创建权限和制品空间。任一前置连续失败两次或阻塞超过 15 分钟，立即停止 CI lane、报告准确阻塞与恢复动作，并把容量释放给产品开发。

## Notion

人类可读内容使用准确、自然的中文。只在需求冻结、lane 交接、累计候选冻结、严格评审终态、部署与真实验收终态五个时点批量写回原产品功能登记簿，不创建重复摘要数据库。

## 验证与迁移

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/audit_prompt_budget.py
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover -s plugins/pkos/skills/codex-company-swarm/tests -v
python plugins/pkos/skills/codex-company-swarm/scripts/validate_org.py plugins/pkos/skills/codex-company-swarm/assets/examples/organization.example.json
python plugins/pkos/skills/codex-company-swarm/scripts/migrate_org_v3.py OLD_ORG.json --output migration.json
```

旧 org-v3 run 先 checkpoint，保留证据、收据、generation、epoch、threadId 和 settled 结果；TD-01 接管集成，最多复用三个开发任务和一个共享测试任务，归档 INT-01/多余测试者，pending work 重新签发 Task Packet v3。不得虚构旧 packet 缺失字段。
