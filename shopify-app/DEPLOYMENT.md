# Deployment Guide - Nami SEO Lab Shopify App

This guide covers deploying the Nami SEO Lab Shopify App to production.

## Prerequisites

- Node.js 18 or higher
- Docker (optional)
- SSL certificate
- Domain name
- Shopify Partner account

## Environment Setup

### 1. Production Environment Variables

Create a `.env.production` file with the following variables:

```bash
# Shopify App Configuration
SHOPIFY_API_KEY=your_production_api_key
SHOPIFY_API_SECRET=your_production_api_secret
SHOPIFY_SCOPES=write_products,read_products,write_blogs,read_blogs,write_blog_articles,read_blog_articles,read_customers,read_orders,read_analytics,read_themes,write_themes
SHOPIFY_APP_URL=https://your-production-domain.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Session Configuration
SESSION_SECRET=your_strong_session_secret

# Environment
NODE_ENV=production
PORT=3000
```

### 2. Shopify App Configuration

1. **Create Production App**
   - Go to your Shopify Partner Dashboard
   - Create a new app for production
   - Set the app URL to your production domain
   - Configure redirect URLs

2. **Set Required Scopes**
   - Products: `write_products`, `read_products`
   - Blogs: `write_blogs`, `read_blogs`, `write_blog_articles`, `read_blog_articles`
   - Analytics: `read_customers`, `read_orders`, `read_analytics`
   - Themes: `read_themes`, `write_themes`

3. **Configure App Settings**
   - Set app URL: `https://your-domain.com`
   - Set redirect URL: `https://your-domain.com/auth/callback`
   - Enable embedded app
   - Set up webhooks if needed

## Deployment Options

### Option 1: Docker Deployment

1. **Build Docker Image**
   ```bash
   docker build -t nami-seo-lab .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Update Environment Variables**
   ```bash
   # Edit docker-compose.yml
   # Update environment variables
   docker-compose up -d
   ```

### Option 2: Manual Deployment

1. **Install Dependencies**
   ```bash
   npm ci --only=production
   ```

2. **Build Application**
   ```bash
   npm run build
   ```

3. **Start Application**
   ```bash
   npm start
   ```

### Option 3: Cloud Platform Deployment

#### Heroku

1. **Create Heroku App**
   ```bash
   heroku create nami-seo-lab
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set SHOPIFY_API_KEY=your_key
   heroku config:set SHOPIFY_API_SECRET=your_secret
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set SESSION_SECRET=your_secret
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

#### AWS

1. **Create EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Configure security groups
   - Set up SSL certificate

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install nodejs npm nginx
   ```

3. **Deploy Application**
   ```bash
   git clone <repository>
   cd shopify-app
   npm ci --only=production
   npm run build
   ```

4. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/nami-seo-lab
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name your-domain.com;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/nami-seo-lab /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## SSL Certificate Setup

### Let's Encrypt (Recommended)

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain Certificate**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Auto-renewal**
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Manual SSL Certificate

1. **Generate Certificate Request**
   ```bash
   openssl req -new -newkey rsa:2048 -nodes -keyout your-domain.key -out your-domain.csr
   ```

2. **Submit to CA**
   - Submit CSR to your certificate authority
   - Download the certificate

3. **Install Certificate**
   ```bash
   sudo cp your-domain.crt /etc/ssl/certs/
   sudo cp your-domain.key /etc/ssl/private/
   sudo chmod 600 /etc/ssl/private/your-domain.key
   ```

## Monitoring and Logging

### 1. Application Logs

```bash
# View logs
tail -f logs/app.log

# Rotate logs
logrotate /etc/logrotate.d/nami-seo-lab
```

### 2. Health Checks

```bash
# Check application health
curl https://your-domain.com/health

# Expected response
{"status":"OK","timestamp":"2024-01-01T00:00:00.000Z"}
```

### 3. Performance Monitoring

- Set up monitoring with tools like New Relic, DataDog, or similar
- Monitor API response times
- Track error rates
- Monitor resource usage

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique secrets
- Rotate secrets regularly

### 2. API Security
- Implement rate limiting
- Validate all inputs
- Use HTTPS only
- Implement proper CORS policies

### 3. Session Security
- Use secure session cookies
- Implement session timeout
- Use strong session secrets

## Troubleshooting

### Common Issues

1. **App Not Loading**
   - Check Shopify app configuration
   - Verify SSL certificate
   - Check environment variables

2. **API Errors**
   - Check API keys and secrets
   - Verify scopes
   - Check rate limits

3. **Content Generation Issues**
   - Verify OpenAI API key
   - Check input validation
   - Review error logs

### Debug Mode

```bash
# Enable debug logging
DEBUG=shopify-app:* npm start
```

### Log Analysis

```bash
# View error logs
grep "ERROR" logs/app.log

# View API calls
grep "API" logs/app.log

# View performance metrics
grep "PERFORMANCE" logs/app.log
```

## Maintenance

### 1. Regular Updates
- Keep dependencies updated
- Monitor security advisories
- Update Node.js version
- Update Shopify API version

### 2. Backup Strategy
- Backup application code
- Backup environment configuration
- Backup SSL certificates
- Backup logs

### 3. Scaling
- Monitor resource usage
- Implement load balancing if needed
- Use CDN for static assets
- Consider database optimization

## Support

For deployment issues:
1. Check the logs
2. Verify configuration
3. Test in development environment
4. Contact support team

## Next Steps

After successful deployment:
1. Test all functionality
2. Set up monitoring
3. Configure backups
4. Submit to Shopify App Store
5. Monitor user feedback
