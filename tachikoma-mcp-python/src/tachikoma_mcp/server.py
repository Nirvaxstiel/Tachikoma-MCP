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
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server.lowlevel import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    CallToolRequest,
    CallToolResult,
    ReadResourceRequest,
    ReadResourceResult,
    TextResourceContents,
    ServerCapabilities,
    ToolsCapability,
)
from pydantic.networks import AnyUrl

# Import models
from .models import TopologyPattern, SkillOutcome, GraphNode, GraphEdge

# Import tools
from .tools.analyze_topology import analyze_topology
from .tools.execute_with_verification import execute_with_verification
from .tools.learn_skill_outcome import learn_skill_outcome
from .tools.query_graph_memory import query_graph_memory
from .tools.enhanced_rlm_process import enhanced_rlm_process

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tachikoma-mcp")


class TachikomaMCPServer:
    def __init__(self):
        self.server = Server("tachikoma-mcp")
        self.skill_outcomes: List[SkillOutcome] = []
        self.graph_nodes: Dict[str, GraphNode] = {}
        self.graph_edges: List[GraphEdge] = []

    # Handler methods for testing
    async def handle_list_resources(
        self, _: ListResourcesRequest
    ) -> ListResourcesResult:
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

    async def handle_read_resource(
        self, request: ReadResourceRequest
    ) -> ReadResourceResult:
        """Read a specific resource"""
        uri_str = str(request.params.uri)
        if uri_str == "tachikoma://topology-patterns":
            # Initialize topology patterns for the resource
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
                    "patterns": [pattern.dict() for pattern in topology_patterns],
                },
                indent=2,
            )
            return ReadResourceResult(
                contents=[
                    TextResourceContents(
                        uri=AnyUrl(uri_str), mimeType="application/json", text=content
                    )
                ]
            )
        elif uri_str == "tachikoma://skill-outcomes":
            content = json.dumps(
                {
                    "resource": "Skill Outcomes",
                    "description": "Historical skill execution outcomes for learning",
                    "outcomes": [
                        outcome.dict() for outcome in self.skill_outcomes[-50:]
                    ],
                },
                indent=2,
            )  # Last 50
            return ReadResourceResult(
                contents=[
                    TextResourceContents(
                        uri=AnyUrl(uri_str), mimeType="application/json", text=content
                    )
                ]
            )
        elif uri_str == "tachikoma://graph-memory":
            content = json.dumps(
                {
                    "resource": "Graph Memory",
                    "description": "Current state of graph-based memory system",
                    "state": {
                        "nodes": [node.dict() for node in self.graph_nodes.values()],
                        "edges": [edge.dict() for edge in self.graph_edges],
                    },
                },
                indent=2,
            )
            return ReadResourceResult(
                contents=[
                    TextResourceContents(
                        uri=AnyUrl(uri_str), mimeType="application/json", text=content
                    )
                ]
            )
        else:
            raise ValueError(f"Unknown resource: {uri_str}")

    async def handle_list_tools(self, _: ListToolsRequest) -> ListToolsResult:
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
                                "description": "Description of the task to analyze",
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
                    description="Execute a task with verification loops and grounding",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Task to execute",
                            },
                            "max_iterations": {
                                "type": "integer",
                                "description": "Maximum verification iterations",
                                "default": 3,
                            },
                            "require_grounding": {
                                "type": "boolean",
                                "description": "Whether to require grounding in verification",
                                "default": True,
                            },
                        },
                        "required": ["task"],
                    },
                ),
                Tool(
                    name="learn_skill_outcome",
                    description="Record skill execution outcome for future learning",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "Name of the skill executed",
                            },
                            "task_type": {
                                "type": "string",
                                "description": "Type of task the skill was applied to",
                            },
                            "success": {
                                "type": "boolean",
                                "description": "Whether the skill execution was successful",
                            },
                            "execution_time": {
                                "type": "number",
                                "description": "Execution time in seconds",
                            },
                            "context_size": {
                                "type": "integer",
                                "description": "Size of context processed",
                                "default": 0,
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

    async def handle_call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls"""
        name = request.name
        arguments = request.arguments or {}
        logger.info(f"Calling tool: {name} with arguments: {arguments}")

        if name == "analyze_topology":
            result = await analyze_topology(arguments)
        elif name == "execute_with_verification":
            result = await execute_with_verification(arguments)
        elif name == "learn_skill_outcome":
            result = await learn_skill_outcome(
                arguments, self.skill_outcomes, self.graph_nodes
            )
        elif name == "query_graph_memory":
            result = await query_graph_memory(
                arguments, self.graph_nodes, self.graph_edges
            )
        elif name == "enhanced_rlm_process":
            result = await enhanced_rlm_process(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return CallToolResult(content=[TextContent(type="text", text=result)])

    async def run(self):
        """Run MCP server"""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main():
    """Main entry point"""
    server = TachikomaMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
