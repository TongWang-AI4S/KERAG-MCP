# KERAG MCP Server

This is a Model Context Protocol (MCP) compliant server that allows AI assistants (like Claude) to access and navigate your KERAG knowledge base.

## Related Projects

| Project | Description | Repository |
|---------|-------------|------------|
| **KERAG** | Core library for building, packing, and managing knowledge bases | [TongWang-AI4S/KERAG](https://github.com/TongWang-AI4S/KERAG) |
| **KERAG Web** | Visual knowledge explorer with web interface for browsing and searching | [TongWang-AI4S/kerag-web](https://github.com/TongWang-AI4S/kerag-web) |
| **KERAG Modules** | Pre-built knowledge base modules (ready-to-install tar archives) | [TongWang-AI4S/KERAG-Modules](https://github.com/TongWang-AI4S/KERAG-Modules) |

## Tutorials

- **Building Knowledge Bases**: Learn how to write knowledge base files, package and distribute them
  [KERAG-Tutorial.md](https://github.com/TongWang-AI4S/KERAG/blob/main/KERAG-Tutorial.md)

## Quick Start: Installation & Usage

You can install and run it directly using `pip` or `uv`.

### Step 1: Install MCP Server

**Using uv (Recommended):**
```bash
# Install as a global tool to use the kerag-mcp command anywhere
uv tool install git+https://github.com/TongWang-AI4S/kerag-mcp.git
```

**Using pip:**
```bash
pip install git+https://github.com/TongWang-AI4S/kerag-mcp.git
```

### Step 2: Configure AI Client (e.g., Claude Code)

Add the following to your `.mcp.json`:

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

### Step 3: Verify
Restart your Claude Code. You should see `kerag` tools (like `knowledge_connect`, `knowledge_load`, etc.) available.

---

## Command Line Arguments

`kerag-mcp` supports the following optional arguments:

- `--port <number>`: Set the server port (default: `5669`).
- `--host <address>`: Set the server host (default: `0.0.0.0`).
- `--transport <type>`: Set the transport protocol: `stdio` (default), `sse`, or `streamable-http`.

**Example: Running with HTTP transport**
```bash
kerag-mcp --transport streamable-http --port 8000
```

---

## Environment Variables
- `KERAG_LOCAL`: Path to your local knowledge modules.
- `KERAG_HOME`: Path to global knowledge base (defaults to `~/.kerag_modules`).
- `KERAG_LANG`: Content language preference (e.g., `zh`, `en`).

## Features

- **Search**: Perform full-text searches across your knowledge base.
- **Navigate**: Move through the hierarchical structure of your notes.
- **View**: Inspect nodes in Markdown, Tree, or JSON formats.
- **Tools**: Provides a set of tools that LLMs can use to retrieve precise context.

> **Important:** You may need **explicitly instruct** the AI assistant to search the knowledge base. AI assistants may not automatically query the knowledge base. Use prompts like:
> - "Search the knowledge base for [topic]"
> - "Look up [concept] in the knowledge base"
> - "What does the knowledge base say about [subject]?"
>
> Alternatively, list relevant knowledge modules in the system prompt or memory for the project to enable proactive retrieval.

## Sub-agent Definition

This repository includes a preliminary sub-agent definition file: [`knowledge-explorer.md`](./knowledge-explorer.md). This file defines the **Knowledge Explorer** agent, a specialized research agent that can be invoked to navigate and extract relevant information from structured knowledge bases on behalf of the main AI assistant. It provides strategic exploration capabilities using the `knowledge_*` tool series.

## Scope of Application

KERAG is designed for **highly structured, hierarchical content**:

**Best suited for:**
- Technical documentation (code docs, API references)
- Tutorials and educational materials
- Textbooks and academic notes
- Knowledge summaries and wikis
- Any content with clear hierarchical organization (chapters, sections, subsections)

**Not suitable for:**
- Narrative content (novels, stories)
- Flat, unstructured documents (news articles, blog posts)
- Conversational logs (chat histories, transcripts)
- Any content without clear hierarchical structure

## License

This project is licensed under the MIT License.
