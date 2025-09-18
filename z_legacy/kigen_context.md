# 📚 Kigen - Contexto Atual

## 🎯 Identidade
**Kigen** é uma plataforma de diagnóstico e geração de soluções inteligentes para automação de problemas.
> "Decidir estrategicamente se um problema deve ser resolvido através de uma crew multiagente (CrewAI) ou por funções Python simples."

## 🛠️ Estrutura Funcional
- **Agentes:**
  - avaliador_problemas
  - pesquisador_solucoes
  - decisor_estrategico
  - especialista_solucoes

- **Tasks:**
  - Diagnóstico inicial
  - Busca de soluções
  - Avaliação da abordagem
  - Verificação da recomendação
  - (Se Funções Python) Geração modular de funções

- **Fluxo de decisão:**
  - Baseado no arquivo {recomendacao}.
  - Se "Funções Python", prossegue.
  - Se "Crew", interrompe.

- **Arquivos principais:**
  - main.py
  - crew.py
  - agents.yaml
  - tasks.yaml
  - recomendacao.md

## 🧩 Inputs Disponíveis
- problema
- crewai_documentacao
- crewai_conceitos
- crewai_crews
- python_docs
- python_patterns
- awesome_python
- bibliotecas
- docling_docs
- langchain_docs
- streamlit_docs
- github
- stack_overflow

## 🎯 Filosofia de Desenvolvimento
- Simplicidade: Soluções simples sempre que possível.
- Modularidade: Arquivos separados, funções reutilizáveis.
- Eficiência: Não reinventar a roda se já houver solução pública.
- Nivelamento: Análise imparcial entre CrewAI e bibliotecas Python.
- Agilidade: Fluxos leves e adaptáveis para qualquer problema.

## 📦 Estado Atual
- Diagnóstico funcionando.
- Geração de funções Python implementada.
- Fluxo condicional baseado em {recomendacao} implementado.
- Inputs atualizados e nivelados.
- Estrutura modular e escalável.