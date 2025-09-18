import { useState, useEffect } from 'react';

export function useShopifyAPI(fetch) {
  const [products, setProducts] = useState([]);
  const [blogs, setBlogs] = useState([]);
  const [shop, setShop] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadShopifyData = async () => {
      try {
        setLoading(true);
        
        // Load shop information
        const shopResponse = await fetch('/api/shopify/shop');
        if (shopResponse.ok) {
          const shopData = await shopResponse.json();
          setShop(shopData);
        }

        // Load products
        const productsResponse = await fetch('/api/shopify/products');
        if (productsResponse.ok) {
          const productsData = await productsResponse.json();
          setProducts(productsData.products || []);
        }

        // Load blogs
        const blogsResponse = await fetch('/api/shopify/blogs');
        if (blogsResponse.ok) {
          const blogsData = await blogsResponse.json();
          setBlogs(blogsData.blogs || []);
        }

      } catch (err) {
        setError(err.message);
        console.error('Error loading Shopify data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadShopifyData();
  }, [fetch]);

  const createBlogPost = async (blogPostData) => {
    try {
      const response = await fetch('/api/shopify/blog-posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(blogPostData),
      });

      if (!response.ok) {
        throw new Error('Failed to create blog post');
      }

      return await response.json();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const updateBlogPost = async (blogPostId, blogPostData) => {
    try {
      const response = await fetch(`/api/shopify/blog-posts/${blogPostId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(blogPostData),
      });

      if (!response.ok) {
        throw new Error('Failed to update blog post');
      }

      return await response.json();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const getProductById = (productId) => {
    return products.find(product => product.id === productId);
  };

  const getProductsByIds = (productIds) => {
    return products.filter(product => productIds.includes(product.id));
  };

  return {
    products,
    blogs,
    shop,
    loading,
    error,
    createBlogPost,
    updateBlogPost,
    getProductById,
    getProductsByIds,
  };
}
