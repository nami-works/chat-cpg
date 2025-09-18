extracao_seo_simples

# 📋 Briefing Simplificado - Extração Semântica para SEO com Código e APIs

## 🎯 Problema
Extrair campos semânticos relevantes a partir de uma **palavra-chave ou frase curta** com o objetivo de apoiar a **otimização de artigos de blog** e **páginas de produto**.

---

## 🧠 Entrada
- `tema`: palavra-chave ou frase curta (ex: "shampoo detox")

---

## 📤 Saída Esperada (formato simples)
Dicionário Python contendo:

```python
{
  'palavra_chave_base': 'shampoo detox',
  'relacionadas_google': [...],
  'long_tail_keywords': [...],
  'intencao_busca': 'informacional' ou 'comercial',
  'titulos_sugeridos': [...],
  'h1': 'Título otimizável',
  'h2': ['Subtítulo 1', 'Subtítulo 2']
}
```

---

## 🔌 Fontes e APIs Utilizadas
- Google Autocomplete (via scraping simples ou API pública)
- AnswerThePublic (se possível)
- People Also Ask (via scraping)
- Algoritmos heurísticos para detectar intenção de busca (baseado em sufixos como "como", "onde", "melhor", "comprar")

---

## 🛠️ Sugestão de Pipeline Python

1. **Função `get_google_suggestions(tema)`**  
   → retorna sugestões do Google autocomplete.

2. **Função `classificar_intencao(termos)`**  
   → classifica como informacional ou comercial.

3. **Função `gerar_headers(titulo_base)`**  
   → gera H1 e H2 a partir da palavra-chave com templates simples.

4. **Função `gerar_titulos_otimizados(tema)`**  
   → retorna frases prontas para blog (usando modelos fixos ou LLM via API).

---

## 💡 MVP Inicial
- Input: `"shampoo detox"`
- Output:
```python
{
  "palavra_chave_base": "shampoo detox",
  "relacionadas_google": ["shampoo detox caseiro", "shampoo detox para oleosidade", ...],
  "long_tail_keywords": ["como fazer shampoo detox natural", "shampoo detox barato para cabelos oleosos"],
  "intencao_busca": "informacional",
  "titulos_sugeridos": ["Como Escolher o Melhor Shampoo Detox para Seu Tipo de Cabelo"],
  "h1": "Tudo sobre Shampoo Detox",
  "h2": ["Para que serve?", "Como usar?", "Vantagens e Cuidados"]
}
```

---

## ⚠️ Riscos
| Risco | Mitigação |
|-------|-----------|
| APIs instáveis ou bloqueadas | Adicionar fallback por scraping |
| Baixa qualidade nos títulos gerados | Refinar templates com base em benchmarks |
| Intenção mal classificada | Ajustar com base em logs reais |

---

## 🧪 Observações Técnicas
- Ideal para rodar como script Jupyter ou backend Streamlit
- Opcionalmente pode usar OpenAI GPT via API para melhorar a geração de títulos e headers