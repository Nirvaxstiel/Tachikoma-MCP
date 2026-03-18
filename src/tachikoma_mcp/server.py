#!/usr/bin/env python3
"""
Tachikoma MCP Server - Research-Informed Implementation

Implements key findings from recent research:
1. Topology-aware orchestration (AdaptOrch)
2. Graph-based self-healing tool routing
3. Enhanced RLM with hierarchical indexing (LycheeCluster)
4. Verification loops with grounding
5. Skill learning from execution traces
"""

import asyncio
import json
import logging
from typing import Dict, List

from mcp.server.lowlevel import Server
from mcp.types import (
    CallToolRequest,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Resource,
    TextContent,
    Tool,
)
from pydantic.networks import AnyUrl

# Import models
from .models import GraphEdge, GraphNode, SkillOutcome, TopologyPattern

# Import tools
from .tools.analyze_topology import analyze_topology
from .tools.enhanced_rlm_process import enhanced_rlm_process
from .tools.execute_with_verification import execute_with_verification
from .tools.learn_skill_outcome import learn_skill_outcome
from .tools.query_graph_memory import query_graph_memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tachikoma-mcp")

# Global state
skill_outcomes: List[SkillOutcome] = []
graph_nodes: Dict[str, GraphNode] = {}
graph_edges: List[GraphEdge] = []

# Create server instance
server = Server("tachikoma-mcp")


@server.list_resources()
async def handle_list_resources(_: ListResourcesRequest) -> ListResourcesResult:
    """List available resources"""
    return ListResourcesResult(
        resources=[
            Resource(
                uri="tachikoma://topology-patterns",
                name="Topology Patterns",
                description="Available orchestration topology patterns",
                mimeType="application/json",
            ),
            Resource(
                uri="tachikoma://skill-outcomes",
                name="Skill Outcomes",
                description="Historical skill execution outcomes for learning",
                mimeType="application/json",
            ),
            Resource(
                uri="tachikoma://graph-memory",
                name="Graph Memory",
                description="Current state of graph-based memory system",
                mimeType="application/json",
            ),
        ]
    )


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read a specific resource"""
    uri_str = str(uri)
    if uri_str == "tachikoma://topology-patterns":
        topology_patterns = [
            TopologyPattern(
                name="sequential",
                description="Sequential execution of subtasks",
                confidence_threshold=0.8,
                patterns=["multi-step task", "complex workflow", "pipeline"],
            ),
            TopologyPattern(
                name="parallel",
                description="Parallel execution of independent subtasks",
                confidence_threshold=0.75,
                patterns=["explore alternatives", "ensemble", "independent tasks"],
            ),
            TopologyPattern(
                name="hierarchical",
                description="Hierarchical decomposition with local-global reflection",
                confidence_threshold=0.85,
                patterns=["complex system", "multi-level task", "decomposition"],
            ),
            TopologyPattern(
                name="hybrid",
                description="Combination of sequential and parallel patterns",
                confidence_threshold=0.8,
                patterns=["mixed workflow", "conditional processing"],
            ),
        ]
        content = json.dumps(
            {
                "resource": "Topology Patterns",
                "description": "Available orchestration topology patterns",
                "patterns": [p.model_dump() for p in topology_patterns],
            },
            indent=2,
        )
        return content
    elif uri_str == "tachikoma://skill-outcomes":
        content = json.dumps(
            {
                "resource": "Skill Outcomes",
                "description": "Historical skill execution outcomes for learning",
                "outcomes": [
                    {
                        **o.model_dump(),
                        "timestamp": o.timestamp.isoformat()
                        if hasattr(o, "timestamp")
                        else None,
                    }
                    for o in skill_outcomes[-50:]
                ],
            },
            indent=2,
        )
        return content
    elif uri_str == "tachikoma://graph-memory":
        # Ensure timestamps are serialized as strings
        nodes_data = []
        for n in list(graph_nodes.values())[-50:]:
            node_dict = n.model_dump()
            # Handle timestamp in properties if present
            if "timestamp" in node_dict.get("properties", {}):
                node_dict["properties"]["timestamp"] = str(
                    node_dict["properties"]["timestamp"]
                )
            nodes_data.append(node_dict)

        content = json.dumps(
            {
                "resource": "Graph Memory",
                "description": "Current state of graph-based memory system",
                "nodes": nodes_data,
                "edges": [e.model_dump() for e in graph_edges[-50:]],
            },
            indent=2,
        )
        return content
    else:
        raise ValueError(f"Unknown resource: {uri_str}")


@server.list_tools()
async def handle_list_tools(_: ListToolsRequest) -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="analyze_topology",
                description="Analyze task and recommend optimal orchestration topology",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Description of task to analyze",
                        },
                        "context_size": {
                            "type": "integer",
                            "description": "Estimated context size in tokens",
                            "default": 1000,
                        },
                        "complexity_indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Indicators of task complexity",
                            "default": [],
                        },
                    },
                    "required": ["task_description"],
                },
            ),
            Tool(
                name="execute_with_verification",
                description="Execute operations with verification loops and grounding",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation to execute",
                        },
                        "verification_query": {
                            "type": "string",
                            "description": "Query to verify results",
                        },
                        "grounding_data": {
                            "type": "object",
                            "description": "Grounding data for verification",
                        },
                        "max_iterations": {
                            "type": "integer",
                            "description": "Maximum verification iterations",
                            "default": 3,
                        },
                    },
                    "required": ["operation"],
                },
            ),
            Tool(
                name="learn_skill_outcome",
                description="Learn skills from execution traces and outcomes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill",
                        },
                        "task_type": {
                            "type": "string",
                            "description": "Type of task the skill addresses",
                        },
                        "success": {
                            "type": "boolean",
                            "description": "Whether the execution was successful",
                        },
                        "execution_time": {
                            "type": "number",
                            "description": "Time taken to execute",
                        },
                        "error_message": {
                            "type": "string",
                            "description": "Error message if execution failed",
                            "default": "",
                        },
                    },
                    "required": [
                        "skill_name",
                        "task_type",
                        "success",
                        "execution_time",
                    ],
                },
            ),
            Tool(
                name="query_graph_memory",
                description="Query the graph-based memory system",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["similarity", "traversal", "pattern"],
                            "description": "Type of query to perform",
                        },
                        "start_node": {
                            "type": "string",
                            "description": "Starting node ID for traversal queries",
                        },
                        "depth_limit": {
                            "type": "integer",
                            "description": "Maximum traversal depth",
                            "default": 3,
                        },
                        "properties_filter": {
                            "type": "object",
                            "description": "Filter nodes by properties",
                            "default": {},
                        },
                    },
                    "required": ["query_type"],
                },
            ),
            Tool(
                name="enhanced_rlm_process",
                description="Process large context using enhanced RLM with hierarchical indexing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to process (can be very large)",
                        },
                        "query": {
                            "type": "string",
                            "description": "Query or instruction for processing the content",
                        },
                        "use_hierarchical_indexing": {
                            "type": "boolean",
                            "description": "Whether to use LycheeCluster hierarchical indexing",
                            "default": True,
                        },
                        "chunk_strategy": {
                            "type": "string",
                            "enum": ["fixed", "semantic", "adaptive"],
                            "description": "Chunking strategy to use",
                            "default": "semantic",
                        },
                    },
                    "required": ["content", "query"],
                },
            ),
        ]
    )


@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> List[TextContent]:
    """Handle tool calls"""
    name = request.name
    arguments = request.arguments or {}
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    if name == "analyze_topology":
        result = await analyze_topology(arguments)
    elif name == "execute_with_verification":
        result = await execute_with_verification(arguments)
    elif name == "learn_skill_outcome":
        result = await learn_skill_outcome(arguments, skill_outcomes, graph_nodes)
    elif name == "query_graph_memory":
        result = await query_graph_memory(arguments, graph_nodes, graph_edges)
    elif name == "enhanced_rlm_process":
        result = await enhanced_rlm_process(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

    return [TextContent(type="text", text=result)]


async def run():
    """Run MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


class TachikomaMCPServer:
    """Compatibility wrapper for tests"""

    def __init__(self):
        """Initialize with shared state"""
        global skill_outcomes, graph_nodes, graph_edges
        self.skill_outcomes = skill_outcomes
        self.graph_nodes = graph_nodes
        self.graph_edges = graph_edges

    async def handle_list_resources(self, request):
        """List available resources"""
        return await handle_list_resources(request)

    async def handle_read_resource(self, uri: str):
        """Read a specific resource by URI"""
        from pydantic.networks import AnyUrl

        return await handle_read_resource(AnyUrl(uri))

    async def handle_list_tools(self, request):
        """List available tools"""
        return await handle_list_tools(request)

    async def handle_call_tool(self, request):
        """Handle tool calls"""
        return await handle_call_tool(request)


def main(argv=None):
    """Main entry point."""
    import argparse

    from . import __version__

    parser = argparse.ArgumentParser(
        prog="tachikoma-mcp-python",
        description="Run the Tachikoma MCP server.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args(argv)

    asyncio.run(run())


if __name__ == "__main__":
    main()
