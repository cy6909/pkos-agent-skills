# PKOS Agent Skills

简体中文 · [English](README.md)

**PKOS（Project Knowledge Operating System，项目知识操作系统）** 是一套面向 ChatGPT / Codex / AI Agent 的 skills-only 插件，用于把 Notion 变成可被 AI “寻址”的软件项目知识控制面和长期记忆控制面。

它适合这样的人或团队：同时使用多个 AI Agent、IDE、设备、代码仓库，但希望软件项目与长期记忆始终有一个**可人工检查、可跨 Agent 共享、可审计的持久事实源**。

PKOS 统一管理：

- 项目 Root Map 与当前状态；
- 产品 Capability 与全量 Feature 跟踪；
- 架构与 ADR；
- Engineering / Operations 知识；
- Current Truth、审计与结构治理；
- AI 长期记忆与用户画像；
- 有硬预算上限的低 Token 上下文检索。

PKOS **不会**在仓库里内置 Notion 凭证、固定 MCP 地址或厂商私有集成。如果 Agent 已经拥有可读写的 Notion MCP / App，Skills 会使用它；如果 Notion 不可用或只有只读权限，PKOS 会安全降级为“只读 / 待回写”模式，并明确列出尚未持久化的修改，绝不会假装同步成功。

> 核心原则：**存储可以持续增长，但上下文必须始终有界。先寻址再读取，先搜索再创建，每一种长期事实只有一个 Canonical Owner。**

## 为什么需要 PKOS？

AI 辅助开发中的项目文档通常会出现几类固定问题：

1. 不同 Agent 每次初始化项目都发明一套不同目录。
2. 为了“了解项目”，AI 递归读取巨大页面，重复消耗大量上下文 Token。
3. Feature List、Incident List、Roadmap、Architecture Overview 被反复复制。
4. 没人知道到底哪一个页面才维护当前正确事实。
5. 旧状态和新状态不断堆在同一页，最终文档本身变得不可判断。
6. 长期记忆一直累积，却没有上下文预算、淘汰和压缩机制。

PKOS 不把项目知识看成“很多文档”，而看成一个**地址空间**：

```text
Protocol            ≈ 指令集 / ABI
Project Root Map     ≈ 根页表
Domain / Capability  ≈ 二级页表
Pointer Entry        ≈ 指针 + 简短路由描述
Canonical Node       ≈ 指针指向的唯一对象
Evidence             ≈ 原始证据 / Ground Truth
Agent                ≈ 按需解引用指针的进程
```

长期记忆使用同一套思想：

```text
LLM Context          ≈ 有界物理内存
Core Profile         ≈ L1/L2 Cache
Memory Root Map      ≈ 页表
Memory Registry      ≈ 虚拟地址空间
MEM-*                ≈ 内存页
Episode / Evidence   ≈ 磁盘 / 原始事实
Context Compiler     ≈ 内存管理器
Memory GC            ≈ 垃圾回收器
```

## 仓库包含什么？

`pkos` 插件当前包含 10 个相互协作但职责独立的 Skill：

| Skill | 作用 |
|---|---|
| `codex-company-swarm` | 显式启动渐进式加载的 SOL Max 公司式开发组织：唯一技术总监、持续 Notion 协调、开发/测试配对、CI/MFSQ 证据、恢复、追踪和 PKOS 回写。 |
| `codex-sol-luna-workflow` | 成本与容量敏感的 Sol–Luna 规划/执行工作流，使用有界可复用会话和证据门禁结算。 |
| `pkos-project-session` | 普通项目工作的总入口：开发前最小上下文路由，开发后长期事实回写。 |
| `pkos-project-bootstrap` | 初始化新项目或把混乱旧项目迁移到 PKOS。 |
| `pkos-context-router` | 只读取完成当前任务所需的最小 Project Working Set。 |
| `pkos-project-writeback` | 把长期有效变化写回正确 Canonical Node，并维护 Pointer / Root 缓存一致性。 |
| `pkos-project-lint` | 检查重复 Owner、过期 Pointer、大页面、缺审计、结构漂移。 |
| `pkos-memory-context-router` | 编译一个有硬 Token 上限的长期记忆 Working Set。 |
| `pkos-memory-writeback` | 提取、去重、替代、合并、审计长期记忆。 |
| `pkos-memory-lint` | 对长期记忆执行 Lint + GC，清理重复、过期、低效用与上下文膨胀。 |

Company Swarm 的安装和上下文预算规则见：[Codex 公司式并行开发组织](docs/zh-CN/CODEX-COMPANY-SWARM.md)。

## 仓库结构

```text
pkos-agent-skills/
├── .agents/plugins/marketplace.json     # Repo Marketplace 目录
├── plugins/pkos/
│   ├── .codex-plugin/plugin.json        # 插件 Manifest
│   ├── skills/                          # Agent Skills
│   └── references/                      # 按需读取的详细规范
├── docs/
│   ├── en/                              # 英文规范
│   └── zh-CN/                           # 中文规范
├── examples/AGENTS.md                   # 可选仓库入口文件
├── scripts/validate.py                  # 本地/CI 结构校验
└── .github/workflows/validate.yml
```

## 从 GitHub Marketplace Source 安装

### 1、把本仓库加入 Codex Marketplace

```bash
codex plugin marketplace add cy6909/pkos-agent-skills
```

也可以固定到 `main`：

```bash
codex plugin marketplace add cy6909/pkos-agent-skills --ref main
```

确认 Marketplace 已添加：

```bash
codex plugin marketplace list
```

### 2、安装 `pkos` Plugin

重启 ChatGPT Desktop / 支持 Plugins 的 Codex 界面，打开 **Plugins**，选择 **PKOS Agent Skills** Marketplace Source，然后安装 **PKOS – Project & Memory OS**。

本仓库使用当前 OpenAI 官方插件目录结构：

```text
.agents/plugins/marketplace.json
plugins/pkos/.codex-plugin/plugin.json
plugins/pkos/skills/<skill>/SKILL.md
```

### 3、连接 Notion（推荐，但不是强绑定依赖）

PKOS 不内置任何 Notion Token 或固定 MCP Server。你可以连接自己使用的 Notion MCP / App。为了完整发挥 PKOS，Agent 最好具有：

- 搜索 Page / Database；
- 读取页面和数据库 Schema；
- 必要时创建 Page / Database；
- 更新 Page Content / Properties；
- 查询数据库 Row / View。

只要 Agent 具备这些能力，PKOS Skills 就会把 Notion 作为项目和长期记忆的持久控制面；如果缺少写权限，Skills 会明确输出“待回写内容”。

详见：[Notion MCP 接入规范](docs/zh-CN/NOTION-MCP.md)。

### 4、可选：为项目加入 `AGENTS.md`

如果某个代码仓库已经有固定的 PKOS Project Root Map，可以把 [examples/AGENTS.md](examples/AGENTS.md) 复制到仓库根目录，然后填入 Project ID / Notion Root URL。

`AGENTS.md` 应该很短：它只是**启动器和路由器**，不是项目知识正文。

## 更新插件

刷新这个 GitHub Marketplace：

```bash
codex plugin marketplace upgrade pkos-agent-skills
```

或者刷新所有 Marketplace：

```bash
codex plugin marketplace upgrade
```

必要时重启 Desktop / Codex 界面，让新的安装快照重新加载。

## PKOS 操作 Notion 时的四条硬规则

**Route Before Read**：从 Root Map 开始，只解引用当前任务真正需要的节点。

**Search Before Create**：创建 Page / Node / Memory 之前，必须先搜索 ID、名称、Alias、Registry 和现有 Owner。

**Canonical Owner**：每一种长期事实只有一个当前主地址。其他页面只能保存“短摘要 + Pointer”，不能演化成第二份事实源。

**Current Truth + Audit**：Canonical Page 尽量只保存当前唯一正确状态；历史放在 Audit / ADR / Incident / Git / Evidence，而不是让“旧版本正文 + 新版本正文”同时堆在 Current Truth 页面里。

## 项目统一骨架

```text
<Project> Root Map
├── 00 Control Plane
├── 10 Product
├── 15 Capabilities
│   ├── Capability Index
│   ├── Project Feature Registry   # 全项目唯一 Feature 总账
│   └── Capability Maps / filtered views
├── 20 Architecture
├── 30 Engineering
├── 40 Operations
├── 50 Planning
├── 60 Governance & Audit
├── 80 Evidence
└── 90 Archive
```

模板中没有真实内容的目录不需要创建空白页。只有出现真实知识 Owner 时才创建 Node。

完整规范见：[PKOS 中文规范](docs/zh-CN/SPEC.md)。

## Feature Registry

每个项目只有**一个 Project Feature Registry**。Capability Page 使用同一个数据库的过滤 View，不再手抄第二份功能列表。

建议核心字段：

- Stable Feature ID；
- Feature / Summary；
- Capability；
- Type；
- Lifecycle；
- Priority；
- Platforms；
- Acceptance；
- Owner Node；
- Architecture Pointer；
- Dependencies；
- Requirement / Source；
- Release；
- Last Verified；
- Audit Required。

简单 Feature 只需要 Registry Row；复杂 Feature 才创建 `FEAT-*` 详情页。

## Audit / ADR 判断标准

所有长期事实写入前先做 C0–C5 分类：

| 级别 | 含义 | Audit | ADR / Incident |
|---|---|---|---|
| C0 Editorial | 排版、错字、无语义清理 | 不需要 | 不需要 |
| C1 State | 状态、进度、Owner、验证日期 | 影响项目跟踪时记录 | 通常不需要 |
| C2 Contract | Feature 范围、API、Schema、权限、行为 | 必须 | 存在取舍/兼容影响时 ADR |
| C3 Architecture | 边界、技术栈、部署拓扑、核心依赖 | 必须 | ADR 必须 |
| C4 Structural | 合并/拆分/Owner 迁移/Node 废弃 | 必须 | 原因具长期价值时 ADR |
| C5 Incident/Security | 生产事故、安全/数据问题、回滚 | 必须 | Incident 必须；架构改变再 ADR |

Canonical Page 更新后应清理失效 Current Truth；Audit 只保存 Before/After 短摘要、原因和 Evidence，不复制旧页面全文。

## 长期记忆如何避免上下文爆炸？

PKOS 强制把“总存储容量”和“单次上下文容量”解耦：

```text
Task
 ↓
Need-Memory Gate: none | core | scoped | deep
 ↓
Scope / Status / Temporal / Sensitivity Filter
 ↓
Semantic + Keyword + Relation Retrieval
 ↓
Relevance + Salience + Confidence + Utility Ranking
 ↓
Dedup / Conflict Resolution
 ↓
Token Budget Packing
 ↓
Memory Pack
```

推荐默认值：

- M1 Core Profile：500–1000 tokens，硬上限约 1200；
- M2 Domain / Pointer：300–800；
- M3 Retrieved Memories：800–2000；
- M4 Episode / Evidence：默认 0，只在核验/历史回溯时加载；
- 普通任务长期记忆总上下文：约 1500–2500 tokens。

即使 Memory Registry 后续增长到数万条，正常单次任务仍只编译一个有限 Working Set。

## 安全与数据行为

PKOS 本身只是 Skills，不会自动授予任何外部系统权限。Agent 实际可读写的数据仍取决于用户已连接的 MCP / App 和源系统权限。

Skills 强制要求：

- Notion 写操作没有真实成功时，不得宣称已经同步；
- 敏感个人记忆提高写入门槛；
- AI 推断只能标记为 `hypothesis`，不能静默升级成用户事实；
- 用户要求 forget/delete 后，要从 active memory 和编译视图中清除该事实；
- 审计只保留治理所需的最小轨迹；
- Notion 与代码、运行环境、设计证据冲突时必须先核验，不能静默选择任意一方。

## 发布到 OpenAI 公共 Plugins Directory

GitHub Marketplace 适合直接安装、开发测试和社区分发。进入 ChatGPT / Codex 共用的 Universal Plugins Directory 是另一套官方审核流程。Skills-only plugin 可以提交，但需要最终 Skill Bundle、公开 Listing、Starter Prompts、测试用例和政策审查。

详见：[发布指南](docs/zh-CN/PUBLISHING.md)。

## 共建

欢迎贡献。请先阅读 [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)。最重要的原则是：任何新增 Skill 都必须维护 PKOS 的核心不变量，而不是重新发明一套平行的文档/记忆体系。

## License

MIT，见 [LICENSE](LICENSE)。
