const { shopifyApi } = require('@shopify/shopify-api');

// Initialize Shopify API
const shopify = shopifyApi({
  apiKey: process.env.SHOPIFY_API_KEY,
  apiSecretKey: process.env.SHOPIFY_API_SECRET,
  scopes: process.env.SHOPIFY_SCOPES.split(','),
  hostName: process.env.SHOPIFY_APP_URL.replace(/https?:\/\//, ''),
  apiVersion: '2023-10',
  isEmbeddedApp: true,
  logger: {
    level: 'info',
    log: console.log,
    warn: console.warn,
    error: console.error
  }
});

// Authentication middleware
const authenticateShopify = async (req, res, next) => {
  try {
    // Get session from request
    const session = req.session;
    
    if (!session) {
      return res.status(401).json({ error: 'No session found' });
    }

    // Verify session is valid
    if (!session.shop || !session.accessToken) {
      return res.status(401).json({ error: 'Invalid session' });
    }

    // Create Shopify client
    const client = new shopify.clients.Rest({
      session: {
        shop: session.shop,
        accessToken: session.accessToken
      }
    });

    // Attach Shopify client to request
    req.shopify = client;
    req.shop = session.shop;

    next();
  } catch (error) {
    console.error('Authentication error:', error);
    res.status(401).json({ error: 'Authentication failed' });
  }
};

// Session validation middleware
const validateSession = async (req, res, next) => {
  try {
    const session = req.session;
    
    if (!session || !session.shop || !session.accessToken) {
      return res.status(401).json({ error: 'Invalid session' });
    }

    // Check if session is expired
    if (session.expires && new Date() > new Date(session.expires)) {
      return res.status(401).json({ error: 'Session expired' });
    }

    next();
  } catch (error) {
    console.error('Session validation error:', error);
    res.status(401).json({ error: 'Session validation failed' });
  }
};

// Rate limiting middleware
const rateLimit = (maxRequests = 100, windowMs = 15 * 60 * 1000) => {
  const requests = new Map();
  
  return (req, res, next) => {
    const clientId = req.ip || req.connection.remoteAddress;
    const now = Date.now();
    const windowStart = now - windowMs;
    
    // Clean up old requests
    if (requests.has(clientId)) {
      const clientRequests = requests.get(clientId);
      const validRequests = clientRequests.filter(time => time > windowStart);
      requests.set(clientId, validRequests);
    }
    
    // Check rate limit
    const clientRequests = requests.get(clientId) || [];
    if (clientRequests.length >= maxRequests) {
      return res.status(429).json({ error: 'Rate limit exceeded' });
    }
    
    // Add current request
    clientRequests.push(now);
    requests.set(clientId, clientRequests);
    
    next();
  };
};

module.exports = {
  authenticateShopify,
  validateSession,
  rateLimit,
  shopify
};
