# Codex 公司式并行开发组织 v0.9.0

`codex-company-swarm` 是 PKOS 的显式最高质量并行交付模式：唯一技术总监按风险路由模型、所有正式角色为侧栏可见任务、数量受限且优先复用，并保留持续 PK-01 Notion 协调、评审门禁、开发/测试配对、准确候选版本 CI、单一集成、恢复、追踪和权威知识回写。

## v0.9：需求驱动的 MFSQ v2

- M 仍为“任务与模型”，Material/来源完整性是独立的失败即停止前置门禁。
- 追踪链升级为：需求 → 唯一功能 → 前后端等实现单元及依赖 → 原子验收点 → 已评审的可视化与文字测试设计 → 逐步骤用例及测试代码 → 准确候选版本 CI。
- 每个步骤都记录对应预期结果；单元测试记录稳定测试符号、被测代码符号、目的和设计原因。
- Notion 使用相互关联的规范化视图，同时继续只保留一个权威产品功能总表。

## v0.7：可见任务、模型路由和有界并发

- TD-01 为每个 Task Packet 写入模型、思考等级、理由、风险和路由来源。高风险、产品开发、集成和严格评审默认 Sol Max；边界冻结的独立测试、CI/verifier 和机械工作优先 Luna Max。
- 正式子角色必须通过 `create_thread` 创建，仓库写者使用独立 worktree，标题含 run/role/lane，并持久保存 threadId、hostId 和 cursor。隐藏 subagent 不属于 Company Swarm 正式角色。
- 默认三条产品 lane、目标六个 active child、最低有效并发四、active hard cap 八、总注册 hard cap 十二，低并发告警阈值 90 秒。
- TD-01 在生命周期边界统一 reconcile；最多对八个可见任务做带 cursor 的有界等待；先复用相近任务，再在预算内创建，否则记录可验证的 underfill 原因。
- 优先使用项目批准的 CI；只有项目没有批准的 provider 时，才按治理默认使用 Jenkins-as-code。

BOOT→G5、PK-01/INT-01 单写者、开发/测试配对、准确候选评审、收据、追踪、恢复和验收条件保持不变。

## v0.6 基础：渐进式加载

交付能力没有删减，加载方式改为：

```text
启动元数据
  -> 精简 SKILL.md 状态机
    -> 只有下一步需要时才读取一个 reference
      -> 用脚本、Schema、示例承载确定性细节
```

入口文件现在只保留：

- 运行寄存器和硬性不变量；
- reference 条件路由表；
- `BOOT -> G0 -> G1 -> EXEC -> G2 -> G3 -> G4 -> G5`；
- 完成门禁与最终状态。

Notion Schema、事件/Outbox、字段清单、MFSQ、Jenkins、Pack Delta、恢复接管、追踪和复盘等细节继续保存在按需 reference 与脚本中，不在入口重复描述。

CI 新增上下文预算纪律：

```text
SKILL.md <= 10.5 KB
frontmatter description <= 360 字符
openai.yaml <= 560 bytes
SKILL + 技术总监角色 <= 12 KB
普通角色 TOML <= 1.25 KB
单个 reference <= 6.5 KB
禁止启动时无条件预读 reference
```

这样减少的是重复提示词，不是 Notion 协调、测试、安全、性能和审计要求。

## 运行架构

```text
Codex 实时消息 -> .pkos Outbox/Checkpoint -> PK-01 -> Notion 状态/事件/证据
                                                       ↓
                                         PKOS Feature/Current Truth/ADR/Audit/Memory
```

Notion 保存精炼语义状态和稳定证据指针，不保存完整聊天或原始日志。

## 安装或更新

```bash
codex plugin marketplace upgrade pkos-agent-skills
python plugins/pkos/skills/codex-company-swarm/scripts/install.py --agents-only --force
```

重启 Codex 后显式调用：

```text
$codex-company-swarm
```

## 验证

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/audit_prompt_budget.py
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover -s plugins/pkos/skills/codex-company-swarm/tests -v
python plugins/pkos/skills/codex-company-swarm/scripts/validate_org.py plugins/pkos/skills/codex-company-swarm/assets/examples/staffing-small-two-lane.example.json
python plugins/pkos/skills/codex-company-swarm/scripts/validate_org.py plugins/pkos/skills/codex-company-swarm/assets/examples/staffing-luna-escalation-reuse.example.json
```

从 v0.6 迁移：把 `org-v2` 升级为 `org-v3`；将当前任务登记为可见 TD-01；恢复时绑定已有任务 ID，不重复创建；新增 `staffing_budget`、`concurrency_state`、可见任务身份/cursor 和逐任务路由字段；等待依赖映射为 `queued`。先运行 validator，再更新缓存；重启或打开新 Codex 任务确认 skill 可见后，才能宣称安装生效。

`COMPANY_SWARM_ACCEPTED` 仍要求：Notion 可写且同步完成、准确候选版本 CI 通过、追踪链完整、G4 接受、PKOS 权威回写已确认，以及最终 Checkpoint、Dashboard 和复盘齐全。
