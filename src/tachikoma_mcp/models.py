from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TopologyPattern(BaseModel):
    """Represents an orchestration topology pattern"""

    name: str
    description: str
    confidence_threshold: float
    patterns: List[str] = []


class SkillOutcome(BaseModel):
    """Tracks skill execution outcomes for learning"""

    skill_name: str
    task_type: str
    success: bool
    execution_time: float
    timestamp: datetime
    context_size: int
    error_message: Optional[str] = None


class GraphNode(BaseModel):
    """Node in the graph-based memory/routing system"""

    id: str
    label: str
    type: str  # 'tool', 'skill', 'context', 'agent'
    properties: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None


class GraphEdge(BaseModel):
    """Edge in the graph-based memory/routing system"""

    source: str
    target: str
    label: str
    weight: float = 1.0
    properties: Dict[str, Any] = {}
