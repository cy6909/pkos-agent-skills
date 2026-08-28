# Codex 公司式并行开发组织 v0.6

`codex-company-swarm` 是 PKOS 的显式最高质量并行交付模式：唯一技术总监、持续 PK-01 Notion 协调、评审门禁、开发/测试配对、MFSQ 与准确候选版本 CI、单一集成、恢复、追踪以及权威知识回写。

## v0.6：渐进式加载

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
```

`COMPANY_SWARM_ACCEPTED` 仍要求：Notion 可写且同步完成、准确候选版本 CI 通过、追踪链完整、G4 接受、PKOS 权威回写已确认，以及最终 Checkpoint、Dashboard 和复盘齐全。
