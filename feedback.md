### 🔧 Feedback: Product Slug Retrieval

The current prompt incorrectly allows slugs to be referenced from secondary sources (brand guides, hardcoded lists, etc.). This creates **inconsistencies** with the actual e-commerce catalog.

#### Required Correction:
- **The only authoritative source for product slugs must be the `products.csv` file.**
- Any mention of “common slugs” or “examples of slugs” outside of the CSV must be **completely removed from the prompt**.
- Whenever a dictionary (`products`) is generated, slugs must always be pulled directly from the `Handle` column in `products.csv`.
- If multiple variations exist (e.g., full-size and travel-size), the system should either:  
  1. Include the most relevant size for the content context, or  
  2. List all variations if the content applies broadly.

#### Why this matters:
- Guarantees **alignment with the actual e-commerce store** (Shopify).
- Prevents slugs that don’t exist in the store (e.g., `shampoo-sem-sulfato`) from being generated.
- Ensures consistency between blog content and product URLs, which is critical for SEO and conversion tracking.

#### Implementation Notes:
- Remove all static slug references from the prompt (like `booster-antifrizz`, `mascara-condicionadora`, etc.).
- Replace them with:

> “Use the exact product slugs from the `Handle` column in `products.csv`. This is the single source of truth.”
