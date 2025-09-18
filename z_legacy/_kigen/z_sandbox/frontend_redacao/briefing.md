front-end_streamlit

# 📋 Briefing para Geração do Front-End em Streamlit

## 🎯 Problema
Construir uma aplicação Streamlit que permita aos usuários:
- Inserir até **5 temas** para produção de blog posts.
- Visualizar imediatamente os temas inseridos.
- **Excluir** temas inseridos clicando em um botão de remoção (ícone "X" ao lado de cada tema).
- Após concluir a lista, enviar os temas coletados para iniciar a crew de Redação.

## ✍️ Fluxo Esperado
1. Campo de texto para digitação de um tema.
2. Ao digitar e confirmar:
   - O tema é adicionado a uma lista visível abaixo do input.
   - Cada tema na lista aparece com um botão **[X]** à direita para exclusão individual.
3. **Limite máximo de 5 temas**.
   - Quando atingir 5 temas, desabilitar o campo de input.
4. **Limite de caracteres por tema: 150 caracteres**.
   - Se o usuário tentar digitar mais de 150 caracteres, bloquear a inserção ou truncar.
5. Botão “Enviar Temas”:
   - Constrói um dicionário no formato:
     ```python
     temas = {
         "tema_1": "Primeiro tema inserido",
         "tema_2": "Segundo tema inserido",
         ...
     }
     ```
   - Executa o kickoff da crew `Redacao`, enviando os temas como parte dos inputs.

## 📥 Entradas Esperadas
- Texto livre (`tema`) limitado a 150 caracteres por tema.
- Operação de exclusão sobre itens já adicionados.

## 📤 Saídas Esperadas
- Dicionário `temas` organizado e pronto para ser utilizado como input no `Redacao().crew().kickoff(inputs=inputs)`.
- Mensagem visual de confirmação de envio ou alerta em caso de erro.

## 🔗 Integrações Necessárias
- Inputs complementares (carregados dos arquivos já existentes):
  - `estilo`: Conteúdo do arquivo `estilo.md`
  - `marca`: URL da marca
  - `produtos`: Conteúdo do arquivo `produtos.md`
  - `blog`: URL do blog
  - `benchmarks`: Benchmarks da marca

- Função de execução:
  ```python
  Redacao().crew().kickoff(inputs=inputs)

