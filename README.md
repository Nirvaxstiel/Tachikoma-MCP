# Tachikoma MCP Server

MCP server with 5 tools for AI agent orchestration.

## Overview

Implements tools for:

- Topology-aware orchestration
- Verification loops with grounding
- Skill learning from execution traces
- Graph-based self-healing tool routing
- Enhanced RLM with hierarchical indexing

Designed to work with [Tachikoma-Agent-Skills](https://github.com/Nirvaxstiel/Tachikoma-Agent-Skills) agent.

## Features

### analyze_topology

Recommends orchestration patterns (sequential/parallel/hierarchical/hybrid) for task routing.

### execute_with_verification

Executes tasks with iterative verification and external grounding.

### learn_skill_outcome

Records skill execution results for continuous improvement.

### query_graph_memory

Queries graph-based memory for intelligent tool selection.

### enhanced_rlm_process

Processes large contexts with semantic/adaptive/fixed chunking.

## Research Documents

- [AdaptOrch: Topology-aware orchestration](https://arxiv.org/abs/2406.16008)
- [Mirror Loop: Verification loops with external grounding](https://arxiv.org/abs/2512.24601)
- [SkillOrchestra: Learning from execution traces](https://arxiv.org/abs/2601.02663)
- [Graph-based Self-healing: Dynamic tool routing](https://arxiv.org/abs/2602.03279)
- [LycheeCluster: Hierarchical indexing for RLM](https://arxiv.org/abs/2602.03837)
- [Additional research](https://arxiv.org/abs/2602.10177)
- [Additional research](https://arxiv.org/abs/2602.16891)
- [Additional research](https://arxiv.org/abs/2603.10123)

## Architecture

Modular Python implementation:

```
tachikoma-mcp-python/
├── src/tachikoma_mcp/
│   ├── server.py
│   ├── models.py
│   └── tools/
├── tests/
├── pyproject.toml
└── run_server.py
```

## Installation

Requires Python 3.14+ and uv:

```bash
git clone <repo-url>
cd tachikoma-mcp-python
uv sync
```

## Usage

Run server:

```bash
python run_server.py
# or
python -m tachikoma_mcp.server
```

## MCP Registration

Add to agent's MCP config:

```json
{
  "mcpServers": [
    {
      "command": "cd /path/to/tachikoma-mcp-python && python run_server.py",
      "name": "tachikoma-mcp",
      "description": "MCP server for agent orchestration"
    }
  ]
}
```

## Development

Run tests: `pytest tests/ -v`

Code style: Direct, minimal comments, single-word variables when clear.

## License

MIT
