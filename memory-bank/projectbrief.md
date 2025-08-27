# 📋 Project Brief - BDD Agent

**Última atualização:** 2024-12-19 14:30:00

---

## 🎯 **Objetivo do Projeto**

Criar um sistema em Python que auxilie na geração de BDD (Behavior Driven Development) utilizando inteligência artificial.

## 📝 **Escopo Funcional**

### **Funcionalidades Principais:**

1. **Sistema de Autenticação**
   - Login: `procer`
   - Senha: `Mbw/E5.r=",6dE`
   - Tela de login simples e segura

2. **Geração de BDD com IA**
   - Campo de entrada para texto do usuário
   - Integração com OpenAI API
   - Geração automática de cenários BDD em formato Gherkin
   - Funcionalidade de copiar resultado

3. **Tela de Configurações**
   - Campo para API Key da OpenAI
   - Seleção de modelos de IA:
     - gpt-4.1-mini
     - gpt-5-mini
     - gpt-4o-mini
     - Campo customizável para outros modelos
   - Persistência no localStorage

4. **Validações e Alertas**
   - Verificação de API Key configurada
   - Verificação de modelo selecionado
   - Alertas informativos ao usuário

## 🛠️ **Stack Tecnológica**

- **Linguagem:** Python
- **Gerenciador de Pacotes:** Poetry
- **Framework Web:** Streamlit
- **IA:** OpenAI API
- **Persistência:** LocalStorage (via Streamlit session state)

## 📚 **Referência BDD**

Baseado na metodologia BDD conforme: https://www.dtidigital.com.br/blog/bdd-como-metodologia-agil

### **Estrutura Gherkin:**
- **Given (Dado que):** Condições e pré-condições
- **When (Quando):** Eventos ou ações
- **Then (Então):** Resultados esperados

## 🎨 **Requisitos de Interface**

- Interface limpa e intuitiva
- Navegação simples entre telas
- Feedback visual para ações do usuário
- Responsividade básica

## 🔒 **Requisitos de Segurança**

- Autenticação básica implementada
- API Keys armazenadas de forma segura
- Validação de entrada de dados

---

**Status:** 🟡 Planejamento Inicial
**Prioridade:** P1 - Alta
**Estimativa:** 2-3 dias de desenvolvimento