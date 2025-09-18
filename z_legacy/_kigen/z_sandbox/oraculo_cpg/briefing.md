oraculo_cpg

# 📋 Briefing para o Desenvolvimento do Oráculo CPG

## 🎯 Problema

Criar um sistema inteligente de documentação e consulta sobre arquivos armazenados em diretórios, com as seguintes capacidades:

1. **Fazer a varredura** de um diretório, suas pastas e subpastas (níveis indefinidos) e identificar todos os arquivos presentes.
2. **Extrair o conteúdo** desses arquivos usando ferramentas como `Docling`, convertendo-os para **Markdown** ou **JSON**.
3. **Analisar nomes de arquivos, nomes de pastas e conteúdo textual** para categorizar de forma inteligente os documentos.
4. **Gerar uma base de conhecimento estruturada** (Markdown/JSON) que permita:
   - Responder a perguntas complexas do usuário sobre o conteúdo arquivado.
   - Identificar automaticamente onde a resposta provavelmente se encontra.

---

## ✍️ Fluxo Esperado

### Primeira execução
- Varredura completa da estrutura de pastas e arquivos.
- Extração de conteúdo textual.
- Geração da base inicial de conhecimento.

### Consulta
- Recebimento de perguntas em linguagem natural.
- Localização da resposta mais provável dentro da estrutura.
- Retorno da resposta com contexto e caminho do documento correspondente.

---

## 📥 Entradas Esperadas

- Caminho do diretório a ser monitorado.
- Permissão para extrair e armazenar conteúdo dos arquivos.

---

## 📤 Saídas Esperadas

- Arquivo(s) `.json` e/ou `.md` com:
  - Categorias semânticas.
  - Metadados por arquivo.
  - Trechos chave de conteúdo extraído.
- Interface de consulta (CLI, API ou GUI leve) capaz de:
  - Receber pergunta do usuário.
  - Buscar a melhor correspondência.
  - Retornar resposta e fonte (arquivo/pasta).

---

## 💡 Exemplos de Casos de Uso

| Pergunta do Usuário | Comportamento Esperado |
|---------------------|------------------------|
| “Qual o valor do contrato com o Shopping Iguatemi?” | Buscar em `lojas_físicas > contratos > shopping > guatemir` e retornar cláusula relevante. |
| “Há cláusulas de exclusividade em nossos contratos?” | Listar todos os contratos com esse termo e indicar a pasta correspondente. |

---

## 🔗 Integrações necessárias

- `Docling`, `pdfplumber`, `unstructured` para extração de texto.
- `LangChain`, `FAISS`, `Weaviate` ou similar para indexação semântica.
- Interface de perguntas e respostas (terminal, API ou frontend com Streamlit).

---

## 🚀 Objetivo Final

Transformar o oraculo_cpg em um **oráculo documental**, capaz de oferecer **respostas confiáveis e rápidas** sobre qualquer conteúdo armazenado, com inteligência organizacional e adaptabilidade semântica.