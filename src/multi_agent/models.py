"""
Modelos de dados para o sistema Multi-Agent BDD.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Papéis disponíveis para agentes na sociedade BDD."""

    PM = "product_manager"
    PO = "product_owner"
    TECH_LEAD = "tech_lead"
    QA = "quality_assurance"


class AgentInput(BaseModel):
    """Input padronizado para agentes."""

    user_story: str = Field(...,
                            description="História do usuário a ser analisada")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Contexto adicional")
    previous_scenarios: List[str] = Field(
        default_factory=list, description="Cenários já gerados")


class AgentOutput(BaseModel):
    """Output padronizado de agentes."""

    agent_role: AgentRole = Field(..., description="Papel do agente")
    scenarios: List[str] = Field(...,
                                 description="Cenários gerados pelo agente")
    insights: List[str] = Field(
        default_factory=list, description="Insights e observações")
    concerns: List[str] = Field(
        default_factory=list, description="Preocupações identificadas")
    suggestions: List[str] = Field(
        default_factory=list, description="Sugestões para outros agentes")


class CollaborationConfig(BaseModel):
    """Configurações para colaboração entre agentes."""

    enabled_agents: List[AgentRole] = Field(
        default_factory=lambda: [AgentRole.PO, AgentRole.QA],
        description="Agentes ativos na colaboração"
    )
    collaboration_rounds: int = Field(
        default=2,
        description="Número de rodadas de colaboração"
    )
    max_scenarios_per_agent: int = Field(
        default=3,
        description="Máximo de cenários por agente"
    )
    include_cross_validation: bool = Field(
        default=True,
        description="Se agentes devem validar cenários de outros"
    )
    include_negative: bool = Field(
        default=False,
        description="Se deve incluir cenários negativos/erro"
    )
    include_edge_cases: bool = Field(
        default=False,
        description="Se deve incluir casos extremos/limite"
    )


class MultiAgentResponse(BaseModel):
    """Resposta consolidada do sistema multi-agente."""

    feature_name: str = Field(..., description="Nome da funcionalidade")
    feature_description: str = Field(...,
                                     description="Descrição da funcionalidade")
    agent_outputs: Dict[str,
                        AgentOutput] = Field(..., description="Outputs de cada agente")
    consolidated_scenarios: List[str] = Field(
        ..., description="Cenários consolidados finais")
    collaboration_summary: Dict[str,
                                Any] = Field(..., description="Resumo da colaboração")
    gherkin_content: str = Field(..., description="Conteúdo Gherkin final")
    quality_metrics: Dict[str, float] = Field(
        default_factory=dict, description="Métricas de qualidade")
