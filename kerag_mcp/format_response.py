from typing import Dict, List, Any

def _format_header(title: str) -> str:
    """Internal helper: format header"""
    return f"\n=== {title} ===\n"

def format_error(error: str) -> str:
    """Format error message"""
    return f"❌ Error: {error}"

def format_connect_response(data: Dict[str, Any]) -> str:
    """Format connection response"""
    lines = [_format_header("Knowledge Base Connected")]
    lines.append(f"Session ID: {data.get('session_id')}")
    lines.append(f"Status: {data.get('status')}")

    config = data.get("config", {})
    if config:
        lines.append("\nConfiguration:")
        if config.get("local_root"):
            lines.append(f"- Local Root: {config['local_root']}")
        if config.get("global_root"):
            lines.append(f"- Global Root: {config['global_root']}")
        if config.get("lang"):
            lines.append(f"- Language: {config['lang']}")

        init_modules = config.get("initialized_modules", [])
        if init_modules:
            lines.append(f"- Initialized Modules: {', '.join(init_modules)}")

    return "\n".join(lines)

def format_modules_list(modules: List[Dict[str, Any]]) -> str:
    """Format modules list (knowledge_modules)"""
    if not modules:
        return "No modules loaded."

    lines = [_format_header(f"Loaded Modules ({len(modules)})")]
    for mod in modules:
        name = mod.get('name', 'Unknown')
        file_count = mod.get('file_count', 0)
        lines.append(f"- {name:<20} ({file_count} files)")

    return "\n".join(lines)

def format_roots_list(roots: List[Dict[str, Any]]) -> str:
    """Format roots list (knowledge_roots)"""
    if not roots:
        return "No root nodes available."

    lines = [_format_header("Knowledge Roots")]
    for root in roots:
        node_id = root.get('id', '')
        title = root.get('title', '')
        lines.append(f"- {title} ({node_id})")

    return "\n".join(lines)

def format_load_result(response: Dict[str, Any]) -> str:
    """Format module load result"""
    if not response.get("success"):
        return format_error(response.get("error", "Unknown error"))

    data = response.get("data", {})
    meta = response.get("metadata", {})

    lines = ["✅ Module Loaded Successfully"]
    lines.append(f"Name: {data.get('name')}")
    lines.append(f"Files: {data.get('file_count')}")
    if meta.get("loaded_nodes"):
        lines.append(f"Nodes Loaded: {meta['loaded_nodes']}")

    return "\n".join(lines)

def format_search_results(response: Dict[str, Any]) -> str:
    """Format search results"""
    if not response.get("success"):
        return format_error(response.get("error", "Search failed"))

    results = response.get("data", [])
    meta = response.get("metadata", {})

    count = len(results)
    total = meta.get("total", count)
    query = meta.get("query", "")

    lines = [_format_header(f"Search Results for '{query}'")]
    lines.append(f"Showing {count} of {total} matches\n")

    if not results:
        lines.append("No matches found.")
        return "\n".join(lines)

    for i, res in enumerate(results, 1):
        node_id = res.get('id') or res.get('node_id')
        node_type = res.get('type', 'unknown')

        # 1. Header Line (Section vs Content)
        if node_type == 'section':
            title = res.get('title') or res.get('label') or "Untitled Section"
            lines.append(f"{i}. [{node_type}] {title} [@{node_id}]")
        else:
            lines.append(f"{i}. [{node_type}] [@{node_id}]")

        # 2. Parent Info (if available)
        parent = res.get('parent')
        if parent:
            p_title = parent.get('title') or parent.get('label') or "Untitled"
            p_id = parent.get('node_id')
            lines.append(f"   Parent: {p_title} [@{p_id}]")

        # 3. Match Context / Excerpt (only for non-section nodes)
        if node_type != 'section':
            excerpt = res.get('excerpt') or res.get('match_context') or res.get('content_preview')
            if excerpt:
                # Clean up newlines for display
                excerpt = excerpt.replace('\n', ' ').strip()
                lines.append(f"   > {excerpt}")

        lines.append("")

    return "\n".join(lines)

def format_node_info(node: Dict[str, Any]) -> str:
    """Format raw node information (from explorer or manual dict)"""
    lines = []
    node_id = node.get("id") or node.get("node_id")
    node_type = node.get("type") or node.get("node_type")
    title = node.get("title") or node.get("label") or "Untitled"

    if node_type == 'section':
        lines.append(f"[{node_type}] {title} [@{node_id}]")
        # 新增: 显示section的content_preview（如果有）
        content_preview = node.get("content_preview")
        if content_preview:
            lines.append(f"\nPreview: {content_preview}")
        # Handle children preview (if any)
        children = node.get("children_preview") or node.get("children", [])
        if children:
            lines.append("\nChildren:")
            if isinstance(children, dict):
                # If it's the recursive dict format from explorer
                for label, child in sorted(children.items()):
                    c_title = child.get('title') or child.get('label') or label
                    c_id = child.get('node_id') or child.get('id')
                    lines.append(f"- {c_title} [@{c_id}]")
            else:
                # If it's a list (preview format)
                for child in children:
                    c_title = child.get('title') or child.get('label') or "Untitled"
                    c_id = child.get('node_id') or child.get('id')
                    lines.append(f"- {c_title} [@{c_id}]")
    else:
        lines.append(f"[{node_type}]")
        content = node.get("content") or node.get("content_preview") or ""
        lines.append(content)
        lines.append(f"[@{node_id}]")

    return "\n".join(lines)

def format_navigation_result(response: Dict[str, Any]) -> str:
    """Format result of navigation operations (to, back, forward, up)"""
    if not response.get("success"):
        # Handle special case: Ambiguous target
        if response.get("error") == "Ambiguous target":
            candidates = response.get("metadata", {}).get("candidates", [])
            lines = ["⚠️ Ambiguous Target. Did you mean one of these?"]
            for c in candidates:
                lines.append(f"- {c}")
            return "\n".join(lines)
        return format_error(response.get("error", "Navigation failed"))

    data = response.get("data", {})
    meta = response.get("metadata", {})

    # 1. Breadcrumb
    breadcrumb = meta.get("breadcrumb")
    header = ""
    if breadcrumb:
        header = f"📍 {format_breadcrumb(breadcrumb)}\n"

    # 2. Special case: already_at_target
    if isinstance(data, dict) and data.get("already_at_target"):
        return f"{header}\n(Already at target node: {meta.get('node_id')})".strip()

    # 3. Node Info
    node_text = format_node_info(data)

    return f"{header}\n{node_text}".strip()

def format_node_view(response: Dict[str, Any]) -> str:
    """Format full node view (usually with formatted content from api.get_node_view)"""
    if not response.get("success"):
        return format_error(response.get("error", "Failed to view node"))

    data = response.get("data", {})
    # Check for formatted_content (from KERAGAPI.get_node_view)
    formatted = data.get("formatted_content", {})
    if "markdown" in formatted:
        return formatted["markdown"]
    elif "text" in formatted:
        return formatted["text"]
    elif "tree" in formatted:
        return formatted["tree"]

    # Fallback to node info if no formatted content (or if data is the node)
    node = data.get("node", data)
    return format_node_info(node)

def format_children_list(children: List[str]) -> str:
    """Format children node ID list"""
    if not children:
        return "No children."

    lines = [_format_header(f"Children Nodes ({len(children)})")]
    for child_id in children:
        lines.append(f"- {child_id}")
    return "\n".join(lines)

def format_children_preview(children: List[Dict[str, Any]]) -> str:
    """Format children preview info"""
    if not children:
        return "No children."

    lines = [_format_header(f"Children Preview ({len(children)})")]
    for i, child in enumerate(children, 1):
        node_id = child.get("id") or child.get("node_id")
        kind = child.get("type", "unknown")

        # Determine main title to display
        if kind == 'section':
            title = child.get("title") or child.get("label") or "Untitled Section"
            lines.append(f"{i}. [section] {title} [@{node_id}]")
            # 新增: 显示section的内容预览（如果有）
            content_preview = child.get("content_preview")
            if content_preview:
                preview_text = content_preview
                if len(preview_text) > 80:
                    preview_text = preview_text[:77] + " ... ... "
                lines.append(f"    Preview: {preview_text}")
        else:
            # For content type, prioritize content_preview
            main_text = child.get("content_preview") or child.get("label") or "Untitled Content"

            # Limit title length to avoid being too long
            if len(main_text) > 80:
                main_text = main_text[:77] + " ... ... "

            lines.append(f"{i}. [{kind}] {main_text}")
            lines.append(f"   [@{node_id}]")

    return "\n".join(lines)

def format_breadcrumb(breadcrumb: List[Dict[str, Any]]) -> str:
    """Format breadcrumb"""
    if not breadcrumb:
        return ""

    path_strs = []
    for item in breadcrumb:
        path_strs.append(item.get("title", item.get("id")))

    return " > ".join(path_strs)

def format_status(status: Dict[str, Any]) -> str:
    """Format system status"""
    lines = [_format_header("System Status")]

    # Basic statistics
    lines.append("Statistics:")
    lines.append(f"- Total Nodes: {status.get('total_nodes', 0)}")
    lines.append(f"- Loaded Modules: {status.get('loaded_modules', 0)}")
    lines.append(f"- Available Modules: {status.get('available_modules', 0)}")

    # Path config
    lines.append("\nConfiguration:")
    lines.append(f"- Local Root: {status.get('local_root', 'N/A')}")
    lines.append(f"- Global Root: {status.get('global_root', 'N/A')}")
    lines.append(f"- Language: {status.get('lang', 'N/A')}")

    # Current location
    curr = status.get("current_node")
    if curr:
        lines.append(f"\nCurrent Location: {curr}")

    return "\n".join(lines)
