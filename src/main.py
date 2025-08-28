"""Entry point principal da aplicação BDD Agent.

Este módulo contém a interface principal do Streamlit para o gerador
de cenários BDD usando IA.
"""

import streamlit as st
import logging
import asyncio
from typing import Dict, Any, List

from bdd_generator import BDDGenerator, OpenAIClientWrapper, OpenAIConfig
from multi_agent import MultiAgentOrchestrator, CollaborationConfig, AgentRole

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="BDD Agent - Gerador de Cenários",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)


async def generate_multi_agent_bdd_scenarios(
    user_story: str, config: Dict[str, Any], api_key: str, model: str
) -> str:
    """
    Gera cenários BDD usando sistema multi-agente.

    Args:
        user_story: História do usuário
        config: Configurações (enabled_agents, collaboration_rounds, etc.)
        api_key: Chave da API OpenAI
        model: Modelo de IA a ser usado

    Returns:
        Cenários BDD formatados com insights da colaboração

    Raises:
        Exception: Se houver erro na geração
    """
    try:
        logger.info(f"Iniciando geração multi-agente com modelo {model}")

        # Configurar orquestrador
        orchestrator = MultiAgentOrchestrator(api_key=api_key, model=model)

        # Configurar colaboração baseado no config
        collaboration_config = CollaborationConfig(
            enabled_agents=config.get(
                "enabled_agents", [AgentRole.PO, AgentRole.QA]),
            collaboration_rounds=config.get("collaboration_rounds", 1),
            max_scenarios_per_agent=config.get("max_scenarios_per_agent", 3),
            include_cross_validation=config.get(
                "include_cross_validation", True),
            include_negative=config.get("include_negative", False),
            include_edge_cases=config.get("include_edge_cases", False)
        )

        # Gerar cenários
        response = await orchestrator.generate_bdd_scenarios(user_story, collaboration_config)

        # Formatar cenários com a mesma estrutura do single agent
        scenarios_formatted = _format_scenarios_for_display(
            response.consolidated_scenarios)

        # Formatar resposta para exibição
        formatted_output = f"""# 🤖 Cenários BDD - Geração Multi-Agente

## 📝 Funcionalidade: {response.feature_name}

{response.feature_description}

---

## 🎯 Cenários Gerados

{scenarios_formatted}

---

## 👥 Colaboração dos Agentes

**Agentes Participantes:** {', '.join(response.collaboration_summary['participating_agents'])}
**Total de Cenários:** {response.collaboration_summary['total_scenarios_generated']}

### 💡 Principais Insights:

{chr(10).join([f"• {insight}" for insight in response.collaboration_summary['key_insights'][:5]]).replace(chr(10), chr(10) + chr(10))}

### ⚠️ Preocupações Identificadas:

{chr(10).join([f"• {concern}" for concern in response.collaboration_summary['main_concerns'][:3]]).replace(chr(10), chr(10) + chr(10))}

---

## 📊 Métricas de Qualidade
- **Score de Colaboração:** {response.quality_metrics['collaboration_score']:.1f}/100
- **Tempo de Geração:** {response.quality_metrics['total_time_seconds']:.2f}s
- **Cenários por Agente:** {response.quality_metrics['scenarios_per_agent']:.1f}
"""

        logger.info(
            f"Geração multi-agente concluída: {response.quality_metrics['total_scenarios']} cenários")
        return formatted_output

    except Exception as e:
        logger.error(f"Erro na geração multi-agente: {str(e)}")
        raise


def _format_scenarios_for_display(scenarios: List[str]) -> str:
    """
    Formata cenários para exibição com a mesma estrutura do single agent.

    Args:
        scenarios: Lista de cenários brutos

    Returns:
        Cenários formatados no estilo BDD
    """
    if not scenarios:
        return "Nenhum cenário foi gerado."

    formatted_lines = []

    for i, scenario in enumerate(scenarios, 1):
        # Parse do cenário para extrair título e passos
        lines = scenario.strip().split('\n')

        # Procurar pelo título do cenário
        title = f"Cenário {i}"
        steps = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Se a linha contém "Cenário:" é o título
            if "cenário:" in line.lower():
                title = line.replace("Cenário:", "").replace(
                    "cenário:", "").strip()
            # Se a linha começa com palavras-chave BDD, é um passo
            elif line.lower().startswith(("dado", "quando", "então", "e ", "mas ")):
                steps.append(line)
            # Outras linhas podem ser parte do contexto
            else:
                if line and not line.startswith("#"):
                    steps.append(line)

        # Formatar o cenário
        formatted_lines.append(f"### Cenário {i}: {title}")
        formatted_lines.append("")  # Linha em branco

        # Adicionar cada passo com indentação
        for step in steps:
            formatted_lines.append(f"    {step}")

        formatted_lines.append("")  # Linha em branco entre cenários

    return "\n".join(formatted_lines)


def generate_bdd_scenarios(
    user_story: str, config: Dict[str, Any], api_key: str, model: str
) -> str:
    """
    Gera cenários BDD baseados na história do usuário e configurações.

    Args:
        user_story: História do usuário
        config: Configurações (incluir_negativos, casos_extremos, num_cenarios)
        api_key: Chave da API OpenAI
        model: Modelo de IA a ser usado

    Returns:
        Cenários BDD formatados

    Raises:
        Exception: Se houver erro na geração
    """
    try:
        logger.info(f"Iniciando geração de cenários BDD com modelo {model}")

        # Criar gerador BDD
        bdd_generator = BDDGenerator(api_key, model)

        # Gerar cenários
        response = bdd_generator.generate_scenarios(
            user_story=user_story,
            num_scenarios=config.get("num_cenarios", 5),
            include_negative=config.get("incluir_negativos", False),
            include_edge_cases=config.get("casos_extremos", False),
            temperature=config.get("criatividade", 0.3),
        )

        # Formatar resposta
        if response.scenarios:
            formatted_scenarios = []
            formatted_scenarios.append("# Cenários BDD Gerados\n")
            formatted_scenarios.append(
                f"## Funcionalidade: {response.feature_name}\n")

            for i, scenario in enumerate(response.scenarios, 1):
                formatted_scenarios.append(
                    f"### Cenário {i}: {scenario.title}")

                for step in scenario.steps:
                    formatted_scenarios.append(f"    {step}")

                formatted_scenarios.append("")  # Linha em branco

            return "\n".join(formatted_scenarios)
        else:
            return (
                "Não foi possível gerar cenários. Tente novamente com uma história mais detalhada."
            )

    except Exception as e:
        logger.error(f"Erro na geração de cenários: {str(e)}")
        raise Exception(f"Erro na geração: {str(e)}")


def main() -> None:
    """Função principal da aplicação."""
    # Configurar página
    st.set_page_config(
        page_title="Pelizza BDD",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header clean e minimalista
    st.markdown("""
    <div style="text-align: center; padding: 30px 0 40px 0;">
        <h1 style="color: #2C3E50; font-size: 2.5em; font-weight: 300; margin-bottom: 8px; letter-spacing: -1px;">
            Pelizza BDD
        </h1>
        <p style="color: #7F8C8D; font-size: 1.1em; margin-top: 0; font-weight: 400;">
            Multi-Agent Society for BDD Generation
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar com design clean
    with st.sidebar:
        st.markdown("""
        <div style="padding: 15px 0 25px 0; border-bottom: 1px solid #E8EAED;">
            <h3 style="color: #2C3E50; font-weight: 500; margin: 0; font-size: 1.2em;">
                Configurações
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Verificação da API Key
        api_key_input = st.text_input(
            "OpenAI API Key", type="password", help="Insira sua chave da API OpenAI (formato: sk-...)"
        )

        # Limpar e validar a API key
        api_key = None
        if api_key_input:
            # Remove espaços em branco e caracteres especiais
            cleaned_key = api_key_input.strip()

            # Validar formato básico da API key OpenAI
            if cleaned_key.startswith('sk-') and len(cleaned_key) >= 20:
                api_key = cleaned_key
                st.success("✅ API Key configurada")
            else:
                st.error("❌ Formato de API Key inválido. Deve começar com 'sk-'")
        else:
            st.warning("⚠️ Configure sua API Key para continuar")

        # Seção: Modelo IA
        st.markdown("""
        <div style="margin: 25px 0 20px 0;">
            <h4 style="color: #2C3E50; font-weight: 500; margin: 0 0 15px 0; font-size: 1.1em;">
                Modelo IA
            </h4>
        </div>
        """, unsafe_allow_html=True)

        st.selectbox(
            "Modelo OpenAI",
            ["gpt-4o-mini", "gpt-4.1-mini"],
            index=0,
            key="modelo",
            help="gpt-4o-mini: mais preciso | gpt-4.1-mini: mais rápido"
        )

        st.slider(
            "Criatividade",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Controla a criatividade das respostas",
            key="criatividade",
        )

        # Separador sutil
        st.markdown("""
        <div style="margin: 30px 0; border-bottom: 1px solid #F1F3F4;"></div>
        """, unsafe_allow_html=True)

        # Seção: Modo de Geração
        st.markdown("""
        <div style="margin: 0 0 20px 0;">
            <h4 style="color: #2C3E50; font-weight: 500; margin: 0 0 15px 0; font-size: 1.1em;">
                Modo de Geração
            </h4>
        </div>
        """, unsafe_allow_html=True)
        generation_mode = st.selectbox(
            "Selecionar Modo",
            ["Single Agent (Rápido)", "Multi-Agent Society (Avançado)"],
            index=0,
            help="Single Agent usa um modelo IA. Multi-Agent usa equipe de especialistas."
        )

        # Configurações Multi-Agent com design clean
        if generation_mode == "Multi-Agent Society (Avançado)":
            # Separador elegante
            st.markdown("""
            <div style="margin: 30px 0; border-bottom: 1px solid #F1F3F4;"></div>
            """, unsafe_allow_html=True)

            # Header clean da seção
            st.markdown("""
            <div style="margin: 0 0 25px 0;">
                <h4 style="color: #2C3E50; font-weight: 500; margin: 0 0 8px 0; font-size: 1.1em;">
                    Equipe de Especialistas
                </h4>
                <p style="color: #7F8C8D; font-size: 0.9em; margin: 0;">
                    Selecione os agentes que irão colaborar
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Agentes com design clean
            po_enabled = st.checkbox(
                "Product Owner",
                value=True,
                help="Foco em experiência do usuário e valor do produto"
            )
            qa_enabled = st.checkbox(
                "QA Engineer",
                value=True,
                help="Edge cases e cenários negativos"
            )
            pm_enabled = st.checkbox(
                "Product Manager",
                value=False,
                help="Regras de negócio e compliance"
            )
            tech_enabled = st.checkbox(
                "Tech Lead",
                value=False,
                help="Viabilidade técnica e arquitetura"
            )

            # Separador
            st.markdown("""
            <div style="margin: 25px 0 20px 0; border-bottom: 1px solid #F8F9FA;"></div>
            """, unsafe_allow_html=True)

            # Configurações de colaboração com design clean
            st.markdown("""
            <div style="margin: 0 0 15px 0;">
                <h5 style="color: #2C3E50; font-weight: 500; margin: 0; font-size: 1em;">
                    Configurações de Colaboração
                </h5>
            </div>
            """, unsafe_allow_html=True)

            collaboration_rounds = st.number_input(
                "Rodadas de Colaboração",
                min_value=1,
                max_value=3,
                value=1,
                help="Mais rodadas = maior qualidade mas mais tempo"
            )

            max_scenarios = st.number_input(
                "Cenários por Agente",
                min_value=1,
                max_value=5,
                value=3,
                help="Máximo de cenários que cada agente pode gerar"
            )

    # Área principal com layout clean
    st.markdown("""
    <div style="max-width: 800px; margin: 0 auto; padding: 0 20px;">
    """, unsafe_allow_html=True)
    # Header da seção principal com design clean
    st.markdown("""
    <div style="margin: 40px 0 30px 0;">
        <h2 style="color: #2C3E50; font-weight: 500; margin: 0 0 8px 0; font-size: 1.6em;">
            História do Usuário
        </h2>
        <p style="color: #7F8C8D; font-size: 1em; margin: 0;">
            Descreva a funcionalidade que você deseja testar
        </p>
    </div>
    """, unsafe_allow_html=True)

    user_story = st.text_area(
        "Descreva a história do usuário:",
        placeholder="Como um [tipo de usuário], eu quero [objetivo] para que [benefício]...",
        height=200,
        key="user_story",
        label_visibility="collapsed"
    )

    # Separador elegante
    st.markdown("""
    <div style="margin: 35px 0 25px 0; border-bottom: 1px solid #F1F3F4;"></div>
    """, unsafe_allow_html=True)

    # Opções avançadas com design clean
    st.markdown("""
    <div style="margin: 0 0 20px 0;">
        <h3 style="color: #2C3E50; font-weight: 500; margin: 0 0 8px 0; font-size: 1.3em;">
            Opções Avançadas
        </h3>
        <p style="color: #7F8C8D; font-size: 0.9em; margin: 0;">
            Configure os tipos de cenários que deseja gerar
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.checkbox(
        "Incluir cenários negativos",
        value=True,
        help="Gerar cenários de teste para casos de erro",
        key="incluir_negativos",
    )

    st.checkbox(
        "Incluir casos extremos",
        value=False,
        help="Gerar cenários para situações limite",
        key="casos_extremos",
    )

    st.number_input(
        "Número de cenários",
        min_value=1,
        max_value=20,
        value=3,
        help="Quantos cenários BDD gerar",
        key="num_cenarios",
    )

    # Botão de geração
    generate_button = st.button(
        "🚀 Gerar Cenários BDD",
        type="primary",
        disabled=not (api_key and user_story.strip()),
        use_container_width=True,
    )

    # Separador elegante
    st.markdown("""
    <div style="margin: 40px 0 25px 0; border-bottom: 1px solid #F1F3F4;"></div>
    """, unsafe_allow_html=True)

    # Header da seção de resultados com design clean
    st.markdown("""
    <div style="margin: 0 0 25px 0;">
        <h2 style="color: #2C3E50; font-weight: 500; margin: 0 0 8px 0; font-size: 1.6em;">
            Cenários BDD Gerados
        </h2>
        <p style="color: #7F8C8D; font-size: 1em; margin: 0;">
            Resultados da geração de cenários
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Definir valores padrão para variáveis multi-agente
    po_enabled = locals().get('po_enabled', True)
    qa_enabled = locals().get('qa_enabled', True)
    pm_enabled = locals().get('pm_enabled', False)
    tech_enabled = locals().get('tech_enabled', False)
    collaboration_rounds = locals().get('collaboration_rounds', 1)
    max_scenarios = locals().get('max_scenarios', 3)

    if generate_button:
        if not api_key:
            st.error("❌ Configure sua API Key primeiro!")
        elif not user_story.strip():
            st.error("❌ Descreva uma história do usuário!")
        else:
            # Geração baseada no modo selecionado
            spinner_text = "🤖 Gerando cenários BDD..." if generation_mode == "Single Agent (Rápido)" else "🤖 Colaboração multi-agente em andamento..."

            with st.spinner(spinner_text):
                example_scenario = None
                try:
                    model = st.session_state.get("modelo", "gpt-4.1-mini")

                    if generation_mode == "Multi-Agent Society (Avançado)":
                        # Preparar configuração multi-agente
                        enabled_agents = []
                        if po_enabled:
                            enabled_agents.append(AgentRole.PO)
                        if qa_enabled:
                            enabled_agents.append(AgentRole.QA)
                        if pm_enabled:
                            enabled_agents.append(AgentRole.PM)
                        if tech_enabled:
                            enabled_agents.append(AgentRole.TECH_LEAD)

                        if not enabled_agents:
                            st.error("❌ Selecione pelo menos um agente!")
                            example_scenario = None
                        else:
                            config = {
                                "enabled_agents": enabled_agents,
                                "collaboration_rounds": collaboration_rounds,
                                "max_scenarios_per_agent": max_scenarios,
                                "include_cross_validation": True,
                                "include_negative": st.session_state.get("incluir_negativos", True),
                                "include_edge_cases": st.session_state.get("casos_extremos", False),
                                "temperature": st.session_state.get("criatividade", 0.5)
                            }

                            # Gerar usando multi-agente (async)
                            example_scenario = asyncio.run(generate_multi_agent_bdd_scenarios(
                                user_story=user_story, config=config, api_key=api_key, model=model
                            ))
                    else:
                        # Modo single agent (atual)
                        config = {
                            "incluir_negativos": st.session_state.get("incluir_negativos", True),
                            "casos_extremos": st.session_state.get("casos_extremos", False),
                            "num_cenarios": st.session_state.get("num_cenarios", 3),
                            "criatividade": st.session_state.get("criatividade", 0.5),
                        }

                        # Gerar cenários usando single agent
                        example_scenario = generate_bdd_scenarios(
                            user_story=user_story, config=config, api_key=api_key, model=model
                        )

                except Exception as e:
                    st.error(f"❌ Erro na geração: {str(e)}")
                    example_scenario = None

            # Exibir resultados se disponíveis
            if example_scenario:
                st.success("✅ Cenários gerados com sucesso!")
                st.markdown(example_scenario)

                # Botões de ação
                col_download = st.columns(1)

                with col_download[0]:
                    st.download_button(
                        "📥 Download .txt",
                        data=example_scenario,
                        file_name="cenarios_bdd.txt",
                        mime="text/plain",
                    )
    else:
        st.info(
            "👆 Preencha a história do usuário e clique em 'Gerar Cenários BDD' para começar!"
        )

    # Footer
    st.divider()
    # Fechar div do container principal
    st.markdown("</div>", unsafe_allow_html=True)

    # Footer clean e minimalista
    st.markdown("""
    <div style="text-align: center; padding: 40px 0 20px 0; margin-top: 50px; border-top: 1px solid #F1F3F4;">
        <p style="color: #B0BEC5; font-size: 0.9em; margin: 0;">
            Pelizza BDD - Powered by Multi-Agent Society
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
