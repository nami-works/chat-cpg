import { useState } from 'react';

export function useOpenAI(fetch) {
  const [loading, setLoading] = useState(false);

  const generateThemes = async (prompt, selectedProducts = []) => {
    setLoading(true);
    try {
      const response = await fetch('/api/openai/generate-themes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          selectedProducts,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate themes');
      }

      const data = await response.json();
      return data.themes;
    } catch (error) {
      console.error('Error generating themes:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const generateContent = async (themes, selectedProducts, settings) => {
    setLoading(true);
    try {
      const response = await fetch('/api/openai/generate-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          themes,
          selectedProducts,
          settings,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate content');
      }

      const data = await response.json();
      return data.content;
    } catch (error) {
      console.error('Error generating content:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const refineThemes = async (themes, feedback) => {
    setLoading(true);
    try {
      const response = await fetch('/api/openai/refine-themes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          themes,
          feedback,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to refine themes');
      }

      const data = await response.json();
      return data.themes;
    } catch (error) {
      console.error('Error refining themes:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const generateSEOKeywords = async (theme, productData) => {
    setLoading(true);
    try {
      const response = await fetch('/api/openai/generate-seo-keywords', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme,
          productData,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate SEO keywords');
      }

      const data = await response.json();
      return data.keywords;
    } catch (error) {
      console.error('Error generating SEO keywords:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    generateThemes,
    generateContent,
    refineThemes,
    generateSEOKeywords,
    loading,
  };
}
