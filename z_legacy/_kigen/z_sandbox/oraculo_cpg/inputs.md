## Checklist Validado de Inputs Necessários para o Oráculo CPG

| Input                  | Tipo     | Origem         | Status             | Observações                                             | Recomendações de Ajustes                                          |
|------------------------|----------|----------------|--------------------|--------------------------------------------------------|-----------------------------------------------------------------|
| diretório_monitorado   | string   | externo usuário | Presente           | Caminho do diretório a ser monitorado.                | Certifique-se de que o caminho é absoluto e que você tem permissão para acess-á-lo. |
| permissao_extracao    | boolean  | externo usuário | Presente           | Confirmação do usuário para extrair e armazenar conteúdo dos arquivos. | Solicite ao usuário a autorização e registre a permissão de forma segura. |
| estilo                 | arquivo  | externo usuário | Ausente            | O guia de tom e voz da marca é crucial para a categorização.  | Solicitar ao usuário que envie um arquivo .md com as diretrizes de estilo. |
| produtos               | arquivo  | externo usuário | Ausente            | Portfólio de produtos necessário para contextualização.      | Pedir ao usuário que forneça um arquivo .md contendo o portfólio de produtos. |
| marca                  | string   | externo usuário | Presente           | Domínio do site da marca para identificar informações contextuais.   | Garantir que o domínio está correto e atualizado.                          |
| guia_ferramentas      | url      | externo web    | Presente          | Acesso à documentação das ferramentas utilizadas.       | Visitar a URL e garantir que a documentação está acessível e clara. |
| conceito_agents        | url      | externo web    | Presente          | Acesso à documentação sobre conceitos de agentes.      | Confirmar que a documentação está atualizada e acessível.                    |
| docling                | url      | externo web    | Presente          | Necessário para a extração do conteúdo dos arquivos.   | Verifique a instalação da biblioteca accessando https://pypi.org/project/docling. |
| pdfplumber             | url      | externo web    | Presente          | Bibliotecas necessárias para PDF.                       | Confirmar instalação através da URL https://pypi.org/project/pdfplumber.     |
| unstructured           | url      | externo web    | Presente          | Importante para manipulação de arquivos não estruturados. | Checar instalação na URL https://pypi.org/project/unstructured.             |
| langchain              | url      | externo web    | Presente          | Fundamental para análise de perguntas e respostas.     | Verificar a documentação em https://docs.langchain.com/docs/.              |
| faiss                  | url      | externo web    | Presente          | Essencial para indexação semântica.                    | Confirmar que o repositório está acessível em https://github.com/facebookresearch/faiss.       |
| weaviate               | url      | externo web    | Presente          | Ideal para estruturas de conhecimento baseadas em embeddings. | Acessar https://weaviate.io/ para verificar a instalação.                |
| streamlit              | url      | externo web    | Presente          | Necessário para a interface do usuário.                | Confirmar acesso e instalação em https://docs.streamlit.io/.                |

### Notas e Considerações

1. **Caminho do Diretório**: É imprescindível validar o diretório informado, garantindo que ele contenha arquivos relevantes para a varredura. Utilize `os.path.exists()` para verificar a existência do caminho no sistema.
   
2. **Permissão de Extração**: Garantir que a extração de conteúdo respeite as normas de privacidade e as preferências do usuário é fundamental. Implementar um mecanismo para registrar essa permissão de forma segura.

3. **Estilo e Produtos**: Documentos que alinham o tom e voz da marca, assim como um portfólio de produtos, ajudam a estruturar o conhecimento de forma contextualizada. Solicitar esses documentos em formato claro e acessível.

### Coletas e Disponibilidades

- **Verificação de URLs**: As URLs fornecidas para as bibliotecas e ferramentas devem ser testadas regularmente para garantir que estão ativas e oferecem a documentação necessária.

- **Interface do Usuário**: Criar uma interface amigável para solicitação dos inputs ao usuário, garantindo explicações claras sobre a necessidade de cada informação.

Com esta análise detalhada, o Oráculo CPG está preparado para um desenvolvimento eficiente e estruturado, otimizando o processo de coleta de dados e garantindo um sistema robusto e responsivo.