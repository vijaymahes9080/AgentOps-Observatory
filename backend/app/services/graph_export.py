"""
AgentOps Observatory - Mermaid & Graphviz DOT Exporter (Phase 5+)
Generates visual diagram code (Mermaid & Graphviz DOT) from agent trace DAGs for inclusion in GitHub PRs and architecture docs.
"""

from typing import Any, Dict, List


class GraphVisualExporter:
    @classmethod
    def export_to_mermaid(cls, nodes: Dict[str, Any], edges: List[Dict[str, str]]) -> str:
        lines = ["graph TD"]

        for node_id, node in nodes.items():
            clean_id = node_id.replace("-", "_")
            label = node.get("name", "Step").replace('"', "'")
            status = node.get("status", "success")

            # Mermaid shape style based on status
            if status == "error" or node.get("has_error"):
                lines.append(f'    {clean_id}["❌ {label}"]:::errorNode')
            elif node.get("is_partial_orphan"):
                lines.append(f'    {clean_id}["⚠️ {label} (Orphan)"]:::orphanNode')
            else:
                lines.append(f'    {clean_id}["✅ {label}"]:::successNode')

        for edge in edges:
            src = edge.get("source", "").replace("-", "_")
            tgt = edge.get("target", "").replace("-", "_")
            rel = edge.get("relation", "")
            if rel == "model_to_tool":
                lines.append(f"    {src} -. calls .-> {tgt}")
            elif rel == "retry":
                lines.append(f"    {src} == retry ==> {tgt}")
            else:
                lines.append(f"    {src} --> {tgt}")

        lines.extend([
            "    classDef successNode fill:#064e3b,stroke:#10b981,color:#ecfdf5;",
            "    classDef errorNode fill:#881337,stroke:#f43f5e,color:#fff1f2;",
            "    classDef orphanNode fill:#7c2d12,stroke:#f59e0b,color:#fffbeb;"
        ])

        return "\n".join(lines)

    @classmethod
    def export_to_dot(cls, nodes: Dict[str, Any], edges: List[Dict[str, str]]) -> str:
        lines = ["digraph AgentTrace {", "    rankdir=TB;", '    node [fontname="Helvetica", shape="box", style="rounded,filled"];']

        for node_id, node in nodes.items():
            label = node.get("name", "Step")
            fill = "#fecdd3" if node.get("has_error") else "#d1fae5"
            lines.append(f'    "{node_id}" [label="{label}", fillcolor="{fill}"];')

        for edge in edges:
            lines.append(f'    "{edge["source"]}" -> "{edge["target"]}";')

        lines.append("}")
        return "\n".join(lines)
