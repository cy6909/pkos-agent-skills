# 安装

## 通过 Marketplace 安装

```bash
codex plugin marketplace add cy6909/pkos-agent-skills
codex plugin marketplace list
```

重启支持 Plugins 的桌面端，打开 Plugins，选择 PKOS Agent Skills Marketplace Source，安装 `pkos`。

更新：

```bash
codex plugin marketplace upgrade pkos-agent-skills
```

## Notion

安装 Plugin 本身不要求 Notion，但要真正持久化 Project / Memory，需要连接可读写的 Notion MCP / App。能力要求见 `NOTION-MCP.md`。

## 项目级启动入口

可把 `examples/AGENTS.md` 复制到项目仓库根目录并填写 Project ID + Notion Root URL，让 Agent 更稳定地定位项目 Root Map。
