@echo off
REM Nami SEO Lab Shopify App Setup Script for Windows

echo 🚀 Setting up Nami SEO Lab Shopify App...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

echo ✅ Node.js version: 
node --version

REM Install dependencies
echo 📦 Installing dependencies...
npm install

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy env.example .env
    echo ⚠️  Please edit .env file with your configuration
)

REM Check if required environment variables are set
findstr /C:"SHOPIFY_API_KEY=your_shopify_api_key" .env >nul
if %errorlevel% equ 0 (
    echo ⚠️  Please configure your .env file with actual values
) else (
    echo ✅ .env file is configured
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist logs mkdir logs
if not exist ssl mkdir ssl
if not exist dist mkdir dist

REM Set up SSL certificates for development
if not exist ssl\cert.pem (
    echo 🔐 Generating SSL certificates for development...
    echo This requires OpenSSL to be installed. Please install OpenSSL or generate certificates manually.
    echo For development, you can use ngrok or similar tools for HTTPS.
)

REM Build the application
echo 🔨 Building the application...
npm run build

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Configure your .env file with actual values
echo 2. Set up your Shopify app in the Partner Dashboard
echo 3. Run 'npm run dev' to start the development server
echo 4. Test the app in your development store
echo.
echo For more information, see README.md
pause
