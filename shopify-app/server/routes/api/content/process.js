const express = require('express');
const { authenticateShopify } = require('../../../middleware/auth');
const { processContent } = require('../../../services/contentService');

const router = express.Router();

// Process content through the crew system
router.post('/', authenticateShopify, async (req, res) => {
  try {
    const { themes, selectedProducts, settings } = req.body;
    
    if (!themes || themes.length === 0) {
      return res.status(400).json({ error: 'Themes are required' });
    }

    const processedContent = await processContent(themes, selectedProducts, settings, req.shop);
    
    res.json({ processedContent });
  } catch (error) {
    console.error('Error processing content:', error);
    res.status(500).json({ error: 'Failed to process content' });
  }
});

module.exports = router;
