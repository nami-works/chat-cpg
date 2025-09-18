const express = require('express');
const { authenticateShopify } = require('../../../middleware/auth');
const { uploadContentToShopify } = require('../../../services/contentService');

const router = express.Router();

// Upload processed content to Shopify
router.post('/', authenticateShopify, async (req, res) => {
  try {
    const { content, settings } = req.body;
    
    if (!content || content.length === 0) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const uploadedContent = await uploadContentToShopify(content, settings, req.shopify);
    
    res.json({ uploadedContent });
  } catch (error) {
    console.error('Error uploading content to Shopify:', error);
    res.status(500).json({ error: 'Failed to upload content to Shopify' });
  }
});

module.exports = router;
