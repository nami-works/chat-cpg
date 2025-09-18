import { useState } from 'react';

export function useContentGeneration(fetch) {
  const [loading, setLoading] = useState(false);

  const processContent = async (themes, selectedProducts, settings) => {
    setLoading(true);
    try {
      const response = await fetch('/api/content/process', {
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
        throw new Error('Failed to process content');
      }

      const data = await response.json();
      return data.processedContent;
    } catch (error) {
      console.error('Error processing content:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const uploadToShopify = async (content, settings) => {
    setLoading(true);
    try {
      const response = await fetch('/api/content/upload-shopify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          settings,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to upload content to Shopify');
      }

      const data = await response.json();
      return data.uploadedContent;
    } catch (error) {
      console.error('Error uploading to Shopify:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const generateBlogPost = async (theme, productData, seoKeywords) => {
    setLoading(true);
    try {
      const response = await fetch('/api/content/generate-blog-post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme,
          productData,
          seoKeywords,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate blog post');
      }

      const data = await response.json();
      return data.blogPost;
    } catch (error) {
      console.error('Error generating blog post:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const optimizeContent = async (content, targetKeywords) => {
    setLoading(true);
    try {
      const response = await fetch('/api/content/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          targetKeywords,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to optimize content');
      }

      const data = await response.json();
      return data.optimizedContent;
    } catch (error) {
      console.error('Error optimizing content:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    processContent,
    uploadToShopify,
    generateBlogPost,
    optimizeContent,
    loading,
  };
}
