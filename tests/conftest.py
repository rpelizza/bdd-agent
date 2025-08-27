"""Configuração global para testes pytest.

Este módulo contém fixtures e configurações compartilhadas
entre todos os testes do projeto BDD Agent.
"""

import pytest
from typing import Generator
from unittest.mock import Mock


@pytest.fixture
def mock_openai_client() -> Mock:
    """Fixture que fornece um cliente OpenAI mockado.
    
    Returns:
        Mock: Cliente OpenAI mockado para testes.
    """
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(
                    content="Cenário BDD de exemplo gerado para teste"
                )
            )
        ]
    )
    return mock_client


@pytest.fixture
def sample_user_story() -> str:
    """Fixture que fornece uma história de usuário de exemplo.
    
    Returns:
        str: História de usuário para testes.
    """
    return (
        "Como um usuário do sistema, "
        "eu quero fazer login com meu email e senha, "
        "para que eu possa acessar minha conta."
    )


@pytest.fixture
def sample_bdd_scenario() -> str:
    """Fixture que fornece um cenário BDD de exemplo.
    
    Returns:
        str: Cenário BDD formatado para testes.
    """
    return """
Funcionalidade: Login de usuário
  Como um usuário do sistema
  Eu quero fazer login com meu email e senha
  Para que eu possa acessar minha conta

  Cenário: Login com credenciais válidas
    Dado que estou na página de login
    E tenho um email válido "usuario@exemplo.com"
    E tenho uma senha válida "senha123"
    Quando eu preencho o campo email
    E eu preencho o campo senha
    E eu clico no botão "Entrar"
    Então eu devo ser redirecionado para o dashboard
    E devo ver a mensagem "Bem-vindo!"
"""