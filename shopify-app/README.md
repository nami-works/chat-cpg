# Nami SEO Lab - Shopify App

AI-powered content generation for Shopify stores. This app integrates the existing Nami SEO Lab functionality into a seamless Shopify admin experience.

## Features

- **Theme Generation**: AI-powered theme generation based on your store's products and content goals
- **Product Integration**: Automatically pull products from your Shopify store
- **Content Creation**: Generate SEO-optimized blog posts using OpenAI GPT models
- **Background Processing**: Automated content processing through the crew system
- **Shopify Integration**: Direct publishing to your store's blog
- **Multi-language Support**: Generate content in multiple languages
- **SEO Optimization**: Built-in SEO scoring and optimization

## Architecture

### Frontend (React + Polaris)
- **App.jsx**: Main application component
- **Components**: Modular UI components for each feature
- **Hooks**: Custom hooks for API integration
- **Locales**: Multi-language support

### Backend (Node.js + Express)
- **API Routes**: RESTful API endpoints
- **Services**: Business logic and external API integration
- **Middleware**: Authentication and security
- **Crew Integration**: Background content processing

### Key Integrations
- **Shopify Admin API**: Product and blog management
- **OpenAI API**: Content generation
- **Crew System**: Background processing (adapted from original Nami)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shopify-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Set up Shopify app**
   - Create a new app in your Shopify Partner Dashboard
   - Configure the app URL and redirect URLs
   - Set up the required scopes

5. **Run the development server**
   ```bash
   npm run dev
   ```

## Configuration

### Environment Variables

- `SHOPIFY_API_KEY`: Your Shopify app's API key
- `SHOPIFY_API_SECRET`: Your Shopify app's secret
- `SHOPIFY_SCOPES`: Required Shopify API scopes
- `SHOPIFY_APP_URL`: Your app's URL
- `OPENAI_API_KEY`: Your OpenAI API key
- `SESSION_SECRET`: Session encryption secret

### Shopify App Configuration

The app requires the following scopes:
- `write_products`, `read_products`: Product management
- `write_blogs`, `read_blogs`: Blog management
- `write_blog_articles`, `read_blog_articles`: Blog post management
- `read_customers`, `read_orders`: Customer and order data
- `read_analytics`: Store analytics
- `read_themes`, `write_themes`: Theme management

## Usage

### 1. Theme Generation
- Enter a content brief describing your goals
- Select target products from your store
- Generate AI-powered themes
- Refine themes based on feedback

### 2. Content Creation
- Select themes for content generation
- Configure content settings (tone, language, SEO targets)
- Generate SEO-optimized blog posts
- Review and edit content before publishing

### 3. Publishing
- Configure blog settings
- Set publishing preferences
- Publish content directly to your Shopify store
- Track content performance

## API Endpoints

### Shopify Integration
- `GET /api/shopify/shop` - Get store information
- `GET /api/shopify/products` - Get products
- `GET /api/shopify/blogs` - Get blogs
- `POST /api/shopify/blog-posts` - Create blog post
- `PUT /api/shopify/blog-posts/:id` - Update blog post

### Content Generation
- `POST /api/openai/generate-themes` - Generate themes
- `POST /api/openai/generate-content` - Generate content
- `POST /api/content/process` - Process content
- `POST /api/content/upload-shopify` - Upload to Shopify

## Development

### Project Structure
```
shopify-app/
├── web/                 # Frontend React app
│   ├── components/      # UI components
│   ├── hooks/          # Custom hooks
│   ├── locales/        # Translations
│   └── App.jsx         # Main app component
├── server/             # Backend Express app
│   ├── routes/         # API routes
│   ├── services/       # Business logic
│   ├── middleware/     # Middleware
│   └── app.js          # Main server file
├── package.json        # Dependencies
└── shopify.app.toml    # Shopify app config
```

### Adding New Features

1. **Frontend**: Add components in `web/components/`
2. **Backend**: Add routes in `server/routes/`
3. **Services**: Add business logic in `server/services/`
4. **API Integration**: Update service files

### Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## Deployment

### Production Build
```bash
npm run build
```

### Environment Setup
1. Set up production environment variables
2. Configure Shopify app for production
3. Set up SSL certificates
4. Configure domain and DNS

### Shopify App Store Submission
1. Complete app testing
2. Prepare app store listing
3. Submit for review
4. Monitor and respond to feedback

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check Shopify app configuration
   - Verify API keys and secrets
   - Ensure proper scopes are set

2. **Content Generation Issues**
   - Verify OpenAI API key
   - Check rate limits
   - Review input validation

3. **Shopify API Errors**
   - Check API permissions
   - Verify product/blog data
   - Review rate limits

### Debug Mode
```bash
DEBUG=shopify-app:* npm run dev
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Changelog

### v1.0.0
- Initial release
- Theme generation
- Product integration
- Content creation
- Shopify publishing
- Multi-language support
