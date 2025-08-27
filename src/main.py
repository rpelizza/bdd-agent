"""Entry point principal da aplicação BDD Agent.

Este módulo contém a interface principal do Streamlit para o gerador
de cenários BDD usando IA.
"""

import streamlit as st
import logging
from typing import Dict, Any

from bdd_generator import BDDGenerator, OpenAIClientWrapper, OpenAIConfig

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

        # Configurar cliente OpenAI
        openai_config = OpenAIConfig(
            api_key=api_key, model=model, temperature=0.3, max_tokens=2000)

        openai_client = OpenAIClientWrapper(openai_config)

        # Criar gerador BDD
        bdd_generator = BDDGenerator(api_key, model)

        # Gerar cenários
        response = bdd_generator.generate_scenarios(
            user_story=user_story,
            num_scenarios=config.get("num_cenarios", 5),
            include_negative=config.get("incluir_negativos", False),
            include_edge_cases=config.get("casos_extremos", False),
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
    # Header da aplicação
    st.title("Wagão BDD")
    st.markdown("**Gerador Inteligente de Cenários BDD com IA**")

    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")

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

        st.divider()

        # Configurações do modelo
        st.subheader("🧠 Modelo IA")
        st.selectbox(
            "Modelo OpenAI", ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"], index=0, key="modelo"
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

    # Área principal
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📝 História do Usuário")

        user_story = st.text_area(
            "Descreva a história do usuário:",
            placeholder="Como um [tipo de usuário], eu quero [objetivo] " "para que [benefício]...",
            height=200,
            help="Descreva a funcionalidade que você quer testar",
        )

        # Opções adicionais
        st.subheader("🎯 Opções Avançadas")

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

    with col2:
        st.header("🎭 Cenários BDD Gerados")

        if generate_button:
            if not api_key:
                st.error("❌ Configure sua API Key primeiro!")
            elif not user_story.strip():
                st.error("❌ Descreva uma história do usuário!")
            else:
                # Geração real usando BDDGenerator
                with st.spinner("🤖 Gerando cenários BDD..."):
                    try:
                        # Coletar configurações
                        config = {
                            "incluir_negativos": st.session_state.get("incluir_negativos", True),
                            "casos_extremos": st.session_state.get("casos_extremos", False),
                            "num_cenarios": st.session_state.get("num_cenarios", 3),
                        }

                        model = st.session_state.get("modelo", "gpt-4o-mini")

                        # Gerar cenários usando a função real
                        example_scenario = generate_bdd_scenarios(
                            user_story=user_story, config=config, api_key=api_key, model=model
                        )

                    except Exception as e:
                        st.error(f"❌ Erro na geração: {str(e)}")
                        example_scenario = None

                if example_scenario:
                    st.success("✅ Cenários gerados com sucesso!")
                    st.markdown(example_scenario)

                    # Botões de ação
                    col_download, col_copy = st.columns(2)

                    with col_download:
                        st.download_button(
                            "📥 Download .txt",
                            data=example_scenario,
                            file_name="cenarios_bdd.txt",
                            mime="text/plain",
                        )

                    with col_copy:
                        if st.button("📋 Copiar para Clipboard"):
                            st.success(
                                "Copiado! (funcionalidade será implementada)")
        else:
            st.info(
                "👆 Preencha a história do usuário e clique em " "'Gerar Cenários BDD' para começar!"
            )

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Wagão BDD - by Rafael Pelizza</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
