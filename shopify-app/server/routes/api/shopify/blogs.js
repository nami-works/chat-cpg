const express = require('express');
const { authenticateShopify } = require('../../../middleware/auth');
const { getBlogs, getBlogById } = require('../../../services/shopifyService');

const router = express.Router();

// Get all blogs
router.get('/', authenticateShopify, async (req, res) => {
  try {
    const blogs = await getBlogs(req.shopify);
    res.json({ blogs });
  } catch (error) {
    console.error('Error fetching blogs:', error);
    res.status(500).json({ error: 'Failed to fetch blogs' });
  }
});

// Get specific blog by ID
router.get('/:id', authenticateShopify, async (req, res) => {
  try {
    const blog = await getBlogById(req.shopify, req.params.id);
    res.json(blog);
  } catch (error) {
    console.error('Error fetching blog:', error);
    res.status(500).json({ error: 'Failed to fetch blog' });
  }
});

module.exports = router;
