#!/usr/bin/env python3
"""
Test script for the CrewAI API service
Run this to test the API locally before deploying
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change to your deployed URL
API_KEY = "your-secret-key-here"  # Change to your actual API key

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_generate_blog():
    """Test the blog generation endpoint"""
    print("\n🔍 Testing blog generation...")
    
    payload = {
        "brand": "Test Brand",
        "topic": "SEO Optimization",
        "keywords": ["seo", "optimization", "marketing", "digital"],
        "language": "pt-BR",
        "additionalContext": "Focus on practical SEO tips for small businesses"
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/seo/generate",
            json=payload,
            headers=headers,
            timeout=120  # 2 minutes timeout
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print("✅ Blog generation successful")
            data = response.json()
            print(f"⏱️ Duration: {duration:.2f}s")
            print(f"📊 Stats: {data.get('stats', {})}")
            print(f"🏷️ Meta: {data.get('meta', {})}")
            print(f"📝 HTML length: {len(data.get('html', ''))} characters")
            print(f"🔍 Trace ID: {data.get('traceId', 'N/A')}")
            
            # Save the generated HTML for inspection
            with open("test_generated_blog.html", "w", encoding="utf-8") as f:
                f.write(data.get('html', ''))
            print("💾 Generated HTML saved to test_generated_blog.html")
            
        else:
            print(f"❌ Blog generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>120s)")
    except Exception as e:
        print(f"❌ Blog generation error: {e}")

def test_unauthorized():
    """Test unauthorized access"""
    print("\n🔍 Testing unauthorized access...")
    
    payload = {
        "brand": "Test Brand",
        "topic": "Test Topic"
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "wrong-key"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/seo/generate",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 401:
            print("✅ Unauthorized access properly blocked")
        else:
            print(f"❌ Unauthorized access not blocked: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Unauthorized test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting CrewAI API Tests")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print(f"🔑 API Key: {API_KEY}")
    
    # Run tests
    test_health()
    test_generate_blog()
    test_unauthorized()
    
    print("\n✅ Tests completed!")
    print("\n📋 Next steps:")
    print("1. If tests pass, deploy to Render.com")
    print("2. Update Lovable environment variables")
    print("3. Test end-to-end integration")
