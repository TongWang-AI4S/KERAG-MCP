#!/usr/bin/env python3
"""
KERAG MCP Server - Knowledge Base MCP Server

A server implementation based on the Model Context Protocol (MCP) standard,
allowing access to the KERAG knowledge base via the MCP protocol.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from mcp.server.fastmcp import FastMCP
from .session_manager import get_session_manager
from . import format_response

# Configure global logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("kerag_mcp")

# Parse command line arguments (needs to be before FastMCP initialization)
parser = argparse.ArgumentParser(description="Start KERAG MCP Server", add_help=False)
parser.add_argument(
    "--port",
    type=int,
    default=5669,
    help="Server port (default: 5669(K-N-O-W))"
)
parser.add_argument(
    "--host",
    type=str,
    default="0.0.0.0",
    help="Server host (default: 0.0.0.0)"
)
parser.add_argument(
    "--transport",
    type=str,
    choices=["stdio", "sse", "streamable-http"],
    default="stdio",
    help="Transport protocol to use (default: stdio)"
)
# Keep -h option for help
parser.add_argument(
    "-h", "--help",
    action="store_true",
    help="Show this help message and exit"
)

# Parse only known args, ignore unknown ones (used internally by mcp.run)
args, unknown = parser.parse_known_args()

# Show help message and exit
if args.help:
    parser.print_help()
    sys.exit(0)

# Initialize FastMCP server (using command line arguments)
mcp = FastMCP("KERAG - Knowledge Explorer Retrieval Augmented Generation", port=args.port, host=args.host)

# Global session manager
session_manager = get_session_manager()

print(f"Starting KERAG MCP Server...")
print(f"Host: {args.host}")
print(f"Port: {args.port}")


# === Session Management Tools ===

@mcp.tool()
async def knowledge_connect(
    local_root: Optional[str] = None,
    global_root: Optional[str] = None,
    lang: Optional[str] = None,
    init_with: Optional[str] = None
) -> str:
    """
    Establish connection to the KERAG knowledge base.

    Creates or updates a knowledge base session. This is the FIRST tool you must
    call before using any other knowledge_* tools. Without a session, all other
    tools will raise RuntimeError.

    Args:
        local_root: Path to local modules. None for the default path
            (./.kerag_modules or KERAG_LOCAL env var).
        global_root: Path to global modules. None for the default path
            (~/.kerag_modules or KERAG_HOME env var).
        lang: Language preference ('zh' or 'en'). Affects error messages and UI.
        init_with: Space-separated module names to load immediately on startup.
            If provided, loads these modules and shows their root nodes.
            If not provided, shows a list of all available modules.

    Returns:
        Connection status with session configuration, plus either:
        - If init_with specified: Root nodes of loaded modules
        - If no init_with: Table of available modules with load status (Y/N)

    Typical Workflow:
        1. knowledge_connect(init_with="module1 module2")  # Start session
        2. knowledge_roots()  # View entry points
        3. knowledge_view(node_id="module::label")  # Read content

    See Also:
        knowledge_list - View available modules without loading
        knowledge_load - Load additional modules after connection

    Raises:
        RuntimeError: If session cannot be established.
    """
    session_id = 0
    local_root_str = f", local_root={local_root}" if local_root else ""
    global_root_str = f", global_root={global_root}" if global_root else ""
    logger.info(f"knowledge_connect: Establishing session, session_id={session_id}{local_root_str}{global_root_str}")

    # Create or update session
    api = session_manager.create_session(
        session_id=session_id,
        local_root=local_root,
        global_root=global_root,
        lang=lang
    )

    # If init_with parameter is present, load specified modules
    initialized_modules = []
    if init_with:
        modules = init_with.split()
        for module_name in modules:
            try:
                result = api.load_module(module_name)
                if result.get("success"):
                    initialized_modules.append(module_name)
                    logger.info(f"knowledge_connect: Successfully loaded module {module_name}")
                else:
                    logger.warning(f"knowledge_connect: Failed to load module {module_name}, error={result.get('error')}")
            except Exception as e:
                logger.error(f"knowledge_connect: Exception loading module {module_name}, error={str(e)}")

        # After loading modules, show loaded roots
        roots_res = api.get_loaded_roots()
        if roots_res.get("success"):
            roots_text = format_response.format_roots_list(roots_res["data"])
            logger.info("knowledge_connect: Initial modules loaded, displaying roots")
        else:
            roots_text = ""
    else:
        # If no modules specified, show all available modules
        list_result = api.list_modules(scope="both")
        if list_result.get("success"):
            data = list_result.get("data", {})
            modules_data = data.get("modules", {})
            loaded_modules = set(data.get("loaded_modules", []))

            def format_table(modules_dict, title):
                if not modules_dict:
                    return []

                rows = []
                # Header - use Y/N format
                rows.append(["Name", "Version", "Loaded (Y/N)", "Description"])

                for name in sorted(modules_dict.keys()):
                    info = modules_dict[name]
                    is_loaded = "Y" if name in loaded_modules else "N"
                    ver_str = info.get("version", "-") or "-"
                    desc_str = info.get("description", "-") or "-"
                    rows.append([name, ver_str, is_loaded, desc_str])

                # Calculate widths
                col_widths = [0, 0, 0, 0]
                for row in rows:
                    for i, col in enumerate(row):
                        col_widths[i] = max(col_widths[i], len(str(col)))

                # Add spacing
                col_widths = [w + 4 for w in col_widths]

                lines = [title]
                # Header line
                header = rows[0]
                lines.append(f"{header[0]:<{col_widths[0]}}{header[1]:<{col_widths[1]}}{header[2]:<{col_widths[2]}}{header[3]}")

                # Data lines
                for row in rows[1:]:
                     lines.append(f"{row[0]:<{col_widths[0]}}{row[1]:<{col_widths[1]}}{row[2]:<{col_widths[2]}}{row[3]}")

                lines.append("")
                return lines

            output_lines = []
            if "local" in modules_data and modules_data["local"]:
                output_lines.extend(format_table(modules_data["local"], "Available Local Modules:"))

            if "global" in modules_data and modules_data["global"]:
                output_lines.extend(format_table(modules_data["global"], "Available Global Modules:"))

            if output_lines:
                roots_text = "\n".join(output_lines)
            else:
                roots_text = "\nNo modules found"
        else:
            roots_text = ""
        logger.info("knowledge_connect: No modules specified, displaying available modules")

    status_res = api.get_status()
    logger.info(f"knowledge_connect: Session established successfully, loaded modules count={len(initialized_modules)}")

    data = {
        "session_id": session_id,
        "status": "connected",
        "config": {
            "local_root": local_root,
            "global_root": global_root,
            "lang": lang,
            "initialized_modules": initialized_modules
        },
        "api_status": status_res.get("data")
    }

    response_text = format_response.format_connect_response(data)
    if roots_text:
        response_text += "\n" + roots_text

    return response_text


# === Module Management Tools ===

@mcp.tool()
async def knowledge_list(scope: str = "both") -> str:
    """
    List all available (installed) knowledge modules.

    Shows all modules found in local and/or global module directories,
    regardless of whether they are loaded. Use this to discover what
    modules you can load.

    Args:
        scope: Filter scope to control which directories to scan:
            - 'both': Local and global modules (default)
            - 'local': Only local modules (./.kerag_modules)
            - 'global': Only global modules (~/.kerag_modules)

    Returns:
        Formatted table with columns:
        - Name: Module name
        - Version: Module version
        - Loaded (Y/N): Whether loaded in current session
        - Description: Brief module description
        Plus local_root and global_root paths at the bottom.

    Difference from knowledge_modules:
        - knowledge_list: Shows ALL available modules (installed but not loaded)
        - knowledge_modules: Shows only LOADED modules with detailed info

    Typical Use Cases:
        - Discover available modules to load
        - Check if a module is already loaded before calling knowledge_load

    See Also:
        knowledge_modules - List only currently loaded modules
        knowledge_load - Load a module to use its content

    Raises:
        RuntimeError: If session not found. Call knowledge_connect first.
    """
    if not scope:
        scope = "both"
    logger.info(f"knowledge_list: Listing all module info, scope={scope}")

    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found, please call knowledge_connect first")

    result = api.list_modules(scope=scope)

    if not result.get("success"):
        return format_response.format_error(f"Failed to get module list: {result.get('error')}")

    data = result.get("data", {})
    modules_data = data.get("modules", {})
    output_lines = []

    loaded_modules = set(data.get("loaded_modules", []))

    def format_table(modules_dict, title):
        if not modules_dict:
            return []

        rows = []
        # Header - use Y/N format
        rows.append(["Name", "Version", "Loaded (Y/N)", "Description"])

        for name in sorted(modules_dict.keys()):
            info = modules_dict[name]
            is_loaded = "Y" if name in loaded_modules else "N"
            ver_str = info.get("version", "-") or "-"
            desc_str = info.get("description", "-") or "-"
            rows.append([name, ver_str, is_loaded, desc_str])

        # Calculate widths
        col_widths = [0, 0, 0, 0]
        for row in rows:
            for i, col in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(col)))

        # Add spacing
        col_widths = [w + 4 for w in col_widths]

        lines = [title]
        # Header line
        header = rows[0]
        lines.append(f"{header[0]:<{col_widths[0]}}{header[1]:<{col_widths[1]}}{header[2]:<{col_widths[2]}}{header[3]}")

        # Data lines
        for row in rows[1:]:
             lines.append(f"{row[0]:<{col_widths[0]}}{row[1]:<{col_widths[1]}}{row[2]:<{col_widths[2]}}{row[3]}")

        lines.append("")
        return lines

    if "local" in modules_data and modules_data["local"]:
        output_lines.extend(format_table(modules_data["local"], "Local Modules:"))

    if "global" in modules_data and modules_data["global"]:
        output_lines.extend(format_table(modules_data["global"], "Global Modules:"))

    if not output_lines:
        output_lines.append("No modules found")

    output_lines.append(f"Local Root: {data.get('local_root', 'N/A')}")
    output_lines.append(f"Global Root: {data.get('global_root', 'N/A')}")

    return "\n".join(output_lines)


@mcp.tool()
async def knowledge_modules() -> str:
    """
    List all currently loaded modules with detailed information.

    Shows only modules that have been loaded into the current session
    via knowledge_connect(init_with=...) or knowledge_load().

    Returns:
        Formatted list with detailed module information including:
        - Module name and version
        - Description and author
        - Number of files and nodes
        - Root node IDs

    Difference from knowledge_list:
        - knowledge_modules: Shows only LOADED modules with full details
        - knowledge_list: Shows ALL available modules (basic info only)

    Typical Use Cases:
        - Check which modules are currently active
        - Get detailed stats about loaded modules
        - Find root node IDs for navigation

    See Also:
        knowledge_list - View all available (installed) modules
        knowledge_roots - Get root nodes of loaded modules only

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    res = api.get_all_modules()
    if not res.get("success"):
        return format_response.format_error(f"Failed to get modules: {res.get('error')}")

    modules = [m for m in res["data"].get("modules", []) if m["loaded"]]
    return format_response.format_modules_list(modules)


@mcp.tool()
async def knowledge_roots() -> str:
    """
    Get root nodes of all currently loaded modules.

    Root nodes are the entry points (top-level nodes) of each loaded module.
    Use these to start exploring the knowledge base structure.

    Returns:
        Formatted list of root nodes showing:
        - Node title (human-readable name)
        - Full node ID in format 'module::label' (e.g., 'docs::intro')

    Typical Workflow:
        1. knowledge_roots()  # Get all entry points
        2. knowledge_children_preview(node_id="module::root")  # Browse structure
        3. knowledge_to(target="module::section")  # Navigate to specific section

    Note:
        The special node "::ROOT" is always listed and represents the
        virtual root above all modules.

    See Also:
        knowledge_children_preview - Browse children of a root node
        knowledge_to - Navigate to a specific node by ID

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    res = api.get_loaded_roots()
    if not res.get("success"):
        return format_response.format_error(f"Failed to get root nodes: {res.get('error')}")
    return format_response.format_roots_list(res["data"])


@mcp.tool()
async def knowledge_load(module_name: str) -> str:
    """
    Load a knowledge module into the session.

    A module must be loaded before its content can be accessed. After loading,
    the module's nodes become searchable and navigable.

    Args:
        module_name: Name of the module to load (e.g., 'python-guide').
            Use knowledge_list() to see available module names.

    Returns:
        Loading confirmation plus root nodes of the loaded module:
        - Success/error message
        - List of root node IDs for the newly loaded module

    Typical Workflow:
        1. knowledge_list()  # Find available modules
        2. knowledge_load("module-name")  # Load specific module
        3. knowledge_roots()  # See updated root list
        4. knowledge_view(node_id="module::root")  # Start reading

    Performance Note:
        Modules use lazy loading - only the structure is loaded initially.
        Content is loaded on-demand when you access specific nodes.

    See Also:
        knowledge_list - Find available modules to load
        knowledge_roots - View root nodes after loading
        knowledge_connect(init_with=...) - Load modules at startup

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    load_result = api.load_module(module_name)
    result_text = format_response.format_load_result(load_result)

    if load_result.get("success"):
        # After successful load, filter roots for this module
        roots_res = api.get_loaded_roots()
        if roots_res.get("success"):
            # Filter roots that start with module_name/ or module_name::
            module_roots = [
                root for root in roots_res["data"]
                if root.get("id", "").startswith(f"{module_name}/") or
                   root.get("id", "").startswith(f"{module_name}::")
            ]
            if module_roots:
                roots_text = format_response.format_roots_list(module_roots)
                result_text += "\n" + roots_text

    return result_text


# === Node Query Tools ===

@mcp.tool()
async def knowledge_search(
    query: str,
    search_under: Optional[str] = None,
    order: str = "priority",
    max_results: int = 50,
    whole_word: bool = False,
    case_sensitive: bool = False,
    use_regex: bool = False,
    with_parents: bool = True
) -> str:
    """
    Search for nodes across all loaded modules.

    Performs text search in node titles, labels, or content. Supports
    regular expressions for advanced pattern matching.

    Args:
        query: Search keywords or regular expression pattern.
        search_under: Optional root node ID (e.g. 'module::label' or 'module' being short for 'module::module') to restrict search to a specific subtree.
            If not provided, searches all loaded modules.
        order: Sort order for results:
            - 'priority': Sort by relevance (Title > Content > Label) (default).
            - 'dfs': Sort by document order (depth-first traversal).
        max_results: Maximum matches to return (default: 50).
        whole_word: Match whole words only (default: False).
        case_sensitive: Case-sensitive matching (default: False).
        use_regex: Treat query as regex pattern (default: False).
        with_parents: Include parent node info in results (default: True).

    Returns:
        Formatted search results showing:
        - Match count (e.g., "Showing 5 of 12 matches")
        - For each match:
          * Node type ([section] or [content])
          * Node ID in 'module::label' format
          * Parent node info (if with_parents=True)
          * Content snippet with context

    Typical Workflow:
        1. knowledge_search("API authentication")  # Broad search
        2. knowledge_search("config", search_under="docs::config") # Scoped search
        3. knowledge_view(node_id="module::section")  # Read the found node

    See Also:
        knowledge_view - View full content of a found node
        knowledge_to - Navigate to a found node

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    search_res = api.search(
        keyword=query,
        search_under=search_under,
        order=order,
        max_results=max_results,
        whole_word=whole_word,
        case_sensitive=case_sensitive,
        use_regex=use_regex
    )

    if not search_res.get("success"):
        return format_response.format_search_results(search_res)

    # Post-process results if parent info is requested
    if with_parents and search_res.get("data"):
        results = search_res["data"]
        for item in results:
            try:
                # Get immediate parent info instead of full breadcrumb
                parent_res = api.get_parent(item["node_id"])
                if parent_res.get("success"):
                    p_data = parent_res["data"]
                    # Skip ROOT as parent for a cleaner look
                    if p_data["node_id"] != "::ROOT":
                        item["parent"] = {
                            "node_id": p_data["node_id"],
                            "title": p_data.get("title", ""),
                            "label": p_data.get("label", "")
                        }
            except Exception as e:
                item["parent_error"] = str(e)

    return format_response.format_search_results(search_res)


@mcp.tool()
async def knowledge_view(
    node_id: Optional[str] = None,
    depth: int = 1,
    format: str = "markdown",
    include_content: bool = True,
    include_see_also: bool = True
) -> str:
    """
    View detailed content of a specific knowledge node.

    Displays the full content of a node including its title, body text,
    and optionally its children structure and cross-references.

    Args:
        node_id: Target node ID in 'module::label' format (e.g., 'docs::intro').
            Uses current location if not provided.
        depth: Hierarchy depth to display, with the target node as depth=0:
            - 0: Current node content only, no children preview
            - 1: Node content + immediate children preview (default, recommended)
            - >1: Include deeper levels of hierarchy with nested previews

            Children at the maximum depth level when depth > 0 or the target node when depth=0 are shown in preview form:
            - Content node: Displays content preview (first 80 chars of body text),
              truncated with "... ..." if exceeded. Format: [content] {preview_text}
            - Section node: Displays section title with [section] tag, plus content
              preview if available. Format: [section] {title} [@{node_id}]
              with optional Preview line
        format: Output style - 'markdown' (default), 'text', 'tree', or 'json'.
        include_content: Include node body text (default: True).
        include_see_also: Include cross-reference links (@node_id) (default: True).

    Returns:
        Formatted node content in requested format. For markdown:
        - Node title with label
        - Body content (if include_content=True)
        - Child structure preview (if depth > 0)
        - Cross-references (if include_see_also=True)

    Depth Selection Guide:
        - depth=0: Read only this node's content, no context
        - depth=1: See content + immediate children titles (most useful)
        - depth>1: Deep view for exploring complex structures

    Typical Workflow:
        1. knowledge_roots()  # Find starting point
        2. knowledge_children_preview(node_id="module::root")  # Browse
        3. knowledge_view(node_id="module::section", depth=1)  # Read content

    See Also:
        knowledge_children_preview - Browse child nodes before viewing
        knowledge_search - Find nodes to view
        knowledge_to - Navigate to this node first

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    result = api.get_node_view(
        node_id=node_id,
        depth=depth,
        format=format,
        include_content=include_content,
        include_see_also=include_see_also
    )
    # Directly pass to format_node_view without pre-unpacking
    return format_response.format_node_view(result)


@mcp.tool()
async def knowledge_children(node_id: Optional[str] = None) -> str:
    """
    Get simple list of child node IDs.

    Returns only the IDs of immediate child nodes without additional details.
    For browsing with full context, use knowledge_children_preview instead.

    Args:
        node_id: Parent node ID in 'module::label' format.
            Uses current location if not provided.

    Returns:
        Simple list of child node IDs (e.g., ['module::child1', 'module::child2']).

    Difference from knowledge_children_preview:
        - knowledge_children: Returns ONLY node IDs (lightweight, for scripting)
        - knowledge_children_preview: Returns full preview with titles, types, index

    When to Use:
        - Use this for getting raw IDs for programmatic navigation
        - Use knowledge_children_preview for interactive browsing

    See Also:
        knowledge_children_preview - Get detailed child preview with titles
        knowledge_view - View content of a specific child

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    res = api.get_children(node_id)
    if not res.get("success"):
        return format_response.format_error(f"Failed to get children: {res.get('error')}")
    return format_response.format_children_list(res["data"])


@mcp.tool()
async def knowledge_parent(node_id: Optional[str] = None) -> str:
    """
    Get the parent node of a specified node.

    Returns information about the immediate parent in the hierarchy.
    Use this to navigate "up" the tree or understand context.

    Args:
        node_id: Child node ID in 'module::label' format.
            Uses current location if not provided.

    Returns:
        Parent node details including:
        - Node ID
        - Title
        - Label

    Typical Use Cases:
        - Check context of current node
        - Navigate up one level (consider using knowledge_up instead)

    See Also:
        knowledge_up - Navigate to parent and update current location
        knowledge_breadcrumb - Get full path from root

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    res = api.get_parent(node_id)
    # Use format_node_view to format parent info
    return format_response.format_node_view(res)


@mcp.tool()
async def knowledge_children_preview(
    node_id: Optional[str] = None,
    node_type: str = "all"
) -> str:
    """
    Get detailed preview of child nodes for browsing.

    Returns a formatted list showing title, type, and ID for each child node.
    This is the primary tool for exploring knowledge base structure.

    Args:
        node_id: Parent node ID in 'module::label' format.
            Uses current location if not provided.
        node_type: Filter children by type:
            - 'all': Show all child types (default)
            - 'section': Show only section containers
            - 'content': Show only content nodes

    Returns:
        Formatted preview showing for each child:
        - Index number (use with knowledge_to by index)
        - Node type ([section] or [content])
        - Node title/label
        - Full node ID

    Difference from knowledge_children:
        - knowledge_children_preview: Full preview with titles, types, index
        - knowledge_children: Returns ONLY node IDs (minimal output)

    Typical Workflow:
        1. knowledge_roots()  # Get starting point
        2. knowledge_children_preview(node_id="module::root")  # Browse
        3. knowledge_to(target="1")  # Navigate by index, or use node_id
        4. Repeat step 2-3 to explore deeper

    See Also:
        knowledge_children - Get raw IDs only
        knowledge_to - Navigate using index or ID
        knowledge_view - Read full content

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    res = api.preview_children(node_id, node_type, 'order')
    if not res.get("success"):
        return format_response.format_error(f"Failed to get preview: {res.get('error')}")
    return format_response.format_children_preview(res["data"])


@mcp.tool()
async def knowledge_breadcrumb() -> str:
    """
    Get full navigation path from root to current location.

    Shows the breadcrumb trail representing your current position in the
    knowledge hierarchy. Useful for understanding context and orientation.

    Returns:
        Formatted breadcrumb showing path like:
        ::ROOT > module::root > module::section > module::subsection

    Typical Use Cases:
        - Understand where you are in the knowledge base
        - Get context for the current node
        - Identify path back to root

    See Also:
        knowledge_up - Move up the hierarchy
        knowledge_parent - Get immediate parent only

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    res = api.get_breadcrumb()
    if not res.get("success"):
        return format_response.format_error(f"Failed to get breadcrumb: {res.get('error')}")
    return format_response.format_breadcrumb(res["data"])


# === Navigation Tools ===

@mcp.tool()
async def knowledge_to(target: str) -> str:
    """
    Navigate to a specific node and update current location.

    Moves to the target node and sets it as the current browsing position.
    The target can be specified in multiple ways for flexibility.

    Args:
        target: Target location - can be one of:
            - Full node ID: 'module::label' (e.g., 'docs::intro')
            - Relative ID: '::label' relative to current module
            - Child index: '1', '2', etc. from knowledge_children_preview

    Returns:
        Navigation confirmation with new location:
        - Success/error status
        - New current node ID

    Navigation Methods:
        - Use full ID when you know it: 'module::section'
        - Use index for quick navigation after children_preview
        - Use relative ID within same module

    Typical Workflow:
        1. knowledge_children_preview(node_id="module::section")
        2. knowledge_to(target="3")  # Go to 3rd child
        3. knowledge_view()  # Read content

    See Also:
        knowledge_children_preview - Get child indices for navigation
        knowledge_back - Return to previous location
        knowledge_up - Go to parent

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    return format_response.format_navigation_result(api.navigate_to(target))


@mcp.tool()
async def knowledge_back(steps: int = 1) -> str:
    """
    Go back in browsing history (like browser back button).

    Returns to previous location(s) in the navigation history stack.

    Args:
        steps: Number of steps to go back (default: 1).
            Each step undoes one knowledge_to/knowledge_up/knowledge_down.

    Returns:
        Navigation confirmation showing:
        - New current location
        - How many steps were reversed

    Typical Use Cases:
        - Return after following a reference
        - Undo accidental navigation
        - Quick way to go back multiple steps

    See Also:
        knowledge_forward - Go forward in history (undo back)
        knowledge_to - Navigate to a specific location

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    return format_response.format_navigation_result(api.navigate_back(steps))


@mcp.tool()
async def knowledge_forward(steps: int = 1) -> str:
    """
    Go forward in browsing history (undo knowledge_back).

    Returns to location(s) you previously went back from.

    Args:
        steps: Number of steps to go forward (default: 1).

    Returns:
        Navigation confirmation showing new current location.

    Typical Use Cases:
        - Undo a knowledge_back operation
        - Navigate forward after going back

    See Also:
        knowledge_back - Go back in history

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    return format_response.format_navigation_result(api.navigate_forward(steps))


@mcp.tool()
async def knowledge_up(levels: int = 1) -> str:
    """
    Move up in the hierarchy to parent node(s).

    Navigates toward the root by going up the specified number of levels.

    Args:
        levels: Number of levels to move up (default: 1).
            Use 1 for parent, 2 for grandparent, etc.

    Returns:
        Navigation confirmation with new current location.

    Typical Use Cases:
        - Go up to parent section after reading a subsection
        - Navigate toward root for broader context

    See Also:
        knowledge_parent - Get parent info without changing location
        knowledge_breadcrumb - See full path to root

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    return format_response.format_navigation_result(api.up(levels))


# === System Tools ===

@mcp.tool()
async def knowledge_status() -> str:
    """
    Get system status and knowledge base statistics.

    Shows current session status, loaded modules, path configuration,
    and overall knowledge base metrics.

    Returns:
        Formatted status showing:
        - Session status
        - Number of loaded modules
        - Local and global root paths
        - Total nodes and files

    Typical Use Cases:
        - Verify connection is active
        - Check how many modules are loaded
        - Get overall system health
        - Debug path configuration issues

    See Also:
        knowledge_connect - Establish the session
        knowledge_modules - List loaded modules with details

    Raises:
        RuntimeError: If session not found.
    """
    api = session_manager.get_session(0)
    if not api:
        raise RuntimeError("Session not found")

    res = api.get_status()
    if not res.get("success"):
        return format_response.format_error(f"Failed to get status: {res.get('error')}")
    return format_response.format_status(res["data"])


def main():
    """Entry point"""
    # MCP server is already initialized via command line arguments
    print(f"Transport: {args.transport}")
    mcp.run(args.transport)


if __name__ == "__main__":
    main()
