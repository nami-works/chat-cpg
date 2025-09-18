const express = require('express');
const { authenticateShopify } = require('../../../middleware/auth');
const { generateContent } = require('../../../services/openaiService');

const router = express.Router();

// Generate content based on themes, products, and settings
router.post('/', authenticateShopify, async (req, res) => {
  try {
    const { themes, selectedProducts, settings } = req.body;
    
    if (!themes || themes.length === 0) {
      return res.status(400).json({ error: 'Themes are required' });
    }

    const content = await generateContent(themes, selectedProducts, settings, req.shop);
    
    res.json({ content });
  } catch (error) {
    console.error('Error generating content:', error);
    res.status(500).json({ error: 'Failed to generate content' });
  }
});

module.exports = router;
