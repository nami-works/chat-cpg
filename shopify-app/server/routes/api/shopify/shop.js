const express = require('express');
const { authenticateShopify } = require('../../../middleware/auth');
const { getShopInfo } = require('../../../services/shopifyService');

const router = express.Router();

// Get shop information
router.get('/', authenticateShopify, async (req, res) => {
  try {
    const shopInfo = await getShopInfo(req.shopify);
    res.json(shopInfo);
  } catch (error) {
    console.error('Error fetching shop info:', error);
    res.status(500).json({ error: 'Failed to fetch shop information' });
  }
});

module.exports = router;
