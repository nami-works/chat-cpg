const express = require('express');
const { authenticateShopify } = require('../../../middleware/auth');
const { generateThemes } = require('../../../services/openaiService');

const router = express.Router();

// Generate themes based on prompt and selected products
router.post('/', authenticateShopify, async (req, res) => {
  try {
    const { prompt, selectedProducts } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    const themes = await generateThemes(prompt, selectedProducts, req.shop);
    
    res.json({ themes });
  } catch (error) {
    console.error('Error generating themes:', error);
    res.status(500).json({ error: 'Failed to generate themes' });
  }
});

module.exports = router;
