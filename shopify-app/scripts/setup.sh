#!/bin/bash

# Nami SEO Lab Shopify App Setup Script

echo "🚀 Setting up Nami SEO Lab Shopify App..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Check if required environment variables are set
if ! grep -q "SHOPIFY_API_KEY=your_shopify_api_key" .env; then
    echo "✅ .env file is configured"
else
    echo "⚠️  Please configure your .env file with actual values"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p ssl
mkdir -p dist

# Set up SSL certificates for development
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    echo "🔐 Generating SSL certificates for development..."
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Build the application
echo "🔨 Building the application..."
npm run build

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure your .env file with actual values"
echo "2. Set up your Shopify app in the Partner Dashboard"
echo "3. Run 'npm run dev' to start the development server"
echo "4. Test the app in your development store"
echo ""
echo "For more information, see README.md"
