# Notion MCP 接入

PKOS 不绑定某一个 Notion MCP 实现。Agent 应先发现当前工具，然后映射到以下能力：

- 搜索 Page / Database；
- 读取 Page Content / Database Schema；
- 查询 Registry Row / View；
- 通过 Search Before Create 后再创建 Page / Database；
- 更新 Page Content / Properties / Registry Row；
- 核验写操作响应。

## 行为规则

Notion 可写时，PKOS 把长期有效 Project / Memory 事实持久化到 Notion。

Notion 只读时，可以读取上下文，但不能绕过权限；应输出 Pending Writeback。

Notion 不可用时，只要代码/当前上下文足够，主要开发任务仍可继续，但不得宣称持久化完成。

## SSOT 的边界

Notion 是长期控制面，不代表它永远比代码/运行结果正确。Code、Config、Runtime、Test、Log、Design 发现冲突时，应先通过 Evidence 复核，再修复 Notion，让后续 Agent 重新获得唯一 Current Truth。
