# BDD Agent

Sistema Python para geração de BDD (Behavior Driven Development) com IA.

## Descrição

O BDD Agent é uma ferramenta que utiliza inteligência artificial para auxiliar na criação e gerenciamento de cenários BDD, facilitando o processo de desenvolvimento orientado por comportamento.

## Tecnologias

- Python 3.9+
- Streamlit (Interface Web)
- OpenAI (IA)
- Pydantic (Validação de dados)
- Poetry (Gerenciamento de dependências)

## Instalação

```bash
# Instalar dependências
poetry install

# Executar aplicação
poetry run streamlit run src/main.py
```

## Estrutura do Projeto

```
bdd-agent/
├── src/
│   ├── main.py
│   ├── core/
│   ├── ui/
│   └── utils/
├── tests/
├── docs/
└── pyproject.toml
```

## Desenvolvimento

```bash
# Executar testes
poetry run pytest

# Formatação de código
poetry run black src tests

# Linting
poetry run flake8 src tests

# Type checking
poetry run mypy src
```

## Licença

MIT License