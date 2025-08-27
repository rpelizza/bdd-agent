"""Cliente OpenAI para integração com a API.

Este módulo contém a configuração e wrapper para o cliente OpenAI,
incluindo tratamento de erros e configurações específicas.
"""

import logging
from typing import Dict, Optional

from openai import OpenAI
from pydantic import BaseModel

# Configuração de logging
logger = logging.getLogger(__name__)


class OpenAIConfig(BaseModel):
    """Configuração para o cliente OpenAI."""

    api_key: str
    model: str = "gpt-4o-mini"
    max_tokens: int = 2000
    temperature: float = 0.3
    timeout: int = 30


class OpenAIClientWrapper:
    """Wrapper para o cliente OpenAI com tratamento de erros."""

    # Modelos suportados e suas configurações
    SUPPORTED_MODELS = {
        "gpt-4o-mini": {"name": "GPT-4o Mini", "max_tokens": 4096, "cost_per_1k": 0.00015},
        "gpt-4.1-mini": {"name": "GPT-4.1 Mini", "max_tokens": 4096, "cost_per_1k": 0.0001},
        "gpt-5-mini": {"name": "GPT-5 Mini", "max_tokens": 8192, "cost_per_1k": 0.0002},
        "gpt-4.1-nano": {"name": "GPT-4.1 Nano", "max_tokens": 2048, "cost_per_1k": 0.00005},
    }

    def __init__(self, config: OpenAIConfig):
        """Inicializa o wrapper do cliente OpenAI.

        Args:
            config: Configuração do cliente OpenAI
        """
        self.config = config
        
        # Validar formato da API key
        if not self._validate_api_key_format(config.api_key):
            raise ValueError("Formato de API key inválido. Deve começar com 'sk-' e ter pelo menos 20 caracteres.")
        
        self.client = OpenAI(api_key=config.api_key)

        # Validar modelo
        if config.model not in self.SUPPORTED_MODELS:
            logger.warning(f"Modelo {config.model} não está na lista de suportados")
    
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Valida o formato básico da API key.
        
        Args:
            api_key: A chave da API para validar
            
        Returns:
            True se o formato é válido, False caso contrário
        """
        if not api_key or not isinstance(api_key, str):
            return False
            
        # Remove espaços e verifica formato
        cleaned_key = api_key.strip()
        return cleaned_key.startswith('sk-') and len(cleaned_key) >= 20

    def create_completion(
        self, messages: list, temperature: Optional[float] = None, max_tokens: Optional[int] = None
    ) -> str:
        """Cria uma completion usando a API OpenAI.

        Args:
            messages: Lista de mensagens para o chat
            temperature: Temperatura para a geração (sobrescreve config)
            max_tokens: Máximo de tokens (sobrescreve config)

        Returns:
            Conteúdo da resposta gerada

        Raises:
            Exception: Se houver erro na API
        """
        try:
            # Usar valores da config se não fornecidos
            temp = temperature if temperature is not None else self.config.temperature
            tokens = max_tokens if max_tokens is not None else self.config.max_tokens

            logger.info(f"Criando completion com modelo {self.config.model}")

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=tokens,
                temperature=temp,
                timeout=self.config.timeout,
            )

            content = response.choices[0].message.content

            # Log de uso
            usage = response.usage
            if usage:
                logger.info(
                    f"Tokens usados - Prompt: {usage.prompt_tokens}, "
                    f"Completion: {usage.completion_tokens}, "
                    f"Total: {usage.total_tokens}"
                )

            return content.strip() if content else ""

        except Exception as e:
            logger.error(f"Erro na API OpenAI: {str(e)}")
            raise

    def validate_api_key(self) -> bool:
        """Valida se a API key está funcionando.

        Returns:
            True se a API key é válida, False caso contrário
        """
        try:
            # Fazer uma chamada simples para testar
            test_messages = [{"role": "user", "content": "Teste"}]

            response = self.client.chat.completions.create(
                model=self.config.model, messages=test_messages, max_tokens=10, temperature=0
            )

            return response.choices[0].message.content is not None

        except Exception as e:
            logger.error(f"API key inválida: {str(e)}")
            return False

    def get_model_info(self) -> Dict:
        """Retorna informações sobre o modelo atual.

        Returns:
            Dicionário com informações do modelo
        """
        return self.SUPPORTED_MODELS.get(
            self.config.model,
            {
                "name": self.config.model,
                "max_tokens": "Desconhecido",
                "cost_per_1k": "Desconhecido",
            },
        )

    @classmethod
    def get_available_models(cls) -> Dict:
        """Retorna lista de modelos disponíveis.

        Returns:
            Dicionário com modelos suportados
        """
        return cls.SUPPORTED_MODELS.copy()