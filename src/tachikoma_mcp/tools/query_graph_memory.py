"""Query the graph-based memory system tool."""

import json
from typing import Any, Dict


async def query_graph_memory(
    arguments: Dict[str, Any],
    graph_nodes: dict,
    graph_edges: list,
) -> str:
    """Query the graph-based memory system."""
    query_type = arguments.get("query_type", "")
    start_node = arguments.get("start_node")
    depth_limit = arguments.get("depth_limit", 3)
    properties_filter = arguments.get("properties_filter", {})

    if query_type == "similarity":
        # Simple similarity search based on properties
        matches = []
        for node_id, node in graph_nodes.items():
            match_score = 0
            for key, value in properties_filter.items():
                if key in node.properties and node.properties[key] == value:
                    match_score += 1
            if match_score > 0:
                matches.append(
                    {
                        "node": node.model_dump(),
                        "score": match_score / len(properties_filter)
                        if properties_filter
                        else 1.0,
                    }
                )

        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)
        result = {
            "query_type": "similarity",
            "filters": properties_filter,
            "matches": matches[:10],  # Top 10 matches
            "total_matches": len(matches),
        }

    elif query_type == "traversal" and start_node:
        # Simple traversal (breadth-first)
        if start_node not in graph_nodes:
            result = {
                "error": f"Start node {start_node} not found",
                "available_nodes": list(graph_nodes.keys()),
            }
        else:
            visited = set()
            queue = [(start_node, 0)]  # (node_id, depth)
            traversal_path = []

            while queue and len(traversal_path) < 50:  # Limit results
                node_id, depth = queue.pop(0)
                if node_id in visited or depth > depth_limit:
                    continue

                visited.add(node_id)
                node = graph_nodes[node_id]
                traversal_path.append(
                    {"node_id": node_id, "node": node.model_dump(), "depth": depth}
                )

                # Add neighbors (simplified - in real implementation would use edges)
                # For demo, just add a few connected nodes
                if depth < depth_limit:
                    # Add some connected nodes based on simple heuristics
                    for neighbor_id, neighbor in list(graph_nodes.items())[:3]:
                        if neighbor_id not in visited and neighbor_id != node_id:
                            queue.append((neighbor_id, depth + 1))

            result = {
                "query_type": "traversal",
                "start_node": start_node,
                "depth_limit": depth_limit,
                "path": traversal_path,
                "nodes_visited": len(visited),
            }
    else:
        # Return general graph stats
        result = {
            "query_type": "stats",
            "total_nodes": len(graph_nodes),
            "total_edges": len(graph_edges),
            "node_types": {},
            "recent_nodes": [
                node.model_dump() for node in list(graph_nodes.values())[-5:]
            ],
        }

        # Count node types
        for node in graph_nodes.values():
            node_type = node.type
            result["node_types"][node_type] = result["node_types"].get(node_type, 0) + 1

    return json.dumps(result, indent=2)
