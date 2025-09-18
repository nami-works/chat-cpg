const express = require('express');
const { authenticateShopify } = require('../../../middleware/auth');
const { getProducts, getProductById } = require('../../../services/shopifyService');

const router = express.Router();

// Get all products
router.get('/', authenticateShopify, async (req, res) => {
  try {
    const { limit = 50, page = 1, product_type, status, title } = req.query;
    
    const products = await getProducts(req.shopify, {
      limit: parseInt(limit),
      page: parseInt(page),
      product_type,
      status,
      title
    });
    
    res.json({
      products: products.products,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: products.total,
        pages: Math.ceil(products.total / parseInt(limit))
      }
    });
  } catch (error) {
    console.error('Error fetching products:', error);
    res.status(500).json({ error: 'Failed to fetch products' });
  }
});

// Get specific product by ID
router.get('/:id', authenticateShopify, async (req, res) => {
  try {
    const product = await getProductById(req.shopify, req.params.id);
    res.json(product);
  } catch (error) {
    console.error('Error fetching product:', error);
    res.status(500).json({ error: 'Failed to fetch product' });
  }
});

module.exports = router;
