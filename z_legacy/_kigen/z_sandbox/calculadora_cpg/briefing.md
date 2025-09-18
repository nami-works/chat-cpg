calculadora_cpg

# Briefing Kigen - Cálculo de Política Comercial com LLM

## Problema a ser Resolvido

Desenvolver uma solução que automatize o cálculo da política comercial de vendas em novos canais com base em premissas percentuais fornecidas pelo usuário. A solução deve calcular:

- Receita líquida
- CMV (produto, frete, embalagem)
- Margem bruta
- Despesas variáveis (vendas, marketing, sistemas)
- Margem de contribuição final

Além disso, o sistema deve ser capaz de:

1. Identificar e classificar **novas despesas** (ex: comissão de marketplace) com apoio de LLM.
2. Permitir uma **interface conversacional** para ajustes de parâmetros, simulações e explicações.

## Componentes Esperados

### 1. Funções Python determinísticas

Para todos os cálculos financeiros conforme estrutura enviada no briefing anterior.

### 2. Classificador via LLM

Função que, ao receber uma nova linha de despesa como input, retorne:
- Sugestão de grupo (ex: "despesas de marketing")
- Justificativa em texto natural

### 3. Camada de interpretação por linguagem natural

Permitir que usuários façam perguntas ou ajustes usando frases como:
- “Simule com 15% de desconto e 5% de mídia online”
- “Adicione 3% de comissão de marketplace”
- “Qual seria a margem se o frete subisse para 12%?”

## Inputs esperados

- Dicionário de premissas com chaves padronizadas (ex: `desconto`, `frete_vendas`, `influencia`)
- Lista opcional de novas linhas de despesa a classificar
- Comandos via texto natural (ex: “Reduza o imposto para 8%”)

## Outputs esperados

- Tabela com todas as etapas e valores (%)
- Valor final da margem de contribuição
- Log de interpretações LLM (classificações e comandos interpretados)

## Requisitos Técnicos

- Separação clara entre funções determinísticas e funções de interpretação
- Uso de OpenAI API para classificação e interface conversacional
- Testes unitários para todas funções de cálculo
- Logging das decisões da LLM para auditoria

## Riscos e Cuidados

| Risco                                     | Mitigação                                     |
|------------------------------------------|-----------------------------------------------|
| Classificação incorreta de nova linha    | Requer confirmação do usuário antes de aplicar |
| Ambiguidade de comandos em linguagem natural | Requisição de confirmação se interpretação for incerta |
| Dependência de LLM                       | Incluir fallback de classificação por regras simples |

## Proposta de Fluxo no Kigen

1. `analisar_problema`: identificar etapas e blocos financeiros.
2. `mapear_funcoes`: decompor cada etapa em função.
3. `buscar_padroes_funcoes`: procurar referências de cálculo percentual e estrutura de dicionário dinâmico.
4. `escrever_funcoes`: gerar `calcular_margens.py`.
5. `escrever_funcoes` (extra): gerar `interpretador_llm.py`.
6. `testar_funcoes`: criar `teste_margens.py`.
