"""Record skill execution outcome for future learning tool."""

from typing import Any, Dict
import json
from datetime import datetime

from ..models import SkillOutcome, GraphNode


async def learn_skill_outcome(
    arguments: Dict[str, Any],
    skill_outcomes: list,
    graph_nodes: dict,
) -> str:
    """Record skill execution outcome for future learning."""
    outcome = SkillOutcome(
        skill_name=arguments.get("skill_name", ""),
        task_type=arguments.get("task_type", ""),
        success=arguments.get("success", False),
        execution_time=arguments.get("execution_time", 0.0),
        timestamp=datetime.now(),
        context_size=arguments.get("context_size", 0),
        error_message=arguments.get("error_message", None)
        if arguments.get("error_message")
        else None,
    )

    skill_outcomes.append(outcome)

    # Also add to graph memory as a node
    node_id = f"skill_outcome_{len(skill_outcomes)}"
    graph_nodes[node_id] = GraphNode(
        id=node_id,
        label=f"{outcome.skill_name}_{outcome.task_type}",
        type="skill_outcome",
        properties={
            "success": outcome.success,
            "execution_time": outcome.execution_time,
            "context_size": outcome.context_size,
            "timestamp": outcome.timestamp.isoformat(),
        },
    )

    result = {
        "recorded": True,
        "outcome_id": len(skill_outcomes),
        "message": f"Recorded outcome for {outcome.skill_name} on {outcome.task_type}",
        "total_outcomes": len(skill_outcomes),
    }

    return json.dumps(result, indent=2)
