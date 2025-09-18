# Checklist de Inputs para a Crew ChizuKaki

| Input                     | Tipo      | Origem           | Status    | Anotações                                                  |
|---------------------------|-----------|------------------|-----------|-----------------------------------------------------------|
| ceps_shoppings            | dicionário| externo fixo     | Presente  | Dicionário criado conforme a instrução de coleta.         |
| base_ceps                 | arquivo   | externo usuário   | Ausente   | Solicitar ao usuário um arquivo CSV com coluna `cep`.     |
| coordenadas_geograficas   | função    | externo web      | Presente  | A API foi identificada e está pronta para uso (ex: ViaCEP).|
| distancia_geodesica       | biblioteca| externo web      | Presente  | Biblioteca geopy do PyPI encontrada e verificada para uso. |
| relatorio_distancias       | arquivo   | interno          | Ausente   | Criar o arquivo CSV a ser gerado, dependendo dos inputs.  |
| documentação da API       | url       | externo web      | Presente  | Documentação acessada e disponível para consulta.         |
| exemplos de uso           | url       | externo web      | Presente  | Repositórios de GitHub e StackOverflow encontrados.       |
| guia_ferramentas         | url       | externo web      | Presente  | Acesso ao guia disponível para criação de ferramentas.     |
| conceito de planejamento   | url       | externo web      | Presente  | Diretrizes consultadas e em conformidade.                  |

## Resumo das Ações Necessárias:
1. **Solicitar ao usuário** a coleta do arquivo CSV (`base_ceps`) contendo a coluna `cep` dos clientes.
2. **Gerar o arquivo CSV** de resultados (`relatorio_distancias`) após a execução do processo.

Essas etapas são essenciais para garantir que todos os dados necessários estejam disponíveis e em conformidade com os formatos e recomendações definidos.