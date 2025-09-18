## Checklist de Inputs Necessários para Geração Automatizada de Alt Text

| Input                                  | Status         | Formato Esperado                   | Anotações e Recomendações                                          |
|----------------------------------------|----------------|------------------------------------|--------------------------------------------------------------------|
| `Export_2025-05-21_120208.xlsx`       | Presente       | Arquivo Excel (.xlsx)             | Certifique-se de que a planilha contém a coluna `link`.           |
| `coluna_links`                        | Presente       | String                             | Deve referenciar a coluna `link` na planilha mencionada.          |
| `produtos_base`                       | Ausente        | Arquivo CSV ou Excel (.csv ou .xlsx) | Adicione um arquivo com informações sobre produtos já classificados para análises. Exemplo: `produtos_classificados.xlsx` |
| `google_vision_api_key`               | Ausente        | String                             | Adicione a chave da API do Google Vision no arquivo de configuração ou como variável de ambiente. |
| `azure_vision_api_key`                | Ausente        | String                             | Insira a chave de assinatura da API do Azure Computer Vision conforme documentação. |
| `openai_clip_model`                   | Presente       | String                             | Verifique se o modelo CLIP do OpenAI está acessível e documentado em seu ambiente. |
| `huggingface_model`                   | Presente       | String                             | Escolha um modelo do Hugging Face para uso, conforme o repositório disponível (ex: `Salesforce/blip-image-captioning-base`). |
| `idioma`                               | Ausente        | String                             | Defina o idioma que será utilizado nas descrições geradas. Exemplo: `pt` para português. |
| `formato_saida`                       | Presente       | String                             | Especificar que a coluna `Alt Text` da planilha deve ser preenchida. |
| `verificar_link()`                    | Presente       | Função (implementação no código)  | Implementar a função para checar a validade dos links antes do processamento. |

### Anotações Finais:
1. **Arquivos e Chaves**: Certifique-se de que todos os arquivos e chaves de API estão corretamente configurados e acessíveis. Recomendamos que as chaves de API sejam armazenadas em um arquivo `.env` ou em variáveis de ambiente para segurança.
   
2. **Validação de Links**: A função `verificar_link()` deve ser implementada para garantir que todos os links na coluna `link` sejam acessíveis antes de qualquer processamento.

3. **Base de Produtos**: A ausência do arquivo de produtos poderá resultar em falhas na validação do conteúdo das imagens. Priorize a aquisição deste dado.

4. **Documentação de Modelos**: Assegure-se de seguir a documentação específica de integração para cada API utilizada, conforme encontrado nas respectivas documentações online.

5. **Testes**: Após garantir a presença e integridade dos dados, inicie o processo com um subconjunto de dados para validar a infraestrutura de geração de Alt Text com a precisão desejada.

Estes passos garantirão que a execução do projeto ocorra sem interrupções e com resultados de alta qualidade, melhorando a acessibilidade e a SEO conforme planejado.