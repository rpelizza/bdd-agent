"""
Sistema Multi-Agent para geração colaborativa de cenários BDD.

Este módulo implementa uma sociedade de agentes especializados que colaboram
para gerar cenários BDD de alta qualidade, cada um contribuindo com sua expertise.
"""

from .orchestrator import MultiAgentOrchestrator
from .agents import POAgent, QAAgent, PMAgent, TechLeadAgent
from .models import AgentRole, CollaborationConfig, MultiAgentResponse

__all__ = [
    "MultiAgentOrchestrator",
    "POAgent",
    "QAAgent",
    "PMAgent",
    "TechLeadAgent",
    "AgentRole",
    "CollaborationConfig",
    "MultiAgentResponse"
]
