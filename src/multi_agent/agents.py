"""
Implementação dos agentes especializados para geração colaborativa de BDD.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
from openai import AsyncOpenAI

from .models import AgentRole, AgentInput, AgentOutput

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Classe base para todos os agentes especialistas."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Inicializa o agente base.

        Args:
            api_key: Chave da API OpenAI
            model: Modelo OpenAI a ser utilizado
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.role = self._get_role()

    @abstractmethod
    def _get_role(self) -> AgentRole:
        """Retorna o papel específico deste agente."""
        pass

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico para este agente."""
        pass

    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """
        Analisa a história do usuário e gera cenários BDD específicos.

        Args:
            agent_input: Input padronizado com história e contexto

        Returns:
            Output do agente com cenários e insights
        """
        try:
            system_prompt = self._get_system_prompt()
            user_prompt = self._create_user_prompt(agent_input)

            logger.info(
                f"Agente {self.role.value} analisando história: {agent_input.user_story[:50]}...")

            # Contexto: Usar temperatura do context, com fallback para 0.3
            temperature = agent_input.context.get("temperature", 0.3)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_completion_tokens=1500
            )

            content = response.choices[0].message.content
            if content is None:
                content = "Erro: Resposta vazia da API"
            return self._parse_response(content)

        except Exception as e:
            logger.error(f"Erro no agente {self.role.value}: {str(e)}")
            return AgentOutput(
                agent_role=self.role,
                scenarios=[],
                insights=[f"Erro na análise: {str(e)}"],
                concerns=["Falha na geração de cenários"],
                suggestions=[]
            )

    def _create_user_prompt(self, agent_input: AgentInput) -> str:
        """Cria o prompt do usuário baseado no input."""
        context = agent_input.context or {}
        max_scenarios = context.get("max_scenarios_per_agent", 3)
        include_negative = context.get("include_negative", False)
        include_edge_cases = context.get("include_edge_cases", False)

        prompt = f"""
História do usuário para análise:
{agent_input.user_story}

REQUISITOS DE GERAÇÃO:
- Gere NO MÁXIMO {max_scenarios} cenário(s) BDD do seu papel ({self.role.value})
- Use formato Gherkin correto (português brasileiro)"""

        # Adicionar requisitos específicos baseados nas configurações
        requirements = []
        if include_negative:
            requirements.append("cenários de erro/validação/falha")
        if include_edge_cases:
            requirements.append("casos extremos/limite/valores limítrofes")

        if requirements:
            prompt += f"\n- Incluir: {', '.join(requirements)}"

        prompt += f"""

Contexto da colaboração:
{context if context else 'Nenhum contexto adicional'}

Cenários já gerados por outros agentes:
{chr(10).join(agent_input.previous_scenarios) if agent_input.previous_scenarios else 'Nenhum cenário prévio'}

REGRAS OBRIGATÓRIAS:
- Gere EXATAMENTE {max_scenarios} cenário(s) BDD, nem mais nem menos
- Cada cenário deve começar com "Cenário X:" onde X é o número
- Use formato Gherkin correto (Dado, Quando, Então, E)
- Foque na sua especialidade como {self.role.value}

ESTRUTURA ESPERADA:
Cenário 1: [título do cenário]
  Dado [condição inicial]
  Quando [ação]
  Então [resultado esperado]

Cenário 2: [título do cenário] (apenas se max_scenarios > 1)
  Dado [condição inicial]
  Quando [ação]
  Então [resultado esperado]

SEÇÕES ADICIONAIS:
1. Insights importantes para esta funcionalidade
2. Preocupações que devem ser consideradas  
3. Sugestões para outros membros da equipe
"""
        return prompt

    def _parse_response(self, content: str) -> AgentOutput:
        """
        Faz parse da resposta do LLM para extrair cenários e insights.

        Args:
            content: Resposta bruta do LLM

        Returns:
            AgentOutput estruturado
        """
        lines = content.strip().split('\n')
        scenarios = []
        insights = []
        concerns = []
        suggestions = []

        current_section = None
        current_scenario = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Contexto: Parser mais específico para cenários, similar ao single agent
            # Identificar seções
            if line.lower().startswith("cenário") and ":" in line:
                if current_scenario:
                    scenarios.append('\n'.join(current_scenario))
                current_scenario = [line]
                current_section = "scenario"
            elif line.lower().startswith(("dado", "quando", "então", "e ", "mas ")):
                if current_section == "scenario":
                    current_scenario.append(line)
            elif "insight" in line.lower():
                current_section = "insights"
            elif "preocupa" in line.lower() or "concern" in line.lower():
                current_section = "concerns"
            elif "sugest" in line.lower():
                current_section = "suggestions"
            elif line.startswith(("- ", "* ", "• ")):
                clean_line = line[2:].strip()
                if current_section == "insights":
                    insights.append(clean_line)
                elif current_section == "concerns":
                    concerns.append(clean_line)
                elif current_section == "suggestions":
                    suggestions.append(clean_line)

        # Adicionar último cenário se existir
        if current_scenario:
            scenarios.append(self._format_bdd_scenario(
                '\n'.join(current_scenario)))

        return AgentOutput(
            agent_role=self.role,
            scenarios=[self._format_bdd_scenario(s) for s in scenarios],
            insights=insights,
            concerns=concerns,
            suggestions=suggestions
        )

    def _format_bdd_scenario(self, scenario: str) -> str:
        """
        Formata um cenário BDD com quebras de linha e indentação correta.

        Args:
            scenario: Cenário bruto extraído da resposta

        Returns:
            Cenário formatado corretamente no padrão BDD
        """
        lines = scenario.split('\n')
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Título do cenário (sem indentação)
            if "cenário" in line.lower() and ":" in line:
                formatted_lines.append(line)
            # Passos BDD (com indentação)
            elif line.lower().startswith(("dado", "quando", "então", "e ", "mas ")):
                formatted_lines.append(f"    {line}")
            else:
                # Outras linhas mantém formatação original com indentação
                formatted_lines.append(f"    {line}")

        return '\n'.join(formatted_lines)


class POAgent(BaseAgent):
    """Agente Product Owner - Foco em experiência do usuário e valor do produto."""

    def _get_role(self) -> AgentRole:
        return AgentRole.PO

    def _get_system_prompt(self) -> str:
        return """
Você é um Product Owner (PO) especialista em BDD e experiência do usuário.

SEU PAPEL:
- Focar na perspectiva do usuário final
- Garantir que os cenários entreguem valor real
- Considerar jornadas do usuário e casos de uso principais
- Pensar em métricas de sucesso e KPIs

DIRETRIZES:
1. Priorize cenários que demonstrem valor para o usuário
2. Inclua happy paths que sejam intuitivos e eficientes
3. Considere diferentes tipos de usuários (personas)
4. Foque em resultados mensuráveis e objetivos de negócio
5. Use linguagem próxima ao usuário final

FORMATO DE RESPOSTA:
Cenários BDD (formato Gherkin):
[seus cenários aqui]

Insights do PO:
- [insight 1]
- [insight 2]

Preocupações:
- [preocupação 1]
- [preocupação 2]

Sugestões para a equipe:
- [sugestão 1]
- [sugestão 2]
"""


class QAAgent(BaseAgent):
    """Agente Quality Assurance - Foco em edge cases e cenários negativos."""

    def _get_role(self) -> AgentRole:
        return AgentRole.QA

    def _get_system_prompt(self) -> str:
        return """
Você é um QA Engineer especialista em BDD e estratégias de teste.

SEU PAPEL:
- Identificar edge cases e cenários negativos
- Garantir cobertura completa de testes
- Pensar em validações e tratamentos de erro
- Considerar performance e segurança

DIRETRIZES:
1. Crie cenários que testam limites e validações
2. Inclua casos de erro e exceções
3. Pense em dados inválidos e situações inesperadas
4. Considere performance under stress
5. Valide integrações e dependências externas

FORMATO DE RESPOSTA:
Cenários BDD (formato Gherkin):
[seus cenários aqui]

Insights do QA:
- [insight 1]
- [insight 2]

Preocupações:
- [preocupação 1] 
- [preocupação 2]

Sugestões para a equipe:
- [sugestão 1]
- [sugestão 2]
"""


class PMAgent(BaseAgent):
    """Agente Product Manager - Foco em regras de negócio e compliance."""

    def _get_role(self) -> AgentRole:
        return AgentRole.PM

    def _get_system_prompt(self) -> str:
        return """
Você é um Product Manager (PM) especialista em BDD e regras de negócio.

SEU PAPEL:
- Garantir alinhamento com objetivos estratégicos
- Validar regras de negócio e compliance
- Considerar stakeholders e requirements
- Pensar em ROI e métricas de sucesso

DIRETRIZES:
1. Valide regras de negócio críticas
2. Considere aspectos regulatórios e compliance
3. Pense em diferentes stakeholders
4. Inclua métricas e KPIs mensuráveis
5. Foque em viabilidade e sustentabilidade

FORMATO DE RESPOSTA:
Cenários BDD (formato Gherkin):
[seus cenários aqui]

Insights do PM:
- [insight 1]
- [insight 2]

Preocupações:
- [preocupação 1]
- [preocupação 2]

Sugestões para a equipe:
- [sugestão 1]
- [sugestão 2]
"""


class TechLeadAgent(BaseAgent):
    """Agente Tech Lead - Foco em viabilidade técnica e arquitetura."""

    def _get_role(self) -> AgentRole:
        return AgentRole.TECH_LEAD

    def _get_system_prompt(self) -> str:
        return """
Você é um Tech Lead especialista em BDD e arquitetura de software.

SEU PAPEL:
- Avaliar viabilidade técnica
- Considerar constraints de performance e segurança
- Pensar em integrações e dependências
- Validar escalabilidade e manutenibilidade

DIRETRIZES:
1. Inclua cenários que testem performance
2. Considere integrações com sistemas externos
3. Pense em segurança e proteção de dados
4. Valide escalabilidade e concorrência
5. Considere deployment e operações

FORMATO DE RESPOSTA:
Cenários BDD (formato Gherkin):
[seus cenários aqui]

Insights do Tech Lead:
- [insight 1]
- [insight 2]

Preocupações:
- [preocupação 1]
- [preocupação 2]

Sugestões para a equipe:
- [sugestão 1]
- [sugestão 2]
"""
