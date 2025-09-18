import os
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class ShopifyBlogAPI:
    """
    Shopify API client for blog post management.
    Handles authentication and blog post creation/updates.
    """
    
    def __init__(self):
        self.shop_domain = os.getenv('SHOPIFY_SHOP_DOMAIN')
        self.access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
        self.api_version = os.getenv('SHOPIFY_API_VERSION', '2023-10')
        
        if not self.shop_domain or not self.access_token:
            raise ValueError("Shopify credentials not found. Please check your .env file.")
        
        # Remove protocol if present
        if self.shop_domain.startswith(('http://', 'https://')):
            self.shop_domain = self.shop_domain.split('://', 1)[1]
        
        # Remove trailing slash
        self.shop_domain = self.shop_domain.rstrip('/')
        
        self.base_url = f"https://{self.shop_domain}/admin/api/{self.api_version}"
        self.headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test the connection to Shopify API.
        
        Returns:
            tuple: (success, message)
        """
        try:
            url = f"{self.base_url}/shop.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                shop_data = response.json()
                shop_name = shop_data.get('shop', {}).get('name', 'Unknown')
                return True, f"✅ Connected to {shop_name}"
            else:
                return False, f"❌ Connection failed: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, f"❌ Connection error: {str(e)}"
    
    def get_blogs(self) -> List[Dict]:
        """
        Get all blogs from the Shopify store.
        
        Returns:
            list: List of blog dictionaries
        """
        try:
            url = f"{self.base_url}/blogs.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('blogs', [])
            else:
                st.error(f"Error fetching blogs: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            st.error(f"Error fetching blogs: {str(e)}")
            return []
    
    def get_or_create_blog(self, blog_handle: str, blog_title: str) -> Optional[Dict]:
        """
        Get existing blog or create a new one.
        
        Args:
            blog_handle: The handle for the blog (URL-friendly identifier)
            blog_title: The title of the blog
            
        Returns:
            dict: Blog data or None if failed
        """
        try:
            # First, try to get existing blogs
            blogs = self.get_blogs()
            
            # Look for existing blog with the same handle
            for blog in blogs:
                if blog.get('handle') == blog_handle:
                    return blog
            
            # If not found, create new blog
            url = f"{self.base_url}/blogs.json"
            blog_data = {
                "blog": {
                    "title": blog_title,
                    "handle": blog_handle,
                    "commentable": "moderate",
                    "feedburner": "",
                    "feedburner_location": "",
                    "tag_list": ""
                }
            }
            
            response = requests.post(url, headers=self.headers, json=blog_data, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                return data.get('blog')
            else:
                st.error(f"Error creating blog: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error getting/creating blog: {str(e)}")
            return None
    
    def create_blog_post(self, 
                        blog_id: int,
                        title: str,
                        body_html: str,
                        summary_html: str = "",
                        author: str = "Nami AI",
                        tags: List[str] = None,
                        published: bool = True,
                        meta_description: str = "") -> Optional[Dict]:
        """
        Create a new blog post.
        
        Args:
            blog_id: ID of the blog to post to
            title: Post title
            body_html: HTML content of the post
            summary_html: Summary/excerpt of the post
            author: Author name
            tags: List of tags
            published: Whether to publish immediately
            meta_description: Meta description for SEO
            
        Returns:
            dict: Created blog post data or None if failed
        """
        try:
            url = f"{self.base_url}/blogs/{blog_id}/articles.json"
            
            # Prepare tags string
            tags_string = ", ".join(tags) if tags else ""
            
            post_data = {
                "article": {
                    "title": title,
                    "body_html": body_html,
                    "summary_html": summary_html,
                    "author": author,
                    "tags": tags_string,
                    "published": published,
                    "published_at": datetime.now().isoformat() if published else None,
                    "metafields": [
                        {
                            "key": "description_tag",
                            "value": meta_description,
                            "type": "multi_line_text_field",
                            "namespace": "seo"
                        }
                    ] if meta_description else []
                }
            }
            
            response = requests.post(url, headers=self.headers, json=post_data, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                return data.get('article')
            else:
                st.error(f"Error creating blog post: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error creating blog post: {str(e)}")
            return None
    
    def update_blog_post(self, 
                        blog_id: int,
                        article_id: int,
                        title: str = None,
                        body_html: str = None,
                        summary_html: str = None,
                        author: str = None,
                        tags: List[str] = None,
                        published: bool = None) -> Optional[Dict]:
        """
        Update an existing blog post.
        
        Args:
            blog_id: ID of the blog
            article_id: ID of the article to update
            title: New title (optional)
            body_html: New HTML content (optional)
            summary_html: New summary (optional)
            author: New author (optional)
            tags: New tags (optional)
            published: New published status (optional)
            
        Returns:
            dict: Updated blog post data or None if failed
        """
        try:
            url = f"{self.base_url}/blogs/{blog_id}/articles/{article_id}.json"
            
            # Build update data with only provided fields
            update_data = {"article": {}}
            
            if title is not None:
                update_data["article"]["title"] = title
            if body_html is not None:
                update_data["article"]["body_html"] = body_html
            if summary_html is not None:
                update_data["article"]["summary_html"] = summary_html
            if author is not None:
                update_data["article"]["author"] = author
            if tags is not None:
                update_data["article"]["tags"] = ", ".join(tags)
            if published is not None:
                update_data["article"]["published"] = published
            
            response = requests.put(url, headers=self.headers, json=update_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('article')
            else:
                st.error(f"Error updating blog post: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error updating blog post: {str(e)}")
            return None
    
    def upload_blog_post_from_files(self, 
                                  html_file: Path,
                                  metafields_file: Path,
                                  blog_handle: str,
                                  blog_title: str,
                                  author: str = "Nami AI") -> Tuple[bool, str, Optional[Dict]]:
        """
        Upload a blog post from HTML and metafields files.
        
        Args:
            html_file: Path to HTML content file
            metafields_file: Path to metafields file
            blog_handle: Handle for the blog
            blog_title: Title for the blog
            author: Author name
            
        Returns:
            tuple: (success, message, blog_post_data)
        """
        try:
            # Read HTML content
            if not html_file.exists():
                return False, f"HTML file not found: {html_file}", None
            
            with open(html_file, 'r', encoding='utf-8') as f:
                body_html = f.read()
            
            # Read metafields
            if not metafields_file.exists():
                return False, f"Metafields file not found: {metafields_file}", None
            
            with open(metafields_file, 'r', encoding='utf-8') as f:
                metafields_content = f.read()
            
            # Extract metadata
            from chats.seo_lab.csv_generator import ShopifyBlogCSVGenerator
            generator = ShopifyBlogCSVGenerator()
            meta_fields = generator.extract_meta_fields(metafields_content)
            
            title = meta_fields.get('meta_title', 'Blog Post Title')
            meta_description = meta_fields.get('meta_description', '')
            summary_html = meta_fields.get('summary_html', meta_description)
            
            # Debug output for meta description
            st.info(f"🔍 Debug - Meta fields extracted: {list(meta_fields.keys())}")
            st.info(f"🔍 Debug - Meta description: '{meta_description}'")
            st.info(f"🔍 Debug - Summary HTML: '{summary_html[:100]}...'" if summary_html else "🔍 Debug - Summary HTML: (empty)")
            st.info(f"🔍 Debug - Raw metafields content preview: '{metafields_content[:200]}...'")
            
            # Get or create blog
            blog = self.get_or_create_blog(blog_handle, blog_title)
            if not blog:
                return False, f"Failed to get/create blog: {blog_handle}", None
            
            # Create blog post
            blog_post = self.create_blog_post(
                blog_id=blog['id'],
                title=title,
                body_html=body_html,
                summary_html=summary_html,
                author=author,
                published=False,  # Set as draft instead of published
                meta_description=meta_description
            )
            
            if blog_post:
                return True, f"✅ Uploaded: {title}", blog_post
            else:
                return False, f"❌ Failed to upload: {title}", None
                
        except Exception as e:
            return False, f"❌ Upload error: {str(e)}", None
    
    def upload_multiple_posts(self, 
                            posts_directory: Path,
                            blog_handle: str,
                            blog_title: str,
                            author: str = "Nami AI") -> Tuple[int, List[str]]:
        """
        Upload multiple blog posts from a directory.
        
        Args:
            posts_directory: Directory containing HTML + metafields files
            blog_handle: Handle for the blog
            blog_title: Title for the blog
            author: Author name
            
        Returns:
            tuple: (success_count, messages)
        """
        from chats.seo_lab.csv_generator import ShopifyBlogCSVGenerator
        
        generator = ShopifyBlogCSVGenerator()
        file_pairs = generator.find_file_pairs(posts_directory)
        
        success_count = 0
        messages = []
        
        for html_file, metafields_file in file_pairs:
            success, message, blog_post = self.upload_blog_post_from_files(
                html_file, metafields_file, blog_handle, blog_title, author
            )
            
            if success:
                success_count += 1
                messages.append(f"✅ {html_file.stem}: {message}")
            else:
                messages.append(f"❌ {html_file.stem}: {message}")
        
        return success_count, messages
    
    def get_blog_authors(self, blog_id: int = None) -> List[str]:
        """
        Get unique authors from blog articles.
        
        Args:
            blog_id: Specific blog ID (optional, gets from all blogs if None)
            
        Returns:
            list: List of unique author names
        """
        try:
            authors = set()
            
            if blog_id:
                # Get authors from specific blog
                url = f"{self.base_url}/blogs/{blog_id}/articles.json?limit=250"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    for article in articles:
                        if article.get('author'):
                            authors.add(article['author'])
            else:
                # Get authors from all blogs
                blogs = self.get_blogs()
                for blog in blogs:
                    blog_id = blog['id']
                    url = f"{self.base_url}/blogs/{blog_id}/articles.json?limit=250"
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get('articles', [])
                        for article in articles:
                            if article.get('author'):
                                authors.add(article['author'])
            
            return sorted(list(authors))
            
        except Exception as e:
            st.error(f"Error fetching authors: {str(e)}")
            return []


def test_shopify_connection() -> Tuple[bool, str]:
    """
    Test Shopify API connection.
    
    Returns:
        tuple: (success, message)
    """
    try:
        client = ShopifyBlogAPI()
        return client.test_connection()
    except Exception as e:
        return False, f"❌ Setup error: {str(e)}"

