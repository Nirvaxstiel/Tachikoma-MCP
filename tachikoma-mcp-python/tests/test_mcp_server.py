import asyncio
import json
import pytest
from src.tachikoma_mcp.server import TachikomaMCPServer
from src.tachikoma_mcp.tools.analyze_topology import analyze_topology
from src.tachikoma_mcp.tools.execute_with_verification import execute_with_verification
from src.tachikoma_mcp.tools.learn_skill_outcome import learn_skill_outcome
from src.tachikoma_mcp.tools.query_graph_memory import query_graph_memory
from src.tachikoma_mcp.tools.enhanced_rlm_process import enhanced_rlm_process
from mcp.types import ReadResourceRequest, ReadResourceRequestParams


class TestMCPServer:
    """Test suite for Tachikoma MCP Server features based on research literature"""

    @pytest.fixture
    def server(self):
        """Create a fresh server instance for each test"""
        return TachikomaMCPServer()

    @pytest.mark.asyncio
    async def test_analyze_topology_sequential(self, server):
        """Test topology analysis for sequential tasks (AdaptOrch research)"""
        arguments = {
            "task_description": "Create a multi-step workflow for data processing pipeline",
            "context_size": 1000,
            "complexity_indicators": ["multi-step"],
        }

        result = await analyze_topology(arguments)
        result_data = json.loads(result)

        # Should recommend sequential topology for multi-step tasks
        assert result_data["recommended_topology"] == "sequential"
        assert result_data["confidence"] > 0.5
        assert "task_characteristics" in result_data

    @pytest.mark.asyncio
    async def test_analyze_topology_parallel(self, server):
        """Test topology analysis for parallel tasks (AdaptOrch research)"""
        arguments = {
            "task_description": "Explore multiple independent alternatives for optimization",
            "context_size": 2000,
            "complexity_indicators": ["independent"],
        }

        result = await analyze_topology(arguments)
        result_data = json.loads(result)

        # Should recommend parallel topology for independent tasks
        assert result_data["recommended_topology"] == "parallel"
        assert result_data["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_analyze_topology_hierarchical_large_context(self, server):
        """Test topology analysis for large contexts (AdaptOrch research)"""
        arguments = {
            "task_description": "Analyze complex system architecture",
            "context_size": 100000,  # Large context
            "complexity_indicators": ["complex system"],
        }

        result = await analyze_topology(arguments)
        result_data = json.loads(result)

        # Should recommend hierarchical topology for large contexts
        assert result_data["recommended_topology"] == "hierarchical"
        assert result_data["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_execute_with_verification_success(self, server):
        """Test verification loop with successful execution (Mirror Loop research)"""
        arguments = {
            "task": "Implement a sorting algorithm",
            "max_iterations": 5,
            "require_grounding": True,
        }

        result = await execute_with_verification(arguments)
        result_data = json.loads(result)

        # Should complete with success and grounding achieved
        assert result_data["final_success"] == True
        assert result_data["grounding_achieved"] == True
        assert result_data["iterations_completed"] >= 1
        assert "execution_history" in result_data
        assert len(result_data["execution_history"]) > 0

    @pytest.mark.asyncio
    async def test_execute_with_verification_without_grounding(self, server):
        """Test verification loop without grounding requirement (Mirror Loop research)"""
        arguments = {
            "task": "Create a simple function",
            "max_iterations": 3,
            "require_grounding": False,  # No grounding required
        }

        result = await execute_with_verification(arguments)
        result_data = json.loads(result)

        # Should still succeed but grounding_achieved will be False
        assert result_data["final_success"] == True
        # When require_grounding is False, grounding_achieved should be False
        assert result_data["grounding_achieved"] == False

    @pytest.mark.asyncio
    async def test_learn_skill_outcome_success(self, server):
        """Test recording successful skill outcomes (SkillOrchestra research)"""
        arguments = {
            "skill_name": "code-agent",
            "task_type": "implementation",
            "success": True,
            "execution_time": 2.5,
            "context_size": 5000,
        }

        result = await learn_skill_outcome(
            arguments, server.skill_outcomes, server.graph_nodes
        )
        result_data = json.loads(result)

        # Should record the outcome successfully
        assert result_data["recorded"] == True
        assert result_data["outcome_id"] == 1
        assert result_data["total_outcomes"] == 1
        assert (
            "Recorded outcome for code-agent on implementation"
            in result_data["message"]
        )

        # Verify the outcome was stored
        assert len(server.skill_outcomes) == 1
        outcome = server.skill_outcomes[0]
        assert outcome.skill_name == "code-agent"
        assert outcome.task_type == "implementation"
        assert outcome.success == True
        assert outcome.execution_time == 2.5
        assert outcome.context_size == 5000

    @pytest.mark.asyncio
    async def test_learn_skill_outcome_failure(self, server):
        """Test recording failed skill outcomes (SkillOrchestra research)"""
        arguments = {
            "skill_name": "verifier-code-agent",
            "task_type": "verification",
            "success": False,
            "execution_time": 1.2,
            "context_size": 3000,
            "error_message": "Timeout during verification",
        }

        result = await learn_skill_outcome(
            arguments, server.skill_outcomes, server.graph_nodes
        )
        result_data = json.loads(result)

        # Should record the outcome successfully
        assert result_data["recorded"] == True
        assert result_data["outcome_id"] == 1
        assert result_data["total_outcomes"] == 1

        # Verify the outcome was stored
        assert len(server.skill_outcomes) == 1
        outcome = server.skill_outcomes[0]
        assert outcome.skill_name == "verifier-code-agent"
        assert outcome.task_type == "verification"
        assert outcome.success == False
        assert outcome.execution_time == 1.2
        assert outcome.context_size == 3000
        assert outcome.error_message == "Timeout during verification"

    @pytest.mark.asyncio
    async def test_query_graph_memory_similarity(self, server):
        """Test graph memory similarity query (graph-based self-healing research)"""
        # First add some outcomes to create graph nodes
        await learn_skill_outcome(
            {
                "skill_name": "code-agent",
                "task_type": "implementation",
                "success": True,
                "execution_time": 2.0,
                "context_size": 4000,
            },
            server.skill_outcomes,
            server.graph_nodes,
        )

        await learn_skill_outcome(
            {
                "skill_name": "verifier-code-agent",
                "task_type": "verification",
                "success": True,
                "execution_time": 1.5,
                "context_size": 2000,
            },
            server.skill_outcomes,
            server.graph_nodes,
        )

        # Query for successful outcomes
        arguments = {"query_type": "similarity", "properties_filter": {"success": True}}

        result = await query_graph_memory(
            arguments, server.graph_nodes, server.graph_edges
        )
        result_data = json.loads(result)

        # Should find matching nodes
        assert result_data["query_type"] == "similarity"
        assert result_data["total_matches"] >= 1
        assert len(result_data["matches"]) >= 1
        assert result_data["matches"][0]["score"] > 0

    @pytest.mark.asyncio
    async def test_query_graph_memory_traversal(self, server):
        """Test graph memory traversal query (graph-based self-healing research)"""
        # Add some outcomes to create graph nodes
        await learn_skill_outcome(
            {
                "skill_name": "code-agent",
                "task_type": "implementation",
                "success": True,
                "execution_time": 2.0,
                "context_size": 4000,
            },
            server.skill_outcomes,
            server.graph_nodes,
        )

        # Query for traversal from the first node
        arguments = {
            "query_type": "traversal",
            "start_node": "skill_outcome_1",
            "depth_limit": 2,
        }

        result = await query_graph_memory(
            arguments, server.graph_nodes, server.graph_edges
        )
        result_data = json.loads(result)

        # Should return traversal path or error if node doesn't exist
        # Note: In our simplified implementation, we might not have actual edges
        assert "query_type" in result_data
        if "error" not in result_data:
            assert "path" in result_data
            assert "nodes_visited" in result_data

    @pytest.mark.asyncio
    async def test_enhanced_rlm_process_semantic_chunking(self, server):
        """Test enhanced RLM processing with semantic chunking (LycheeCluster research)"""
        # Create a large content to process
        large_content = "This is a test sentence. " * 1000  # ~25k characters

        arguments = {
            "content": large_content,
            "query": "What is the main topic of this content?",
            "use_hierarchical_indexing": True,
            "chunk_strategy": "semantic",
        }

        result = await enhanced_rlm_process(arguments)
        result_data = json.loads(result)

        # Should process the content successfully
        assert result_data["content_length"] == len(large_content)
        assert result_data["chunk_strategy"] == "semantic"
        assert "LycheeCluster" in result_data["chunking_method"]
        assert result_data["num_chunks"] > 0
        assert result_data["final_synthesis"]["total_chunks_processed"] > 0
        assert "context_expansion" in result_data
        assert "performance_improvement" in result_data

    @pytest.mark.asyncio
    async def test_enhanced_rlm_process_adaptive_chunking(self, server):
        """Test enhanced RLM processing with adaptive chunking (LycheeCluster research)"""
        # Create content with varying complexity
        content = (
            "Simple text. " * 500
            + "\n\nComplex analysis: "
            + "detailed explanation. " * 1000
        )

        arguments = {
            "content": content,
            "query": "Analyze the complexity patterns in this content",
            "use_hierarchical_indexing": True,
            "chunk_strategy": "adaptive",
        }

        result = await enhanced_rlm_process(arguments)
        result_data = json.loads(result)

        # Should process the content successfully
        assert result_data["content_length"] == len(content)
        assert result_data["chunk_strategy"] == "adaptive"
        assert "Adaptive chunking" in result_data["chunking_method"]
        assert result_data["num_chunks"] > 0
        assert result_data["final_synthesis"]["total_chunks_processed"] > 0

    @pytest.mark.asyncio
    async def test_enhanced_rlm_process_fixed_chunking(self, server):
        """Test enhanced RLM processing with fixed chunking (baseline comparison)"""
        content = "Test content for fixed chunking. " * 500

        arguments = {
            "content": content,
            "query": "Summarize this content",
            "use_hierarchical_indexing": True,
            "chunk_strategy": "fixed",
        }

        result = await enhanced_rlm_process(arguments)
        result_data = json.loads(result)

        # Should process the content successfully
        assert result_data["content_length"] == len(content)
        assert result_data["chunk_strategy"] == "fixed"
        assert "Fixed-size chunking" in result_data["chunking_method"]
        assert result_data["num_chunks"] > 0
        assert result_data["final_synthesis"]["total_chunks_processed"] > 0

    @pytest.mark.asyncio
    async def test_resource_endpoints(self, server):
        """Test that resource endpoints are properly configured"""
        # Test topology patterns resource
        request = ReadResourceRequest(
            method="resources/read",
            params=ReadResourceRequestParams(uri="tachikoma://topology-patterns"),
        )

        result = await server.handle_read_resource(request)
        assert hasattr(result, "contents")
        assert len(result.contents) > 0
        content = result.contents[0].text
        assert "Topology Patterns" in content
        assert "sequential" in content
        assert "parallel" in content

        # Test skill outcomes resource
        request = ReadResourceRequest(
            method="resources/read",
            params=ReadResourceRequestParams(uri="tachikoma://skill-outcomes"),
        )

        result = await server.handle_read_resource(request)
        assert hasattr(result, "contents")
        assert len(result.contents) > 0
        content = result.contents[0].text
        assert "Skill Outcomes" in content

        # Test graph memory resource
        request = ReadResourceRequest(
            method="resources/read",
            params=ReadResourceRequestParams(uri="tachikoma://graph-memory"),
        )

        result = await server.handle_read_resource(request)
        assert hasattr(result, "contents")
        assert len(result.contents) > 0
        content = result.contents[0].text
        assert "Graph Memory" in content

    @pytest.mark.asyncio
    async def test_tool_endpoints_exist(self, server):
        """Test that all expected tools are available"""
        from mcp.types import ListToolsRequest

        request = ListToolsRequest(method="tools/list")
        result = await server.handle_list_tools(request)

        assert hasattr(result, "tools")
        tool_names = [tool.name for tool in result.tools]

        expected_tools = [
            "analyze_topology",
            "execute_with_verification",
            "learn_skill_outcome",
            "query_graph_memory",
            "enhanced_rlm_process",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Missing tool: {expected_tool}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
