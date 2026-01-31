# KERAG MCP Server (Knowledge Explorer MCP)

KERAG MCP 是一个符合 **Model Context Protocol (MCP)** 标准的服务器。它作为连接 AI 助手（如 Claude Code, Cursor）与 KERAG 知识库的桥梁，允许 AI 像人类一样在结构化的“知识树”中导航、搜索和提取上下文。

它不是简单的文本检索，而是赋予了 AI 助手在 KERAG 知识树（森林）中导航检索的能力。

## 相关项目

| 项目 | 描述 | 仓库 |
| --- | --- | --- |
| **KERAG** | 核心库，用于构建、打包和管理结构化知识库 | [TongWang-AI4S/KERAG](https://github.com/TongWang-AI4S/KERAG) |
| **KERAG Web** | 可视化浏览器，提供 Web 界面用于手动浏览 | [TongWang-AI4S/kerag-web](https://github.com/TongWang-AI4S/kerag-web) |

## 教程

- **构建知识库**：学习如何编写知识库文件、打包和分发

  [KERAG-Tutorial.zh.md](https://github.com/TongWang-AI4S/KERAG/blob/main/KERAG-Tutorial.zh.md)

## 核心功能

* **层级导航**：AI 可以在知识库的章、节、小节中前后跳转，理解上下文。
* **全文搜索**：支持在海量知识模块中执行精确的全文检索。
* **多格式查看**：支持以 Markdown、树形结构或 JSON 格式输出节点内容。
* **子智能体支持**：内置 `knowledge-explorer.md` 定义，支持作为独立研究代理运行。

---

## 快速开始

### 1. 安装服务

推荐使用 `uv` 进行快速安装，也可以使用 `pip`：

```bash
# 使用 uv (推荐)
uv tool install git+https://github.com/TongWang-AI4S/kerag-mcp.git

# 使用 pip
pip install git+https://github.com/TongWang-AI4S/kerag-mcp.git

```

### 2. 配置 AI 客户端

以 **Claude Code** 为例，在 `.mcp.json` 或配置文件中添加：

```json
{
  "mcpServers": {
    "knowledge-explorer": {
      "type": "stdio",
      "command": "kerag-mcp",
      "env": {
        "KERAG_LANG": "zh"
      }
    }
  }
}

```

### 3. 验证运行

重启客户端后，若看到 `knowledge_connect`、`knowledge_load`、`knowledge_search` 等工具，说明集成成功。

---

## 进阶配置

### 命令行参数

`kerag-mcp` 支持自定义传输协议和网络设置：

* `--transport <type>`：可选 `stdio` (默认), `sse`, 或 `streamable-http`。
* `--port <number>`：设置端口（默认 `5669`）。
* `--host <address>`：设置地址（默认 `0.0.0.0`）。

### 环境变量

| 变量名 | 描述 | 默认值 |
| --- | --- | --- |
| **KERAG_LOCAL** | 项目局部知识库路径 | `./.kerag_modules` |
| **KERAG_HOME** | 全局知识库路径 | `~/.kerag_modules` |
| **KERAG_LANG** | 知识库内容语言偏好 | `en` (支持 `zh`) |

---

## 使用技巧

> [!IMPORTANT]
> **显式引导：** AI 助手有时不会主动触发检索。若想获得最佳效果，请尝试如下指令：
> * "在知识库中搜索关于 [主题] 的定义。"
> * "查找知识库中 [模块名] 的章节结构。"
> * "根据知识库中的 API 指南修改这段代码。"

## 子智能体定义

本仓库包含一个初步的子智能体定义文件：[`knowledge-explorer.md`](./knowledge-explorer.md)。该文件定义了**知识探索者 (Knowledge Explorer)** 智能体，这是一个专门的研究代理，可以代表主 AI 助手被调用，用于从结构化知识库中导航和提取相关信息。它提供了使用 `knowledge_*` 工具系列进行探索的能力。


---

## 适用范围
KERAG 专为高度结构化、层级化的内容而设计：

**最适合的场景：**
* **技术文档：** 代码文档、API 参考手册。
* **教育材料：** 结构化的教程、教科书、学术笔记。
* **知识库：** 个人经验总结、百科条目。
* **层级文档：** 任何具有清晰章、节、小节结构的内容。

**不适用的场景：**
* **叙事内容：** 小说、散文或故事情节。
* **非结构化文档：** 单篇的新闻报导或随笔博文。
* **流式记录：** 聊天记录、会议对话转录。
* **碎片信息：** 任何缺乏明确层级逻辑的扁平内容。

---

> ### KERAG Modules - 知识库分享
>
> 在[KERAG-Modules](https://github.com/TongWang-AI4S/KERAG-Modules)仓库，本人会分享一些自己生成的知识库模块，可以直接安装到自己的 KERAG 环境中使用。
> ```bash
> kerag install kerag install https://raw.githubusercontent.com/TongWang-AI4S/KERAG-Modules/refs/heads/main/example/module-name.tar

## 开源协议

本项目采用 MIT 开源协议。