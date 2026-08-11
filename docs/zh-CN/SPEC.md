# PKOS 完整规范

## 1、项目知识

PKOS 把项目知识抽象成地址空间。Root / Domain / Capability Map 负责路由；Canonical Node 负责维护唯一 Current Truth；Evidence 用来验证事实。

核心不变量：

1. Route Before Read。
2. Search Before Create。
3. 每一种长期事实只有一个 Canonical Owner。
4. Progressive Disclosure + Stop Rule。
5. Current Truth 保持干净；历史通过 Audit / ADR / Incident / Evidence 回溯。
6. Pointer Summary 是缓存，不是第二份事实源。
7. 新 Canonical Node 必须注册到唯一主要父 Map。

### 分层

- L0：Protocol；
- L1：Project Root，建议 800–1500 tokens；
- L2：Domain / Capability Map，建议每页 500–1200；
- L3：Canonical Node；
- L4：原始 Evidence。

### 项目骨架

`00 Control Plane / 10 Product / 15 Capabilities / 20 Architecture / 30 Engineering / 40 Operations / 50 Planning / 60 Governance & Audit / 80 Evidence / 90 Archive`。

### Capability 与 Feature

Architecture 回答“系统有什么、如何连接”；Capability 回答“每个部分提供什么能力”；Engineering 回答“代码如何实现”。

一个项目只能有一个 Feature Registry。Capability 页面使用同一数据库的过滤 View。

## 2、Current Truth / Audit / ADR

所有长期事实变化按 C0–C5 分类。C2+ 必须 Audit，C3 必须 ADR，C5 必须 Incident。Current Canonical Page 不应该长期同时堆叠已经废弃的完整旧正文和新正文。

Audit Event 保存紧凑的 Before/After Summary、原因、Actor、Evidence、Verification 和关联 ADR/Incident。

## 3、长期记忆

Notion Memory Registry 是长期地址空间；Core Profile 是编译缓存；Episode 是来源证据。

Memory Type：profile-semantic / goal-state / procedural / episodic。

动态事实必须具有时间有效性。同一语义不能同时存在互相冲突的多个 Active Fact。

### 有界上下文

总记忆规模不得决定单次 Prompt 大小。每次任务先经过 Need-Memory Gate，再经过 Scope / Status / Temporal / Sensitivity Filter、Retrieval / Ranking、Dedup / Conflict、Token Budget Packing。

普通任务长期记忆建议约 1500–2500 tokens。

### Compaction / GC

高度重复的 Current Memory 合并成一个 Canonical Memory，Episode 保留。GC 检查 Duplicate、Expired、Stale、Low Utility、Orphan、Unsupported Sensitive Inference、Contradiction、Forget/Delete Residue。

## 4、Notion 接入

PKOS 不绑定具体 Tool Name。它使用当前已连接 Notion MCP / App 暴露的能力；没有真实成功响应时，绝不能宣称写入已经完成。
