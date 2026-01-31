# KERAG MCP Server (Knowledge Explorer MCP)

KERAG MCP is a server compliant with the **Model Context Protocol (MCP)** standard. It serves as a bridge between AI assistants (such as Claude Code, Cursor) and the KERAG knowledge base, allowing AI to navigate, search, and extract context within a structured "knowledge tree" just like humans do.

Unlike simple text retrieval, it empowers AI assistants with the ability to navigate and retrieve information within the KERAG knowledge tree (forest).

## Related Projects

| Project | Description | Repository |
| --- | --- | --- |
| **KERAG** | Core library for building, packaging, and managing structured knowledge bases | [TongWang-AI4S/KERAG](https://github.com/TongWang-AI4S/KERAG) |
| **KERAG Web** | Visual browser providing a Web interface for manual exploration | [TongWang-AI4S/kerag-web](https://github.com/TongWang-AI4S/kerag-web) |

## Tutorial

- **Building a Knowledge Base**: Learn how to write knowledge base files, package, and distribute them

  [KERAG-Tutorial.md](https://github.com/TongWang-AI4S/KERAG/blob/main/KERAG-Tutorial.md)

## Core Features

* **Hierarchical Navigation**: AI can navigate forward and backward through chapters, sections, and subsections of the knowledge base, understanding the context.
* **Full-text Search**: Supports precise full-text retrieval across massive knowledge modules.
* **Multi-format Viewing**: Supports outputting node content in Markdown, tree structure, or JSON formats.
* **Sub-agent Support**: Built-in `knowledge-explorer.md` definition, supporting operation as an independent research agent.

---

## Quick Start

### 1. Install the Server

It is recommended to use `uv` for quick installation, but `pip` is also supported:

```bash
# Using uv (recommended)
uv tool install git+https://github.com/TongWang-AI4S/kerag-mcp.git

# Using pip
pip install git+https://github.com/TongWang-AI4S/kerag-mcp.git
```

### 2. Configure the AI Client

Taking **Claude Code** as an example, add the following to `.mcp.json` or the configuration file:

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

### 3. Verify Operation

After restarting the client, if you see tools such as `knowledge_connect`, `knowledge_load`, `knowledge_search`, etc., the integration is successful.

---

## Advanced Configuration

### Command Line Arguments

`kerag-mcp` supports custom transport protocols and network settings:

* `--transport <type>`: Options are `stdio` (default), `sse`, or `streamable-http`.
* `--port <number>`: Set the port (default `5669`).
* `--host <address>`: Set the address (default `0.0.0.0`).

### Environment Variables

| Variable Name | Description | Default Value |
| --- | --- | --- |
| **KERAG_LOCAL** | Project-local knowledge base path | `./.kerag_modules` |
| **KERAG_HOME** | Global knowledge base path | `~/.kerag_modules` |
| **KERAG_LANG** | Knowledge base content language preference | `en` (supports `zh`) |

---

## Usage Tips

> [!IMPORTANT]
> **Explicit Guidance:** AI assistants may not always proactively trigger retrieval. For best results, try commands like:
> * "Search the knowledge base for definitions about [topic]."
> * "Find the chapter structure of [module name] in the knowledge base."
> * "Modify this code according to the API guide in the knowledge base."

## Sub-agent Definition

This repository contains a preliminary sub-agent definition file: [`knowledge-explorer.md`](./knowledge-explorer.md). This file defines the **Knowledge Explorer** agent, a specialized research agent that can be invoked on behalf of the main AI assistant to navigate and extract relevant information from structured knowledge bases. It provides the capability to explore using the `knowledge_*` tool series.

---

## Scope of Application

KERAG is specifically designed for highly structured, hierarchical content:

**Best For:**
* **Technical Documentation:** Code documentation, API reference manuals.
* **Educational Materials:** Structured tutorials, textbooks, academic notes.
* **Knowledge Bases:** Personal experience summaries, encyclopedia entries.
* **Hierarchical Documents:** Any content with a clear structure of parts, chapters, and sections.

**Not Recommended For:**
* **Narrative Content:** Novels, essays, or plot-driven stories.
* **Unstructured Documents:** Single news reports or casual blog posts.
* **Streaming Logs:** Chat history, meeting transcripts.
* **Fragmented Information:** Any flat content lacking clear hierarchical logic.

---

> ### KERAG Modules - Knowledge Base Sharing
>
> In the [KERAG-Modules](https://github.com/TongWang-AI4S/KERAG-Modules) repository, I share some knowledge base modules I've generated, which can be installed directly into your KERAG environment.
> ```bash
> kerag install https://raw.githubusercontent.com/TongWang-AI4S/KERAG-Modules/refs/heads/main/example/module-name.tar
> ```

## License

This project is licensed under the MIT License.
