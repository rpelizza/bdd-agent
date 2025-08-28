"""
Orquestrador do sistema multi-agente para geração colaborativa de BDD.
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

from .models import (
    AgentRole, AgentInput, AgentOutput, CollaborationConfig, MultiAgentResponse
)
from .agents import POAgent, QAAgent, PMAgent, TechLeadAgent

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Orquestra a colaboração entre múltiplos agentes especializados
    para gerar cenários BDD de alta qualidade.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Inicializa o orquestrador multi-agente.

        Args:
            api_key: Chave da API OpenAI
            model: Modelo OpenAI a ser utilizado por todos os agentes
        """
        self.api_key = api_key
        self.model = model
        self._agents = self._initialize_agents()

    def _initialize_agents(self) -> Dict[AgentRole, Any]:
        """Inicializa todos os agentes disponíveis."""
        return {
            AgentRole.PO: POAgent(self.api_key, self.model),
            AgentRole.QA: QAAgent(self.api_key, self.model),
            AgentRole.PM: PMAgent(self.api_key, self.model),
            AgentRole.TECH_LEAD: TechLeadAgent(self.api_key, self.model)
        }

    async def generate_bdd_scenarios(
        self,
        user_story: str,
        config: CollaborationConfig = CollaborationConfig()
    ) -> MultiAgentResponse:
        """
        Gera cenários BDD através da colaboração entre agentes.

        Args:
            user_story: História do usuário a ser analisada
            config: Configurações de colaboração

        Returns:
            Resposta consolidada com cenários de todos os agentes
        """
        start_time = datetime.now()
        logger.info(
            f"Iniciando geração multi-agente para: {user_story[:50]}...")

        try:
            # Extrair nome e descrição da feature
            feature_name, feature_description = self._extract_feature_info(
                user_story)

            # Executar colaboração entre agentes
            agent_outputs = await self._orchestrate_collaboration(user_story, config)

            # Consolidar cenários
            consolidated_scenarios = self._consolidate_scenarios(agent_outputs)

            # Gerar conteúdo Gherkin final
            gherkin_content = self._generate_gherkin_content(
                feature_name, feature_description, consolidated_scenarios
            )

            # Calcular métricas de qualidade
            quality_metrics = self._calculate_quality_metrics(
                agent_outputs, start_time)

            # Criar resumo da colaboração
            collaboration_summary = self._create_collaboration_summary(
                agent_outputs)

            response = MultiAgentResponse(
                feature_name=feature_name,
                feature_description=feature_description,
                agent_outputs={role.value: output for role,
                               output in agent_outputs.items()},
                consolidated_scenarios=consolidated_scenarios,
                collaboration_summary=collaboration_summary,
                gherkin_content=gherkin_content,
                quality_metrics=quality_metrics
            )

            logger.info(
                f"Geração multi-agente concluída em {quality_metrics.get('total_time_seconds', 0):.2f}s")
            return response

        except Exception as e:
            logger.error(f"Erro na geração multi-agente: {str(e)}")
            raise

    async def _orchestrate_collaboration(
        self,
        user_story: str,
        config: CollaborationConfig
    ) -> Dict[AgentRole, AgentOutput]:
        """
        Orquestra a colaboração entre os agentes ativos.

        Args:
            user_story: História do usuário
            config: Configurações de colaboração

        Returns:
            Outputs de todos os agentes participantes
        """
        agent_outputs: Dict[AgentRole, AgentOutput] = {}
        all_scenarios: List[str] = []

        # Executar rodadas de colaboração
        for round_num in range(config.collaboration_rounds):
            logger.info(f"Executando rodada {round_num + 1} de colaboração...")

            # Preparar input para os agentes
            agent_input = AgentInput(
                user_story=user_story,
                context={
                    "round": round_num + 1,
                    "total_rounds": config.collaboration_rounds,
                    "max_scenarios_per_agent": config.max_scenarios_per_agent,
                    "include_negative": config.include_negative,
                    "include_edge_cases": config.include_edge_cases
                },
                previous_scenarios=all_scenarios.copy()
            )

            # Executar agentes em paralelo
            active_agents = [
                self._agents[role] for role in config.enabled_agents
                if role in self._agents
            ]

            tasks = [agent.analyze(agent_input) for agent in active_agents]
            outputs = await asyncio.gather(*tasks)

            # Processar outputs da rodada
            for output in outputs:
                agent_outputs[output.agent_role] = output
                all_scenarios.extend(
                    output.scenarios[:config.max_scenarios_per_agent])

        return agent_outputs

    def _extract_feature_info(self, user_story: str) -> tuple[str, str]:
        """
        Extrai nome e descrição da feature a partir da história.

        Args:
            user_story: História do usuário

        Returns:
            Tupla (nome_feature, descrição_feature)
        """
        lines = user_story.strip().split('\n')

        # Tentar extrair do formato padrão "Como... eu quero... para que..."
        if len(lines) >= 3:
            feature_name = "Funcionalidade extraída da história"
            feature_description = user_story.strip()
        else:
            # Usar primeira linha como nome
            feature_name = lines[0][:50] + \
                "..." if len(lines[0]) > 50 else lines[0]
            feature_description = user_story.strip()

        return feature_name, feature_description

    def _consolidate_scenarios(self, agent_outputs: Dict[AgentRole, AgentOutput]) -> List[str]:
        """
        Consolida cenários de todos os agentes, removendo duplicatas.

        Args:
            agent_outputs: Outputs de todos os agentes

        Returns:
            Lista de cenários consolidados
        """
        all_scenarios = []
        seen_scenarios = set()

        # Priorizar ordem: PO -> QA -> PM -> Tech Lead
        priority_order = [AgentRole.PO, AgentRole.QA,
                          AgentRole.PM, AgentRole.TECH_LEAD]

        for role in priority_order:
            if role in agent_outputs:
                for scenario in agent_outputs[role].scenarios:
                    # Criar hash simples para detectar duplicatas
                    scenario_hash = hash(scenario.lower().replace(' ', ''))
                    if scenario_hash not in seen_scenarios:
                        all_scenarios.append(scenario)
                        seen_scenarios.add(scenario_hash)

        return all_scenarios

    def _generate_gherkin_content(
        self,
        feature_name: str,
        feature_description: str,
        scenarios: List[str]
    ) -> str:
        """
        Gera o conteúdo Gherkin final formatado.

        Args:
            feature_name: Nome da funcionalidade
            feature_description: Descrição da funcionalidade
            scenarios: Lista de cenários consolidados

        Returns:
            Conteúdo Gherkin formatado com quebras de linha adequadas
        """
        gherkin_lines = [
            f"Funcionalidade: {feature_name}",
            f"  {feature_description}",
            ""
        ]

        for i, scenario in enumerate(scenarios, 1):
            # Adicionar o cenário com formatação adequada
            scenario_lines = scenario.split('\n')
            for line in scenario_lines:
                if line.strip():  # Ignorar linhas vazias
                    gherkin_lines.append(f"  {line}")

            # Adicionar linha vazia entre cenários (exceto o último)
            if i < len(scenarios):
                gherkin_lines.append("")

        return '\n'.join(gherkin_lines)

    def _calculate_quality_metrics(
        self,
        agent_outputs: Dict[AgentRole, AgentOutput],
        start_time: datetime
    ) -> Dict[str, float]:
        """
        Calcula métricas de qualidade da colaboração.

        Args:
            agent_outputs: Outputs de todos os agentes
            start_time: Tempo de início da geração

        Returns:
            Dicionário com métricas de qualidade
        """
        total_time = (datetime.now() - start_time).total_seconds()
        total_scenarios = sum(len(output.scenarios)
                              for output in agent_outputs.values())
        total_insights = sum(len(output.insights)
                             for output in agent_outputs.values())
        total_concerns = sum(len(output.concerns)
                             for output in agent_outputs.values())

        return {
            "total_time_seconds": total_time,
            "total_scenarios": float(total_scenarios),
            "total_insights": float(total_insights),
            "total_concerns": float(total_concerns),
            "agents_participated": float(len(agent_outputs)),
            "scenarios_per_agent": total_scenarios / len(agent_outputs) if agent_outputs else 0.0,
            "collaboration_score": min(100.0, (total_scenarios * 10 + total_insights * 5) / 10)
        }

    def _create_collaboration_summary(
        self,
        agent_outputs: Dict[AgentRole, AgentOutput]
    ) -> Dict[str, Any]:
        """
        Cria resumo da colaboração entre agentes.

        Args:
            agent_outputs: Outputs de todos os agentes

        Returns:
            Resumo estruturado da colaboração
        """
        return {
            "participating_agents": [role.value for role in agent_outputs.keys()],
            "total_scenarios_generated": sum(len(output.scenarios) for output in agent_outputs.values()),
            "key_insights": [
                insight
                for output in agent_outputs.values()
                for insight in output.insights[:2]  # Top 2 insights por agente
            ],
            "main_concerns": [
                concern
                for output in agent_outputs.values()
                for concern in output.concerns[:1]  # Top concern por agente
            ],
            "collaboration_timestamp": datetime.now().isoformat()
        }
