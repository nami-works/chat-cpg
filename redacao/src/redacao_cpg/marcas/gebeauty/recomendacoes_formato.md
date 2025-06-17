## 📝 Orientação para geração de conteúdo HTML otimizado para Shopify

**Objetivo:**  
Gerar um **texto final limpo, claro, uniforme e fiel às bases de conhecimento**, pronto para publicação direta no blog da Shopify **sem necessidade de nova revisão**.

O conteúdo deve ser entregue em **formato HTML técnico e otimizado para Shopify**, obedecendo às seguintes diretrizes:

---

### ✅ Estrutura e marcação

1. **Usar exclusivamente** tags semânticas como:
   - `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<li>`, `<strong>`, `<em>`.
   - ❗ **Não utilizar `<h1>`**, pois o Shopify **gera automaticamente** o `<h1>` com base no campo “Title” do post.

2. Manter a **hierarquia correta**:  
   - `<h2>` para as principais seções do conteúdo.  
   - `<h3>` ou `<h4>` para subtópicos, se necessário.

3. Não incluir quaisquer elementos visuais, como:  
   - Estilos inline (`style=""`)  
   - Cores  
   - Fontes personalizadas  
   - Tamanhos específicos

4. Não inserir elementos de estrutura global, como:  
   - `<!DOCTYPE html>`  
   - `<html>`  
   - `<head>`  
   - `<meta>`  
   - `<title>`  
   - `<body>`

Esses elementos são **gerados automaticamente pelo Shopify** e **não devem ser duplicados**.

---

### ✅ Conteúdo e SEO

5. O conteúdo deve:
   - Começar com uma **introdução clara**.
   - Ser dividido em seções bem definidas, facilitando a leitura e a escaneabilidade.
   - Usar **palavras-chave relevantes** para SEO de forma natural.

6. Sempre que possível, incluir **chamadas para ação (CTAs)** claras e objetivas no final.

7. ❗ **Não inserir** `<meta name="description">` ou `<meta name="keywords">`.  
Essas informações serão configuradas **diretamente no painel do Shopify**, na seção “Search engine listing preview”.

---

### ✅ Outros pontos importantes

8. Evitar links que não sejam essenciais.  
Se inserir, usar a estrutura:  
`<a href="URL">Texto</a>`  
Sem `target` ou `rel` extras.

9. Usar **listas** (`<ul>`, `<ol>`) para destacar pontos importantes quando necessário.

10. **Não incluir scripts, iframes ou elementos interativos**.

---

### ✅ Formatação de ênfase

11. Usar `<strong>` para destacar termos importantes ou conceitos-chave.

12. Usar `<em>` para marcar ênfase leve ou expressões específicas.

---

### ✅ Exemplos de tags permitidas

```html
<h2>Como usar os boosters da GE Beauty</h2>
<p>Os boosters oferecem personalização e tratamento intensivo para diferentes tipos de cabelo.</p>

<strong>Benefícios principais:</strong>
<ul>
  <li>Hidratação profunda</li>
  <li>Fortalecimento dos fios</li>
  <li>Brilho natural</li>
</ul>

<h2>Dicas de aplicação</h2>
<p>Para melhores resultados, siga as orientações abaixo:</p>
<ol>
  <li>Escolha o booster ideal para seu tipo de cabelo.</li>
  <li>Misture conforme as instruções.</li>
  <li>Use regularmente para resultados duradouros.</li>
</ol>
```

### ✅ Requisitos finais

- O conteúdo gerado deve ser **pronto para copiar e colar diretamente** no editor de blog post do Shopify.
- Estruturalmente **compatível com as boas práticas de SEO** e com a lógica de publicação da plataforma.
- **Sem necessidade de ajustes manuais adicionais**.

---

**Observação:**  
O `<h1>` será automaticamente gerado a partir do campo **“Title”** do post no Shopify.  
A meta description será configurada na seção **“Search engine listing preview”**.

---

_Fique atento à clareza, objetividade e estrutura hierárquica. Evite redundâncias e excesso de marcações._
