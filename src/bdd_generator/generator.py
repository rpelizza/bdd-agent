"""Módulo responsável pela geração de cenários BDD usando OpenAI.

Este módulo contém a lógica principal para converter descrições em linguagem
natural para cenários BDD estruturados no formato Gherkin.
"""

import logging
from typing import List

from openai import OpenAI
from pydantic import BaseModel, Field

# Configuração de logging
logger = logging.getLogger(__name__)


class BDDScenario(BaseModel):
    """Modelo para um cenário BDD individual."""

    title: str = Field(..., description="Título do cenário")
    steps: List[str] = Field(..., description="Lista de passos do cenário")
    scenario_type: str = Field(default="positive", description="Tipo do cenário")


class BDDResponse(BaseModel):
    """Modelo para resposta completa de geração BDD."""

    feature_name: str = Field(..., description="Nome da funcionalidade")
    feature_description: str = Field(..., description="Descrição da funcionalidade")
    scenarios: List[BDDScenario] = Field(..., description="Lista de cenários")
    gherkin_content: str = Field(..., description="Conteúdo completo em Gherkin")


class BDDGenerator:
    """Gerador de cenários BDD usando OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Inicializa o gerador BDD.

        Args:
            api_key: Chave da API OpenAI
            model: Modelo OpenAI a ser usado
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _create_system_prompt(self) -> str:
        """Cria o prompt do sistema para geração BDD."""
        return """
Você é um especialista em BDD (Behavior Driven Development) e deve gerar cenários de teste
no formato Gherkin.

Regras importantes:
1. Use SEMPRE português brasileiro
2. Siga a estrutura: Funcionalidade, Cenário, Dado, Quando, Então, E
3. Seja específico e claro nos passos
4. Inclua cenários positivos e negativos quando solicitado
5. Use verbos no presente do indicativo
6. Evite detalhes técnicos de implementação

Formato esperado:
```gherkin
Funcionalidade: [Nome da funcionalidade]
  [Descrição da funcionalidade]

  Cenário: [Nome do cenário]
    Dado [condição inicial]
    Quando [ação do usuário]
    Então [resultado esperado]
    E [validação adicional]
```
"""

    def _create_user_prompt(
        self,
        user_story: str,
        num_scenarios: int = 5,
        include_negative: bool = False,
        include_edge_cases: bool = False,
    ) -> str:
        """Cria o prompt do usuário para geração BDD.

        Args:
            user_story: História do usuário
            num_scenarios: Número de cenários a gerar
            include_negative: Se deve incluir cenários negativos
            include_edge_cases: Se deve incluir casos extremos
        """
        prompt = f"""Gere {num_scenarios} cenários BDD para a seguinte história:

{user_story}

Requisitos:
- Gere cenários claros e testáveis
- Use português brasileiro
- Inclua pelo menos 1 cenário de sucesso"""

        if include_negative:
            prompt += "\n- Inclua cenários de erro/validação"

        if include_edge_cases:
            prompt += "\n- Inclua casos extremos/limite"

        prompt += "\n\nRetorne apenas o conteúdo Gherkin formatado."

        return prompt

    def generate_scenarios(
        self,
        user_story: str,
        num_scenarios: int = 3,
        include_negative: bool = True,
        include_edge_cases: bool = False,
        temperature: float = 0.3,
    ) -> BDDResponse:
        """Gera cenários BDD a partir de uma história do usuário.

        Args:
            user_story: História do usuário em linguagem natural
            num_scenarios: Número de cenários a gerar
            include_negative: Se deve incluir cenários negativos
            include_edge_cases: Se deve incluir casos extremos
            temperature: Criatividade da IA (0.0 a 1.0)

        Returns:
            BDDResponse com os cenários gerados

        Raises:
            Exception: Se houver erro na chamada da API
        """
        try:
            logger.info(f"Gerando {num_scenarios} cenários BDD para: {user_story[:50]}...")

            # Criar prompts
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(
                user_story, num_scenarios, include_negative, include_edge_cases
            )

            # Chamar OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=2000,
                temperature=temperature,
            )

            # Extrair conteúdo
            gherkin_content = response.choices[0].message.content.strip()

            # Processar resposta
            feature_name = self._extract_feature_name(gherkin_content)
            feature_description = self._extract_feature_description(gherkin_content)
            scenarios = self._parse_scenarios(gherkin_content)

            logger.info(f"Cenários gerados com sucesso: {len(scenarios)} cenários")

            return BDDResponse(
                feature_name=feature_name,
                feature_description=feature_description,
                scenarios=scenarios,
                gherkin_content=gherkin_content,
            )

        except Exception as e:
            logger.error(f"Erro ao gerar cenários BDD: {str(e)}")
            raise

    def _extract_feature_name(self, gherkin_content: str) -> str:
        """Extrai o nome da funcionalidade do conteúdo Gherkin."""
        lines = gherkin_content.split("\n")
        for line in lines:
            if line.strip().startswith("Funcionalidade:"):
                return line.replace("Funcionalidade:", "").strip()
        return "Nova Funcionalidade"

    def _extract_feature_description(self, gherkin_content: str) -> str:
        """Extrai a descrição da funcionalidade do conteúdo Gherkin."""
        lines = gherkin_content.split("\n")
        description_lines = []

        found_feature = False
        for line in lines:
            if line.strip().startswith("Funcionalidade:"):
                found_feature = True
                continue
            elif found_feature and line.strip().startswith("Cenário"):
                break
            elif found_feature and line.strip():
                description_lines.append(line.strip())

        return " ".join(description_lines) if description_lines else ""

    def _parse_scenarios(self, gherkin_content: str) -> List[BDDScenario]:
        """Parseia os cenários do conteúdo Gherkin."""
        scenarios = []
        lines = gherkin_content.split("\n")

        current_scenario = None
        current_steps = []

        for line in lines:
            line = line.strip()

            if line.startswith("Cenário:"):
                # Salvar cenário anterior se existir
                if current_scenario:
                    scenarios.append(
                        BDDScenario(
                            title=current_scenario,
                            steps=current_steps.copy(),
                            scenario_type=self._determine_scenario_type(
                                current_scenario, current_steps
                            ),
                        )
                    )

                # Iniciar novo cenário
                current_scenario = line.replace("Cenário:", "").strip()
                current_steps = []

            elif line.startswith(("Dado", "Quando", "Então", "E", "Mas")):
                current_steps.append(line)

        # Adicionar último cenário
        if current_scenario:
            scenarios.append(
                BDDScenario(
                    title=current_scenario,
                    steps=current_steps.copy(),
                    scenario_type=self._determine_scenario_type(current_scenario, current_steps),
                )
            )

        return scenarios

    def _determine_scenario_type(self, title: str, steps: List[str]) -> str:
        """Determina o tipo do cenário baseado no título e passos."""
        title_lower = title.lower()
        steps_text = " ".join(steps).lower()

        negative_keywords = ["erro", "inválido", "falha", "negativo", "incorreto"]
        edge_keywords = ["limite", "extremo", "máximo", "mínimo", "vazio"]

        if any(keyword in title_lower or keyword in steps_text for keyword in negative_keywords):
            return "negative"
        elif any(keyword in title_lower or keyword in steps_text for keyword in edge_keywords):
            return "edge_case"
        else:
            return "positive"
