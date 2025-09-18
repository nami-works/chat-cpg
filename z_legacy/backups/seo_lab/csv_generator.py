import csv
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class ShopifyBlogCSVGenerator:
    """
    Standalone CSV generator for Shopify blog imports using standard Python libraries.
    This replaces the crew-based CSV generation approach.
    """
    
    def __init__(self):
        self.delimiter = ';'  # Shopify CSV uses semicolon delimiter
        
    def extract_meta_fields(self, metafields_content: str) -> Dict[str, str]:
        """Extract meta_title and meta_description from metafields.md content"""
        meta_fields = {}
        
        # Extract meta_title - handles various formats
        title_patterns = [
            r'meta_title:\s*(.+)',
            r'meta_title\s*:\s*(.+)',
            r'title:\s*(.+)',
            r'Meta Title:\s*(.+)'
        ]
        
        for pattern in title_patterns:
            title_match = re.search(pattern, metafields_content, re.MULTILINE | re.IGNORECASE)
            if title_match:
                meta_fields['meta_title'] = title_match.group(1).strip()
                break
                
        # Extract meta_description - handles various formats
        desc_patterns = [
            r'meta_description:\s*(.+)',
            r'meta_description\s*:\s*(.+)',
            r'description:\s*(.+)',
            r'Meta Description:\s*(.+)'
        ]
        
        for pattern in desc_patterns:
            desc_match = re.search(pattern, metafields_content, re.MULTILINE | re.IGNORECASE)
            if desc_match:
                meta_fields['meta_description'] = desc_match.group(1).strip()
                break
        
        return meta_fields
    
    def convert_markdown_to_html(self, markdown_content: str) -> str:
        """Convert basic markdown to HTML format"""
        html_content = markdown_content
        
        # Convert headers (maintaining hierarchy)
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # Convert bold text
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        
        # Convert italic text
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
        
        # Convert links
        html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
        
        # Convert line breaks to paragraphs
        paragraphs = html_content.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # Check if it's already a header or other HTML element
                if not re.match(r'^<[h1-6]|<a |<strong|<em', para):
                    # Wrap in paragraph tags if it's plain text
                    para = f'<p>{para}</p>'
                formatted_paragraphs.append(para)
        
        return '\n'.join(formatted_paragraphs)
    
    def generate_csv_from_files(self, 
                               content_file: Path,
                               metafields_file: Path,
                               output_file: Path,
                               blog_handle: str = None,
                               blog_title: str = None,
                               author: str = None) -> bool:
        """
        Generate Shopify CSV from content and metafields files
        
        Args:
            content_file: Path to the HTML content file
            metafields_file: Path to the metafields file
            output_file: Path where CSV should be saved
            blog_handle: Shopify blog handle
            blog_title: Blog title for Shopify
            author: Author name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get brand context if parameters are not provided
            if blog_handle is None or blog_title is None or author is None:
                try:
                    import streamlit as st
                    from translations import LANG
                    context = st.session_state.get('context', {})
                    brand_id = context.get('brand_id')
                    brand_name = context.get('brand', 'Selected Brand')
                    
                    if blog_handle is None:
                        blog_handle = brand_id or 'blog'
                    if blog_title is None:
                        blog_title = f'Blog {brand_name}'
                    if author is None:
                        author = f'Redação {brand_name}'
                except ImportError:
                    # Fallback values if streamlit is not available
                    if blog_handle is None:
                        blog_handle = 'blog'
                    if blog_title is None:
                        blog_title = 'Blog'
                    if author is None:
                        author = 'Redação'
            
            # Read content file
            if not content_file.exists():
                print(f"Content file not found: {content_file}")
                return False
                
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Read metafields file
            if not metafields_file.exists():
                print(f"Metafields file not found: {metafields_file}")
                return False
                
            with open(metafields_file, 'r', encoding='utf-8') as f:
                metafields_content = f.read()
            
            # Extract meta fields
            meta_fields = self.extract_meta_fields(metafields_content)
            
            if not meta_fields.get('meta_title'):
                print("Warning: Could not extract meta_title from metafields")
                meta_fields['meta_title'] = "Blog Post Title"
                
            if not meta_fields.get('meta_description'):
                print("Warning: Could not extract meta_description from metafields")
                meta_fields['meta_description'] = "Blog post description"
            
            # Convert content to HTML if it appears to be markdown
            if content_file.suffix.lower() in ['.md', '.markdown']:
                body_html = self.convert_markdown_to_html(content)
            else:
                body_html = content
            
            # Generate the CSV
            return self.generate_csv(
                title=meta_fields['meta_title'],
                meta_description=meta_fields['meta_description'],
                body_html=body_html,
                output_file=output_file,
                blog_handle=blog_handle,
                blog_title=blog_title,
                author=author
            )
            
        except Exception as e:
            print(f"Error generating CSV: {str(e)}")
            return False
    
    def generate_csv(self, 
                    title: str,
                    meta_description: str, 
                    body_html: str,
                    output_file: Path,
                    blog_handle: str = None,
                    blog_title: str = None,
                    author: str = None) -> bool:
        """
        Generate the Shopify CSV file
        
        Args:
            title: Blog post title (meta_title)
            meta_description: Meta description for SEO
            body_html: HTML content of the blog post
            output_file: Where to save the CSV
            blog_handle: Shopify blog handle
            blog_title: Blog title
            author: Author name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Define CSV structure based on Shopify template
            fieldnames = [
                'Command', 'Title', 'Author', 'Body HTML', 'Summary HTML', 'Tags', 'Tags Command',
                'Published', 'Template Suffix', 'Blog: Handle', 'Blog: Title', 'Blog: Commentable',
                'Blog: Feedburner URL', 'Blog: Feedburner Path', 'Blog: Template Suffix',
                'Metafield: title_tag [string]', 'Metafield: description_tag [string]',
                'Metafield: custom.produto [list.product_reference]'
            ]
            
            # Prepare CSV data
            csv_data = {
                'Command': 'MERGE',
                'Title': title,
                'Author': author,
                'Body HTML': body_html,
                'Summary HTML': meta_description,
                'Tags': '',
                'Tags Command': '',
                'Published': 'VERDADEIRO',
                'Template Suffix': '',
                'Blog: Handle': blog_handle,
                'Blog: Title': blog_title,
                'Blog: Commentable': 'yes',
                'Blog: Feedburner URL': '',
                'Blog: Feedburner Path': '',
                'Blog: Template Suffix': '',
                'Metafield: title_tag [string]': title,
                'Metafield: description_tag [string]': meta_description,
                'Metafield: custom.produto [list.product_reference]': ''
            }
            
            # Write CSV file
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=self.delimiter)
                writer.writeheader()
                writer.writerow(csv_data)
            
            print(f"✅ CSV file generated successfully: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error writing CSV file: {str(e)}")
            return False
    
    def generate_batch_csv(self, posts_directory: Path, output_directory: Path) -> int:
        """
        Generate CSV files for multiple blog posts in a directory
        
        Args:
            posts_directory: Directory containing blog post files
            output_directory: Directory to save CSV files
            
        Returns:
            int: Number of CSV files successfully generated
        """
        generated_count = 0
        
        # Look for HTML and metafields file pairs
        html_files = list(posts_directory.glob('*.html'))
        
        for html_file in html_files:
            # Find corresponding metafields file
            base_name = html_file.stem
            metafields_patterns = [
                f"{base_name}_metafields.md",
                f"{base_name}_metacampos.md", 
                f"{base_name}.md"
            ]
            
            metafields_file = None
            for pattern in metafields_patterns:
                potential_file = posts_directory / pattern
                if potential_file.exists():
                    metafields_file = potential_file
                    break
            
            if metafields_file:
                output_csv = output_directory / f"{base_name}_shopify_import.csv"
                
                if self.generate_csv_from_files(html_file, metafields_file, output_csv):
                    generated_count += 1
                else:
                    print(f"Failed to generate CSV for {base_name}")
            else:
                print(f"No metafields file found for {html_file.name}")
        
        print(f"Generated {generated_count} CSV files")
        return generated_count


# Utility function for easy usage
def generate_shopify_csv(content_file: str, metafields_file: str, output_file: str) -> bool:
    """
    Convenience function to generate a single Shopify CSV
    
    Args:
        content_file: Path to content file (string)
        metafields_file: Path to metafields file (string) 
        output_file: Output CSV path (string)
        
    Returns:
        bool: Success status
    """
    generator = ShopifyBlogCSVGenerator()
    return generator.generate_csv_from_files(
        Path(content_file),
        Path(metafields_file), 
        Path(output_file)
    )


if __name__ == "__main__":
    # Example usage
    generator = ShopifyBlogCSVGenerator()
    
    # Test with example files (adjust paths as needed)
    content_file = Path("posts/content.html")
    metafields_file = Path("posts/metafields.md")
    output_file = Path("posts/shopify_import.csv")
    
    success = generator.generate_csv_from_files(content_file, metafields_file, output_file)
    print(f"CSV generation {'successful' if success else 'failed'}") 