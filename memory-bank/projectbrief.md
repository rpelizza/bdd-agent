# 📋 Project Brief - BDD Agent

**Última atualização:** 2025-08-27 16:19:05

---

## 🎯 **Escopo e Requisitos Fundamentais**

### **Nome do Projeto**
**BDD Agent** - Sistema Python para geração de BDD com IA

### **Desenvolvedor**
Rafael Pelizza (PelizzAI)

### **Versão Atual**
0.1.0

---

## 🌟 **Objetivo Principal**

Desenvolver uma aplicação web que **automatiza a geração de cenários BDD (Behavior Driven Development)** a partir de histórias de usuário em linguagem natural, utilizando Inteligência Artificial (OpenAI) para criar testes estruturados no formato Gherkin.

---

## 📊 **Requisitos Funcionais**

### **RF01 - Interface Web Intuitiva**
- Interface Streamlit responsiva e amigável
- Entrada de texto para histórias de usuário
- Configurações avançadas (criatividade, tipo de cenários)
- Download de arquivos .feature

### **RF02 - Geração Inteligente de BDD**
- Conversão de linguagem natural para formato Gherkin
- Suporte a cenários positivos, negativos e casos extremos
- Validação de estrutura BDD (Dado, Quando, Então)
- Múltiplos cenários por história

### **RF03 - Integração OpenAI**
- Suporte a múltiplos modelos (GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo)
- Configuração de temperatura para criatividade
- Tratamento de erros e timeout
- Validação de API key

### **RF04 - Processamento e Validação**
- Parser de conteúdo Gherkin
- Classificação de tipos de cenário
- Extração de metadados (feature name, description)
- Formatação para download

---

## 📊 **Requisitos Não-Funcionais**

### **RNF01 - Performance**
- Timeout de 30s para requisições OpenAI
- Interface responsiva sem travamentos
- Logging estruturado para debugging

### **RNF02 - Usabilidade**
- Interface em português brasileiro
- Feedback visual durante processamento
- Validação em tempo real de inputs

### **RNF03 - Segurança**
- API key mascarada na interface
- Validação de formato de chaves
- Não persistência de credenciais

### **RNF04 - Qualidade**
- Cobertura de testes configurada
- Linting automático (Black, Flake8, MyPy)
- Tipagem estrita com Pydantic

---

## 🏗️ **Arquitetura Definida**

### **Stack Tecnológico**
- **Backend**: Python 3.9+
- **Interface**: Streamlit 1.28+
- **IA**: OpenAI API 1.3+
- **Validação**: Pydantic 2.5+
- **Gerenciamento**: Poetry
- **Testes**: Pytest + Coverage

### **Estrutura Modular**
```
src/
├── bdd_generator/     # Core BDD generation
├── auth/             # Autenticação (futuro)
├── config/           # Configurações
├── ui/              # Componentes UI
└── utils/           # Utilitários
```

---

## 🎯 **Escopo de Entrega**

### **Funcionalidades Implementadas**
✅ Interface Streamlit funcional  
✅ Integração completa OpenAI  
✅ Geração de cenários BDD  
✅ Parser Gherkin  
✅ Download de arquivos .feature  
✅ Configurações avançadas  
✅ Tratamento de erros  

### **Funcionalidades Planejadas**
🔄 Sistema de autenticação  
🔄 Histórico de gerações  
🔄 Templates personalizados  
🔄 Exportação múltiplos formatos  
🔄 Integração com ferramentas BDD  

---

## 📈 **Métricas de Sucesso**

### **Técnicas**
- Cobertura de testes ≥ 85%
- Tempo de resposta ≤ 30s
- Zero erros críticos de produção
- Tipagem 100% MyPy compliant

### **Usuário**
- Interface responsiva e intuitiva
- Cenários BDD válidos e úteis
- Facilidade de configuração
- Feedback claro em erros

---

## 🔒 **Restrições e Limitações**

### **Técnicas**
- Dependência da API OpenAI
- Limite de tokens por requisição (2000)
- Python 3.9+ obrigatório
- Conexão internet necessária

### **Negócio**
- Custos variáveis por uso da OpenAI
- Disponibilidade dependente da API externa
- Qualidade depende do modelo IA utilizado

---

## 📅 **Timeline e Marcos**

### **Fase 1 - MVP Concluído** ✅
- Interface básica funcional
- Geração de cenários BDD
- Integração OpenAI operacional

### **Fase 2 - Melhorias** 🔄
- Sistema de autenticação
- Persistência de dados
- Templates avançados

### **Fase 3 - Integração** 📋
- APIs para ferramentas externas
- Webhooks e automações
- Dashboard de métricas

---

**📌 IMPORTANTE**: Este project brief reflete o estado atual analisado do código em 2025-08-27. Todas as funcionalidades listadas como implementadas foram verificadas na base de código existente.
