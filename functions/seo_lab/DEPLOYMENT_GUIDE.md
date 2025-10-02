# CrewAI API Deployment Guide

## Overview
This guide shows how to deploy your CrewAI SEO Lab API to Render.com for integration with your Lovable frontend.

## Files Created
- `api_service.py` - FastAPI service that wraps your existing CrewAI system
- `api_requirements.txt` - Dependencies for the API service
- `DEPLOYMENT_GUIDE.md` - This guide

## Step 1: Prepare Your Repository

### Option A: Deploy from existing repo
1. Push your code to GitHub (if not already done)
2. Make sure `functions/seo_lab/api_service.py` and `api_requirements.txt` are in your repo

### Option B: Create a separate API repo
1. Create a new GitHub repository for the API
2. Copy these files to the new repo:
   - `api_service.py`
   - `api_requirements.txt`
   - All files from `functions/seo_lab/src/` (your CrewAI code)
   - All files from `functions/seo_lab/` (config files, etc.)

## Step 2: Deploy to Render.com

### 2.1 Create Render Service
1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### 2.2 Configure Service Settings
- **Name**: `nami-crewai-api` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r functions/seo_lab/api_requirements.txt`
- **Start Command**: `python functions/seo_lab/api_service.py`

### 2.3 Set Environment Variables
In Render dashboard, go to **Environment** tab and add:

```
API_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
# Add any other API keys your CrewAI system needs
```

### 2.4 Deploy
- Click **"Create Web Service"**
- Render will build and deploy your API
- You'll get a URL like: `https://nami-crewai-api.onrender.com`

## Step 3: Test the API

### 3.1 Test Health Endpoint
```bash
curl https://nami-crewai-api.onrender.com/health
```

### 3.2 Test Blog Generation
```bash
curl -X POST https://nami-crewai-api.onrender.com/api/seo/generate \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-secret-key-here" \
  -d '{
    "brand": "Test Brand",
    "topic": "SEO Optimization",
    "keywords": ["seo", "optimization", "marketing"],
    "language": "pt-BR"
  }'
```

## Step 4: Update Lovable Environment Variables

In your Lovable Cloud dashboard, set:
```
PYTHON_API_URL=https://nami-crewai-api.onrender.com
EDGE_API_KEY=your-secret-key-here
```

## Step 5: Test End-to-End Integration

1. Deploy your Lovable app
2. Use the SEO Lab chat to collect inputs
3. Click "Generate Blog" when inputs are ready
4. Verify the generated content appears in the UI

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all your CrewAI files are in the correct relative paths
2. **Memory Issues**: Render free tier has memory limits - consider upgrading for production
3. **Timeout Issues**: Generation might take >60s - consider implementing async processing
4. **API Key Issues**: Double-check all environment variables are set correctly

### Debugging

1. Check Render logs in the dashboard
2. Test API endpoints individually
3. Verify environment variables are loaded
4. Check that all dependencies are installed

### Performance Optimization

1. **Caching**: Implement Redis caching for repeated requests
2. **Async Processing**: For long-running tasks, implement job queues
3. **Resource Limits**: Monitor memory and CPU usage
4. **Database**: Consider adding a database for storing generated content

## Production Considerations

1. **Security**: 
   - Use proper CORS settings
   - Implement rate limiting
   - Validate all inputs
   - Use HTTPS only

2. **Monitoring**:
   - Add logging and monitoring
   - Set up alerts for failures
   - Monitor performance metrics

3. **Scaling**:
   - Consider load balancing for multiple instances
   - Implement horizontal scaling
   - Use CDN for static assets

## Next Steps

Once deployed and tested:
1. Monitor the API performance
2. Optimize based on usage patterns
3. Add more sophisticated error handling
4. Implement caching for better performance
5. Consider adding authentication and user management
