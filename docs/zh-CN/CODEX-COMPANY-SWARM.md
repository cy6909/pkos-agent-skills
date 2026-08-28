# Codex 公司式并行开发组织 v0.5

`codex-company-swarm` 是 PKOS 的最高质量、高并发、无需优先考虑 Token 成本的完整交付模式。一个 Codex 根会话作为逻辑技术总监，统一管理持续运行的 Notion 协调记录员、评审委员会、各领域开发/测试配对、CI/CD、安全与性能、单一集成负责人、端到端追踪、检查点恢复和 PKOS 权威知识回写。

## v0.5 的核心变化

Notion 不再只是“启动时读取、结束时写回”，而是成为关键状态和恢复信息的持久协调控制面：

```text
Codex 实时消息
    ↓ 结构化事件
.pkos Outbox / Checkpoint
    ↓ PK-01 单写者核验
Notion 当前状态投影 / 事件账本 / 证据索引
    ↓ 最终权威回写
PKOS Feature / Current Truth / ADR / Audit / Memory
```

Notion **不会**保存完整聊天、原始控制台日志和每次微小代码修改。

### PK-01 持续协调

`PK-01` 在评审主席之前拉起，并持续工作到 G5，统一负责：

- Run、Lane、Session、Task、Pack、Checkpoint 当前状态；
- 只追加的语义事件与决策历史；
- Git、CI、测试、安全、性能等证据指针和校验值；
- Feature 关键生命周期状态投影；
- Context Request 和代理快照；
- Pack Delta 与强制确认；
- Outbox、写入回执、连续同步水位、失败重试和死信；
- 技术总监接管与恢复记录；
- 最终经过批准的 PKOS Current Truth、Feature、Audit、ADR、Incident、Memory 回写与复盘。

其他会话可以只读核验 Notion，但不能并发创建或修改协调记录。

### 最小 Notion 结构

继续复用现有唯一 Project Feature Registry，只增加三个数据库：

1. Swarm Run & Lane Registry；
2. Event & Decision Ledger；
3. Evidence Registry。

创建前必须搜索稳定 ID、别名和 Control Plane 指针，禁止重复创建第二套 Feature List 或“最新状态页”。

### 信息不缺漏但保持精炼

- 当前状态只保留投影；
- 历史变化放事件账本；
- 大日志留在 Git/CI/Artifact Store；
- Notion 只保存证据摘要、URI、Checksum、Producer/Verifier；
- 缺失上下文通过 Context Request 补充；
- 共享规范变化通过 Pack Delta 广播；
- Requirement → Feature → Acceptance → Commit → Test → CI → Review → Notion Receipt 由脚本强制验证。

### 恢复与接管

每个关键 Gate、交接、候选冻结和评审结果都会生成带校验值的 Checkpoint。根会话异常退出后，新会话必须读取最后检查点、核验 Event Ledger 和同步水位，并在用户授权下写入 `TAKEOVER` 事件、将 Director Epoch 加一，再重新下发受影响任务包。旧 Epoch 的结果会保留为证据，但不能修改当前状态。

## 安装或更新

```bash
codex plugin marketplace upgrade pkos-agent-skills
python plugins/pkos/skills/codex-company-swarm/scripts/install.py --agents-only --force
```

重启 Codex 或打开新任务，然后显式调用：

```text
$codex-company-swarm
```

因为该模式可能创建大量 SOL Max 会话和 Notion 协调写入，所以仍然禁止隐式触发。

## 验证

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover \
  -s plugins/pkos/skills/codex-company-swarm/tests -v
```

完整通过必须满足 Notion 可写、Schema Ready、同步水位到达最新事件、Outbox/死信清空、Traceability 完整、G4 ACCEPT、权威 PKOS 回写确认。Notion 只读或不可用时可以形成可恢复 Checkpoint，但不能返回 `COMPANY_SWARM_ACCEPTED`。
