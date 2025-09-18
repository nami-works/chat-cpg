# Checklist de Inputs Obrigatórios para a Solução do Cálculo de Política Comercial com LLM

Abaixo está a verificação dos inputs necessários conforme identificado no briefing e proposta de fluxo. Cada input foi avaliado quanto à presença, formato e validade, juntamente com recomendações para correções, quando necessário.

| Input                                     | Status     | Formato Esperado             | Observações e Recomendações                                                                                                                                                     |
|-------------------------------------------|------------|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Dicionário de premissas                   | Presente   | Dict (chaves: `desconto`, `frete_vendas`, `influencia`) | Certifique-se de que todas as chaves estão presentes e com valores numéricos (ex: `{"desconto": 15, "frete_vendas": 0.1, "influencia": 0.05}`).                                   |
| Lista de novas linhas de despesa          | Ausente    | List (de str)                | Esta lista é opcional, mas se quiser utilizá-la, adicione novas despesas no formato: `["3% de comissão de marketplace", "5% de marketing"]`.                                     |
| Comandos via texto natural                | Presente   | String                        | Certifique-se de que os comandos estão claros e seguidos pelo formato esperado de ajustes (ex: “Reduza o imposto para 8%”).                                                      |
| Chave da API OpenAI                       | Presente   | String                        | Verifique a validade da chave. Se não estiver funcionando, adicione sua chave no arquivo `.env` com o nome `OPENAI_API_KEY`.                                                    |
| Configuração do ambiente de execução      | Ausente    | Configuração de dependências  | Certifique-se de que as bibliotecas necessárias (OpenAI, NumPy, Pandas, Streamlit, LangChain) estão instaladas. Use o comando `pip install openai numpy pandas streamlit langchain`. |
| Estrutura de logging                       | Ausente    | Implementação de logging      | Implemente um sistema de logging, por exemplo usando a biblioteca `logging` do Python, para registrar as decisões e classificações da LLM.                                       |

## Notas Gerais

- Todos os inputs devem ser validados antes da execução do código. Isso pode ser feito por meio de testes que asseguram se cada input é do tipo e formato correto.
- Recomenda-se o uso de um bloco de código para validação que possa levantar exceções claras caso algum input esteja ausente ou mal formatado. Exemplo:
  ```python
  def validar_inputs(dados):
      if not isinstance(dados, dict) or 'desconto' not in dados:
          raise ValueError("Dicionário de premissas inválido: deve incluir 'desconto'.")
      # Adicione verificações adicionais conforme necessário.
  ```

## Sugerindo Próximos Passos

1. Confirme a presença da chave da API no ambiente e que você pode conectar-se à OpenAI API.
2. Caso a lista de novas linhas de despesa seja utilizada, adicione exemplos relevantes para garantir a funcionalidade de classificação.
3. Implemente um sistema de logging para rastrear as classificações e decisões tomadas pela LLM.
4. Valide o formato dos inputs e documente onde cada um deles é definido e coletado, garantindo que futuros desenvolvedores possam entender e manter o sistema facilmente.

A validação criteriosa dos inputs e o cuidado na configuração do ambiente são passos críticos para garantir uma execução suave e a minimização de erros no cálculo da política comercial.