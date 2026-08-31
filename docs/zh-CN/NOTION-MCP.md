# Notion MCP 接入

## 中文写入要求

PKOS 的所有技能在向 Notion 写入面向人的内容时，默认使用准确、自然、便于理解的简体中文（`NOTION_WRITE_LANGUAGE=zh-CN`）。页面标题、摘要、状态说明、决策理由、风险、行动项、审计记录、长期记忆正文和待回写内容都适用该规则。

为保证机器契约和证据准确，Schema 属性名、ID、枚举值、代码符号、API 名称、文件路径、命令、URL、哈希、Commit SHA 与原始错误信息保持原文。写入后必须回读标题、属性值和正文；只有内容已持久化且中文语义准确、清楚、没有虚构信息，才能报告写入成功。用户明确要求其他语言或既有规范指定其他语言时，以该要求为准。

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
