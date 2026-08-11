# 参与共建 PKOS Agent Skills

感谢参与 PKOS 共建。

## 核心不变量

所有修改必须维持：

1. Route Before Read。
2. Search Before Create。
3. 每种长期事实只有一个 Canonical Owner。
4. Current Truth 保持干净，历史通过 Audit / ADR / Incident / Evidence 回溯。
5. Project Feature Registry 是项目级唯一 Feature 总账。
6. Memory Storage 可以增长，但 Context Working Set 必须始终有界。
7. Notion 写入必须真实验证，工具未成功不得宣称已持久化。
8. 敏感长期记忆不得通过 AI 推断直接升级成已确认用户画像。

## Skill 设计

每个 Skill 只解决一个可识别工作流。复杂 Schema / Policy 下沉到 `references/`，`SKILL.md` 保持足够简洁，以支持 Progressive Disclosure。

新增或修改 Skill 时要明确：

- 触发条件；
- 不应该触发的情况；
- 输入；
- 工作步骤；
- 读写边界；
- 失败行为；
- 输出契约；
- 需要按需读取的 reference。

## Pull Request

提交前运行：

```bash
python scripts/validate.py
```

PR 至少说明：

- 要解决的问题；
- 修改的 Protocol / Skill；
- 兼容性影响；
- 至少一个应触发示例；
- 至少一个不应触发示例。

破坏协议兼容性的修改同时更新 `CHANGELOG.md`。
