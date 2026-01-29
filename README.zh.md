# KERAG MCP Server (MCP 服务)

这是一个符合 Model Context Protocol (MCP) 标准的服务器，允许 AI 助手（如 Claude）访问和导航您的 KERAG 知识库。

## 🔗 相关项目

| 项目 | 描述 | 仓库 |
|---------|-------------|------------|
| **KERAG** | 核心库，用于构建、打包和管理知识库 | [TongWang-AI4S/KERAG](https://github.com/TongWang-AI4S/KERAG) |
| **KERAG Web** | 可视化知识浏览器，提供 Web 界面用于浏览和搜索 | [TongWang-AI4S/kerag-web](https://github.com/TongWang-AI4S/kerag-web) |
| **KERAG Modules** | 预构建知识库模块（可直接安装的 tar 文件） | [TongWang-AI4S/KERAG-Modules](https://github.com/TongWang-AI4S/KERAG-Modules) |

## 📚 教程

- **构建知识库**：学习如何编写知识库文件、打包和分发
  👉 [KERAG-Tutorial.zh.md](https://github.com/TongWang-AI4S/KERAG/blob/main/KERAG-Tutorial.zh.md)

## 🚀 快速开始：从零开始安装与运行

可以直接通过 `pip` 或 `uv` 进行安装。

### 第一步：安装 MCP 服务

**使用 uv (推荐):**
```bash
# 将其作为全局工具安装，以便在任何地方调用 kerag-mcp 命令
uv tool install git+https://github.com/TongWang-AI4S/kerag-mcp.git
```

**使用 pip:**
```bash
pip install git+https://github.com/TongWang-AI4S/kerag-mcp.git
```

### 第二步：配置到 AI 客户端 (以 Claude Code为例)

打开您的 `.mcp.json`，添加配置：

```json
{
  "mcpServers": {
    "knowledge-explorer": {
        "type": "stdio",
        "command": "kerag-mcp", 
        "env": {
          "KERAG_LANG": "en"
        }
      }
    }
}
```

### 第三步：验证运行
重启您的 Claude 客户端，您应该能在工具栏看到 `kerag` 相关的工具（如 `knowledge_connect`, `knowledge_load` 等）。

---

## ⚙️ 命令行参数

`kerag-mcp` 支持以下可选参数进行配置：

- `--port <number>`: 设置服务器监听端口（默认为 `5669`）。
- `--host <address>`: 设置服务器监听地址（默认为 `0.0.0.0`）。
- `--transport <type>`: 设置传输协议，可选 `stdio` (默认), `sse`, 或 `streamable-http`。

**示例：使用 HTTP 传输运行**
```bash
kerag-mcp --transport streamable-http --port 8000
```

---

## 🌍 环境变量
您可以根据需要配置以下环境变量：
- `KERAG_LOCAL`: 本地知识库模块目录（当前工作目录下的 `.kerag_modules`）。
- `KERAG_HOME`: 全局知识库目录（默认为 `~/.kerag_modules`）。
- `KERAG_LANG`: 知识库内容语言偏好（如 `zh`, `en`）。

## ✨ 功能

- **搜索**: 在知识库中执行全文搜索。
- **导航**: 在知识库的层级结构中前后导航或移动。
- **查看**: 以 Markdown、树形或 JSON 格式查看节点详细内容。
- **工具**: 提供一组 AI 可调用的工具，用于检索精确的上下文。

> **重要提示：** 您可能需要**显式指示** AI 助手去搜索知识库。AI 助手可能不会自动查询知识库。请使用如下提示：
> - "在知识库中搜索 [主题]"
> - "查找知识库中关于 [概念] 的内容"
> - "知识库中对 [课题] 是怎么说的？"
>
> 或者，在项目的系统提示或记忆中列出相关知识模块，以实现主动检索。

## 🤖 子智能体定义

本仓库包含一个初步的子智能体定义文件：[`knowledge-explorer.md`](./knowledge-explorer.md)。该文件定义了**知识探索者 (Knowledge Explorer)** 智能体，这是一个专门的研究代理，可以代表主 AI 助手被调用，用于从结构化知识库中导航和提取相关信息。它提供了使用 `knowledge_*` 工具系列进行探索的能力。

## 📋 适用范围

KERAG 专为**高度结构化、层级化的内容**而设计：

**✅ 最适合的场景：**
- 技术文档（代码文档、API 参考）
- 教程和教育材料
- 教科书和学术笔记
- 知识总结和百科
- 任何具有清晰层级结构的内容（章、节、小节）

**❌ 不适用的场景：**
- 叙事性内容（小说、故事）
- 平铺、非结构化文档（新闻文章、博客文章）
- 对话记录（聊天记录、对话转录）
- 任何没有清晰层级结构的内容

## 📄 开源协议

本项目采用 MIT 开源协议。
