# Tachikoma MCP Server

Research-informed MCP (Model Context Protocol) server implementation for AI coding agents.

## Overview

This MCP server implements key findings from recent research on multi-agent orchestration, tool routing, and context management. It provides 5 high-value tools based on research literature from January-March 2026.

## Features

### 1. Topology-aware Orchestration (AdaptOrch Research)
Analyzes tasks and recommends optimal orchestration topology patterns:
- **Sequential**: For multi-step workflows and pipelines
- **Parallel**: For exploring independent alternatives and ensemble tasks
- **Hierarchical**: For complex systems with large contexts requiring multi-level decomposition
- **Hybrid**: For mixed workflows with conditional processing

### 2. Verification Loops with Grounding (Mirror Loop Research)
Executes tasks with iterative verification and grounding in external validation:
- Configurable max iterations
- Optional grounding requirement
- Tracks execution history with confidence progression
- Supports both generation and verification phases

### 3. Skill Learning from Execution Traces (SkillOrchestra Research)
Records skill execution outcomes for continuous improvement:
- Tracks success/failure rates
- Monitors execution time and context size
- Captures error messages for debugging
- Enables data-driven skill selection

### 4. Graph-based Self-healing Tool Routing
Maintains a graph-based memory system for intelligent tool routing:
- Supports similarity queries by properties
- Supports traversal queries through graph structure
- Enables pattern-based matching
- Adapts routing based on historical performance

### 5. Enhanced RLM with Hierarchical Indexing (LycheeCluster Research)
Processes large contexts using advanced chunking strategies:
- **Semantic chunking**: LycheeCluster boundary-aware chunking for 3.6x speedup
- **Adaptive chunking**: Triangle inequality indexing for complex content
- **Fixed chunking**: Baseline comparison approach
- Provides context expansion beyond standard limits

## Architecture

The implementation follows a modular pattern inspired by [jcodemunch-mcp](https://github.com/jgravelle/jcodemunch-mcp):

```
tachikoma-mcp-python/
├── src/
│   └── tachikoma_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP server setup and orchestration
│       ├── models.py              # Pydantic data models
│       └── tools/                # Modular tool implementations
│           ├── analyze_topology.py
│           ├── execute_with_verification.py
│           ├── learn_skill_outcome.py
│           ├── query_graph_memory.py
│           └── enhanced_rlm_process.py
├── tests/
│   └── test_mcp_server.py   # Comprehensive test suite
├── pyproject.toml              # Project dependencies
└── run_server.py              # Entry point for execution
```

## Installation

### Prerequisites
- Python 3.14+
- uv package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd tachikoma-mcp-python

# Install dependencies
uv sync

# Run tests (optional)
uv run pytest tests/
```

## Usage

### Running the Server

```bash
# Run MCP server over stdio (default)
python run_server.py

# Or directly with python
python -m tachikoma_mcp.server
```

### MCP Tools

All tools return JSON-formatted results with detailed information:

1. **analyze_topology**
   - Input: task_description, context_size, complexity_indicators
   - Output: Recommended topology with confidence scores
   - Use Case: Analyze incoming tasks before routing to agents

2. **execute_with_verification**
   - Input: task, max_iterations, require_grounding
   - Output: Execution history with verification results
   - Use Case: Execute critical tasks with validation

3. **learn_skill_outcome**
   - Input: skill_name, task_type, success, execution_time, context_size, error_message
   - Output: Confirmation with outcome ID
   - Use Case: After any skill execution for continuous learning

4. **query_graph_memory**
   - Input: query_type, start_node, depth_limit, properties_filter
   - Output: Matching nodes, traversal paths, or graph statistics
   - Use Case: Select best tools based on historical performance

5. **enhanced_rlm_process**
   - Input: content, query, use_hierarchical_indexing, chunk_strategy
   - Output: Chunks, synthesis, and performance metrics
   - Use Case: Process large codebases or documentation

## MCP Resources

The server provides 3 resources for accessing internal state:

1. **tachikoma://topology-patterns** - Available orchestration patterns
2. **tachikoma://skill-outcomes** - Historical skill execution outcomes (last 50)
3. **tachikoma://graph-memory** - Current graph nodes and edges

## Testing

Run the comprehensive test suite:

```bash
cd tachikoma-mcp-python
pytest tests/ -v
```

All 14 tests pass, covering:
- Topology analysis for sequential, parallel, and hierarchical tasks
- Verification loops with and without grounding
- Skill outcome recording for success and failure
- Graph memory similarity and traversal queries
- Enhanced RLM with semantic, adaptive, and fixed chunking
- Resource and tool endpoint availability

## Registering with Coding Agents

To register this MCP server with an agent (like opencode), add to the agent's MCP configuration:

```json
{
  "mcpServers": [
    {
      "command": "cd /path/to/tachikoma-mcp-python && python run_server.py",
      "name": "tachikoma-mcp",
      "description": "Research-informed MCP server with topology-aware orchestration, verification loops, skill learning, graph-based routing, and enhanced RLM"
    }
  ]
}
```

Or using uv directly:

```json
{
  "mcpServers": [
    {
      "command": "cd /path/to/tachikoma-mcp-python && .venv/bin/python -m tachikoma_mcp.server",
      "name": "tachikoma-mcp",
      "description": "Research-informed MCP server with topology-aware orchestration, verification loops, skill learning, graph-based routing, and enhanced RLM"
    }
  ]
}
```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Style
- Use existing naming patterns
- Keep functions focused and small
- Handle errors explicitly
- Prefer single word variable names
- Use type inference

## Research References

This implementation is based on findings from recent research papers:

- **AdaptOrch**: Topology-aware orchestration for multi-agent systems
- **Mirror Loop**: Verification loops with external grounding
- **SkillOrchestra**: Learning from execution traces for skill composition
- **Graph-based Self-healing**: Dynamic tool routing using performance graphs
- **LycheeCluster**: Hierarchical indexing for RLM with 3.6x speedup

## License

MIT

## Contributing

Contributions welcome! Please ensure:
1. All tests pass
2. Code follows existing patterns
3. Features align with research findings
4. Documentation is updated for any changes
