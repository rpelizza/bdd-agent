# 🔧 Tech Context - BDD Agent (Modular)

**Última atualização:** 2025-08-27 16:19:05

---

## 📋 **Módulos Disponíveis**

Este arquivo foi preparado para ser modular conforme a regra de 500 linhas do Memory Bank.

### **🎯 Contexto Técnico Consolidado:**

#### **Stack Principal**
- **Linguagem**: Python 3.9+ (com restrições específicas)
- **Interface**: Streamlit 1.28.0
- **IA**: OpenAI API 1.3.0
- **Validação**: Pydantic 2.5.0
- **Configuração**: python-dotenv 1.0.0

#### **Ferramentas de Desenvolvimento**
- **Gerenciamento**: Poetry (pyproject.toml)
- **Testes**: Pytest 7.4.0 + Coverage 4.1.0
- **Formatação**: Black 23.9.0 (line-length=88)
- **Linting**: Flake8 6.1.0
- **Tipagem**: MyPy 1.6.0 (strict mode)
- **Imports**: isort 5.12.0

---

## 🐍 **Python Core Configuration**

### **Versão e Restrições**
```toml
python = ">=3.9,<3.9.7 || >3.9.7,<4.0"
```
**Nota**: Exclusão específica da versão 3.9.7 - possível incompatibilidade conhecida

### **Configuração MyPy (Strict)**
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
strict_equality = true
```

### **Padrões de Código**
```toml
[tool.black]
line-length = 88
target-version = ['py39']

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
```

---

## 🖥️ **Streamlit Interface Stack**

### **Versão e Configuração**
```python
streamlit = "^1.28.0"

# Configuração de página
st.set_page_config(
    page_title="BDD Agent - Gerador de Cenários",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

### **Componentes Utilizados**
- **Layout**: Columns, Sidebar, Container
- **Inputs**: text_area, text_input, selectbox, checkbox, number_input, slider
- **Outputs**: markdown, success, error, warning, info
- **Actions**: button, download_button
- **UI**: spinner, divider, header, subheader

### **Features Avançadas**
- **Session State**: Para persistência de configurações
- **File Download**: Geração de arquivos .feature
- **Real-time Validation**: Validação de inputs em tempo real

---

## 🤖 **OpenAI Integration Stack**

### **API Configuration**
```python
openai = "^1.3.0"

# Modelos Suportados
SUPPORTED_MODELS = {
    "gpt-4o-mini": {"name": "GPT-4o Mini", "max_tokens": 4096, "cost_per_1k": 0.00015},
    "gpt-4.1-mini": {"name": "GPT-4.1 Mini", "max_tokens": 4096, "cost_per_1k": 0.0001},
    "gpt-5-mini": {"name": "GPT-5 Mini", "max_tokens": 8192, "cost_per_1k": 0.0002},
    "gpt-4.1-nano": {"name": "GPT-4.1 Nano", "max_tokens": 2048, "cost_per_1k": 0.00005},
}
```

### **Client Configuration**
```python
class OpenAIConfig(BaseModel):
    api_key: str
    model: str = "gpt-4o-mini"
    max_tokens: int = 2000
    temperature: float = 0.3
    timeout: int = 30
```

### **Error Handling**
- Timeout management (30s default)
- API key validation
- Token usage logging
- Graceful degradation

---

## 📊 **Data Validation Stack (Pydantic)**

### **Core Models**
```python
pydantic = "^2.5.0"

class BDDScenario(BaseModel):
    title: str = Field(..., description="Título do cenário")
    steps: List[str] = Field(..., description="Lista de passos")
    scenario_type: str = Field(default="positive", description="Tipo")

class BDDResponse(BaseModel):
    feature_name: str = Field(..., description="Nome da funcionalidade")
    feature_description: str = Field(..., description="Descrição")
    scenarios: List[BDDScenario] = Field(..., description="Cenários")
    gherkin_content: str = Field(..., description="Conteúdo Gherkin")
```

### **Validation Benefits**
- Runtime type checking
- Automatic documentation
- JSON serialization
- IDE support com autocomplete

---

## 🧪 **Testing Stack**

### **Core Testing Framework**
```toml
pytest = "^7.4.0"
pytest-cov = "^4.1.0"

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --cov=src --cov-report=term-missing --cov-report=html"
testpaths = ["tests"]
```

### **Test Structure**
```
tests/
├── conftest.py        # Fixtures globais
├── fixtures/          # Fixtures específicas
├── unit/             # Testes unitários
└── integration/      # Testes de integração
```

### **Mock Strategy**
```python
@pytest.fixture
def mock_openai_client() -> Mock:
    """Cliente OpenAI mockado para testes"""
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Cenário BDD exemplo"))]
    )
    return mock_client
```

---

## 📁 **Project Structure**

### **Source Organization**
```
src/
├── __init__.py
├── main.py           # Entry point Streamlit
├── bdd_generator/    # Core BDD logic
│   ├── __init__.py
│   ├── generator.py
│   └── openai_client.py
├── auth/            # Authentication (future)
├── config/          # Configuration management
├── ui/              # UI components
│   ├── components/
│   └── pages/
└── utils/           # Utilities
```

### **Configuration Files**
- **pyproject.toml**: Poetry + tools configuration
- **poetry.lock**: Dependency lock file
- **.gitignore**: Version control exclusions
- **README.md**: Project documentation

---

## 🔧 **Development Workflow**

### **Dependency Management**
```bash
# Install dependencies
poetry install

# Add new dependency
poetry add package-name

# Update dependencies  
poetry update

# Show dependency tree
poetry show --tree
```

### **Code Quality Pipeline**
```bash
# Format code
poetry run black src/
poetry run isort src/

# Type checking
poetry run mypy src/

# Linting
poetry run flake8 src/

# Run tests
poetry run pytest
```

### **Coverage Requirements**
- **Minimum**: 85% code coverage
- **Reports**: Terminal + HTML
- **CI Integration**: Configured for automated checks

---

## 🚀 **Deployment Considerations**

### **Environment Setup**
```python
# python-dotenv para variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Configurações sensíveis via env vars
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### **Streamlit Deployment**
- **Local**: `streamlit run src/main.py`
- **Cloud**: Compatível com Streamlit Cloud
- **Docker**: Containerização futura planejada

### **Performance Considerations**
- **Memory**: Baixo uso, apenas texto processing
- **CPU**: Leve, processamento na OpenAI API
- **Network**: Dependente da qualidade de conexão
- **Storage**: Mínimo, sem persistência de dados

---

## 🔒 **Security Stack**

### **API Key Management**
- Validation de formato básico
- Masking na interface
- Não persistência em storage local
- Sanitização de inputs

### **Dependencies Security**
```bash
# Security audit (futuro)
poetry audit

# Update security patches
poetry update --dry-run
```

---

## 📈 **Monitoring and Logging**

### **Logging Configuration**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Structured logging
logger.info(f"Gerando {num_scenarios} cenários para: {user_story[:50]}...")
logger.error(f"Erro na API OpenAI: {str(e)}")
```

### **Metrics Tracking**
- Token usage per request
- Response time monitoring
- Error rate tracking
- User interaction patterns

---

## 🔄 **Future Technical Improvements**

### **Planned Enhancements**
1. **FastAPI Backend**: Para APIs mais robustas
2. **Database Integration**: PostgreSQL ou SQLite
3. **Redis Caching**: Para cenários frequentes
4. **Docker Containerization**: Para deployment
5. **CI/CD Pipeline**: GitHub Actions
6. **Monitoring**: Prometheus + Grafana

### **Architecture Evolution**
1. **Microservices**: Separar geração BDD
2. **Event Driven**: Para processamento assíncrono
3. **WebSockets**: Para real-time updates
4. **GraphQL**: Para APIs flexíveis

---

**🔧 STACK ATUAL**: Python moderno com foco em qualidade de código, testes rigorosos e interface de usuário intuitiva. Base sólida para escalabilidade futura.

---

## 🎯 **Navegação Rápida**

**NOTA**: Esta é a versão consolidada do techContext. Caso este arquivo cresça além de 500 linhas, será modularizado em:
- `tech/python.md` - Configurações Python específicas
- `tech/streamlit.md` - Interface e componentes UI
- `tech/openai.md` - Integração IA e modelos
- `tech/testing.md` - Framework de testes
- `tech/deployment.md` - Deploy e infraestrutura
