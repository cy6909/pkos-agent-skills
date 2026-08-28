# Codex 公司式并行开发组织

`codex-company-swarm` 是 PKOS 的最高质量、高并发、无需优先考虑 Token 成本的完整交付模式。它把一个 Codex 根会话作为技术总监，由该会话统一管理常驻评审委员会、各领域开发组、与开发强制配对的独立测试组、CI/CD 平台组、安全与性能专家、单一集成负责人以及 PKOS 回写角色。

## 安装

刷新并安装本仓库的 `pkos` 插件后，安装自定义角色 TOML：

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/install.py --agents-only
```

仅为某个项目安装：

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/install.py \
  --project-root /path/to/project
```

按当前 Codex 版本支持情况合并 `assets/config.toml.fragment`，重启 Codex 或新开任务，然后显式调用：

```text
$codex-company-swarm
```

由于这个模式可能创建大量 SOL Max 会话，Skill 默认禁止隐式触发。

## 核心组织规则

- 当前会话就是唯一的 `TD-01` 技术总监，禁止再拉起第二个总监。
- `RB-01` 评审主席负责需求、现状差距、实现路径、功能清单和最终实现评审。
- 每个产品代码开发会话必须与一个测试会话双向绑定；开发不负责决定测试范围，也不能自行宣布测试通过。
- 测试会话使用 MFSQ 设计并实现测试，行为变化必须有安全与性能测试或经评审主席批准的 N/A；所有权威测试必须进入流水线。
- 已有有效 CI/CD 时继续使用；没有可用流水线时，由 CI 角色搭建源码化 Jenkins Pipeline。
- 只有一个集成负责人生成累计候选版本；评审委员会负责通过或打回；技术总监最终用图表和证据向用户汇报，并执行或生成可核验的 PKOS 回写。

完整 G0–G5 规则见 Skill 的 `SKILL.md` 与 `references/`。

## 验证

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover \
  -s plugins/pkos/skills/codex-company-swarm/tests -v
```
