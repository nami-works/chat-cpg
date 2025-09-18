const express = require('express');
const { authenticateShopify } = require('../../../middleware/auth');
const { 
  createBlogPost, 
  updateBlogPost, 
  getBlogPosts, 
  getBlogPostById,
  deleteBlogPost 
} = require('../../../services/shopifyService');

const router = express.Router();

// Get all blog posts
router.get('/', authenticateShopify, async (req, res) => {
  try {
    const { blog_id, limit = 50, page = 1 } = req.query;
    
    const blogPosts = await getBlogPosts(req.shopify, {
      blog_id,
      limit: parseInt(limit),
      page: parseInt(page)
    });
    
    res.json({
      blog_posts: blogPosts.articles,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: blogPosts.total,
        pages: Math.ceil(blogPosts.total / parseInt(limit))
      }
    });
  } catch (error) {
    console.error('Error fetching blog posts:', error);
    res.status(500).json({ error: 'Failed to fetch blog posts' });
  }
});

// Get specific blog post by ID
router.get('/:id', authenticateShopify, async (req, res) => {
  try {
    const blogPost = await getBlogPostById(req.shopify, req.params.id);
    res.json(blogPost);
  } catch (error) {
    console.error('Error fetching blog post:', error);
    res.status(500).json({ error: 'Failed to fetch blog post' });
  }
});

// Create new blog post
router.post('/', authenticateShopify, async (req, res) => {
  try {
    const { title, content, blog_id, author, tags, summary, published_at } = req.body;
    
    const blogPost = await createBlogPost(req.shopify, {
      title,
      content,
      blog_id,
      author,
      tags,
      summary,
      published_at
    });
    
    res.status(201).json(blogPost);
  } catch (error) {
    console.error('Error creating blog post:', error);
    res.status(500).json({ error: 'Failed to create blog post' });
  }
});

// Update blog post
router.put('/:id', authenticateShopify, async (req, res) => {
  try {
    const { title, content, author, tags, summary, published_at } = req.body;
    
    const blogPost = await updateBlogPost(req.shopify, req.params.id, {
      title,
      content,
      author,
      tags,
      summary,
      published_at
    });
    
    res.json(blogPost);
  } catch (error) {
    console.error('Error updating blog post:', error);
    res.status(500).json({ error: 'Failed to update blog post' });
  }
});

// Delete blog post
router.delete('/:id', authenticateShopify, async (req, res) => {
  try {
    await deleteBlogPost(req.shopify, req.params.id);
    res.status(204).send();
  } catch (error) {
    console.error('Error deleting blog post:', error);
    res.status(500).json({ error: 'Failed to delete blog post' });
  }
});

module.exports = router;
