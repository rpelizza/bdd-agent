# 🛠️ Tech Context - BDD Agent

**Última atualização:** 2024-12-19 14:30:00

---

## 🐍 **Stack Principal**

### **Core Technologies**
- **Python:** 3.9+ (Linguagem principal)
- **Poetry:** Gerenciamento de dependências e ambiente virtual
- **Streamlit:** Framework web para interface do usuário
- **OpenAI API:** Integração com modelos de IA para geração BDD

### **Versões Recomendadas**
```toml
[tool.poetry.dependencies]
python = "^3.9"
streamlit = "^1.28.0"
openai = "^1.3.0"
pydantic = "^2.5.0"
pytest = "^7.4.0"
```

## 📦 **Dependências Detalhadas**

### **Produção**
```toml
# Interface Web
streamlit = "^1.28.0"          # Framework web principal
streamlit-authenticator = "^0.2.3"  # Componentes de auth (opcional)

# IA e APIs
openai = "^1.3.0"              # Cliente oficial OpenAI
requests = "^2.31.0"           # HTTP requests (backup)

# Validação e Estruturas
pydantic = "^2.5.0"            # Validação de dados
dataclasses-json = "^0.6.0"    # Serialização dataclasses

# Utilitários
python-dotenv = "^1.0.0"       # Variáveis de ambiente (dev)
datetime = "*"                 # Manipulação de datas
typing-extensions = "^4.8.0"   # Type hints avançados
```

### **Desenvolvimento**
```toml
# Testes
pytest = "^7.4.0"              # Framework de testes
pytest-cov = "^4.1.0"          # Coverage de testes
pytest-mock = "^3.12.0"        # Mocking para testes

# Qualidade de Código
black = "^23.9.0"              # Formatação de código
flake8 = "^6.1.0"              # Linting
mypy = "^1.6.0"                # Type checking
isort = "^5.12.0"              # Organização de imports

# Documentação
sphinx = "^7.2.0"              # Geração de docs (opcional)
```

## 🏗️ **Estrutura do Projeto**

### **Layout Recomendado**
```
bdd-agent/
├── pyproject.toml             # Configuração Poetry
├── README.md                  # Documentação principal
├── .gitignore                 # Arquivos ignorados
├── .env.example               # Template variáveis ambiente
│
├── src/                       # Código fonte
│   ├── __init__.py
│   ├── main.py                # Entry point Streamlit
│   │
│   ├── auth/                  # Módulo autenticação
│   │   ├── __init__.py
│   │   └── authenticator.py
│   │
│   ├── config/                # Módulo configurações
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── session_manager.py
│   │
│   ├── bdd_generator/         # Módulo geração BDD
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── openai_client.py
│   │
│   ├── ui/                    # Módulo interface
│   │   ├── __init__.py
│   │   ├── pages/
│   │   │   ├── login.py
│   │   │   ├── main.py
│   │   │   └── config.py
│   │   └── components/
│   │       ├── header.py
│   │       └── footer.py
│   │
│   └── utils/                 # Utilitários
│       ├── __init__.py
│       ├── exceptions.py
│       └── validators.py
│
├── tests/                     # Testes
│   ├── __init__.py
│   ├── conftest.py            # Configurações pytest
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                      # Documentação
│   ├── api.md
│   ├── deployment.md
│   └── user_guide.md
│
└── memory-bank/               # Sistema de memória
    ├── projectbrief.md
    ├── productContext.md
    ├── activeContext.md
    ├── systemPatterns.md
    ├── techContext.md
    └── progress.md
```

## 🔧 **Configurações de Desenvolvimento**

### **pyproject.toml Base**
```toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "bdd-agent"
version = "0.1.0"
description = "Sistema inteligente para geração de BDD usando IA"
authors = ["PelizzAI <pelizzai@example.com>"]
readme = "README.md"
packages = [{include = "src"}]

[tool.poetry.scripts]
bdd-agent = "src.main:main"

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"
```

## 🌐 **Integração OpenAI**

### **Modelos Suportados**
```python
SUPPORTED_MODELS = {
    "gpt-4.1-mini": {
        "name": "GPT-4.1 Mini",
        "max_tokens": 4096,
        "cost_per_1k": 0.0001
    },
    "gpt-5-mini": {
        "name": "GPT-5 Mini",
        "max_tokens": 8192,
        "cost_per_1k": 0.0002
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "max_tokens": 4096,
        "cost_per_1k": 0.00015
    }
}
```

### **Cliente OpenAI**
```python
from openai import OpenAI
from typing import Optional

class OpenAIClient:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_bdd(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": BDD_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content
```

## 🎨 **Streamlit Configuration**

### **config.toml**
```toml
[global]
developmentMode = false

[server]
port = 8501
headless = true

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### **Secrets Management**
```toml
# .streamlit/secrets.toml (não commitado)
[auth]
default_username = "procer"
default_password = "Mbw/E5.r=\",6dE"

[openai]
default_api_key = "sk-..."
```

## 🧪 **Configuração de Testes**

### **conftest.py**
```python
import pytest
from unittest.mock import Mock
from src.config.settings import AppConfig
from src.bdd_generator.openai_client import OpenAIClient

@pytest.fixture
def app_config():
    return AppConfig(
        openai_api_key="test-key",
        selected_model="gpt-4o-mini"
    )

@pytest.fixture
def mock_openai_client():
    client = Mock(spec=OpenAIClient)
    client.generate_bdd.return_value = "Given...When...Then..."
    return client
```

## 🚀 **Scripts de Desenvolvimento**

### **Makefile**
```makefile
.PHONY: install test lint format run

install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run flake8 src tests
	poetry run mypy src

format:
	poetry run black src tests
	poetry run isort src tests

run:
	poetry run streamlit run src/main.py

dev:
	poetry run streamlit run src/main.py --server.runOnSave true
```

## 🔒 **Segurança e Boas Práticas**

### **Variáveis de Ambiente**
```bash
# .env (desenvolvimento)
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
OPENAI_API_KEY=sk-your-key-here
DEBUG=true
```

### **Validações de Entrada**
```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    text: str
    
    @validator('text')
    def validate_text(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Texto muito curto')
        if len(v) > 2000:
            raise ValueError('Texto muito longo')
        return v.strip()
```

## 📊 **Monitoramento e Logs**

### **Logging Configuration**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bdd-agent.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🎯 **Status de Implementação**

### **Configurado:**
- ❌ Poetry setup
- ❌ Estrutura de pastas
- ❌ Dependências instaladas
- ❌ Configurações base

### **Próximos Passos:**
1. 🔧 Inicializar projeto Poetry
2. 📦 Instalar dependências
3. 🏗️ Criar estrutura de pastas
4. ⚙️ Configurar ambiente desenvolvimento
5. 🧪 Setup inicial de testes

---

**Ambiente:** Desenvolvimento
**Python Version:** 3.9+
**Poetry Status:** ⏳ Pendente instalação