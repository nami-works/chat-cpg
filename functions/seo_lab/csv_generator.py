import csv
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime


class ShopifyBlogCSVGenerator:
    """
    Enhanced CSV generator for Shopify blog imports with multi-post batch processing.
    Processes multiple HTML + metafields file pairs into a single consolidated CSV.
    """
    
    def __init__(self):
        self.delimiter = ';'  # Shopify CSV uses semicolon delimiter
        
    def extract_meta_fields(self, metafields_content: str) -> Dict[str, str]:
        """Extract all meta fields from metafields.md content"""
        meta_fields = {}
        
        # First, try to extract YAML frontmatter from markdown code blocks
        yaml_match = re.search(r'```markdown\s*\n(.*?)\n```', metafields_content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
        else:
            # If no markdown code block, use the entire content
            yaml_content = metafields_content
        
        # Extract meta_title - handles various formats
        title_patterns = [
            r'meta_title:\s*(.+?)(?:\n|$)',
            r'meta_title\s*:\s*(.+?)(?:\n|$)',
            r'title:\s*(.+?)(?:\n|$)',
            r'Meta Title:\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in title_patterns:
            title_match = re.search(pattern, yaml_content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if title_match:
                meta_fields['meta_title'] = title_match.group(1).strip().strip('"\'')
                break
                
        # Extract meta_description - handles various formats
        desc_patterns = [
            r'meta_description:\s*(.+?)(?:\n|$)',
            r'meta_description\s*:\s*(.+?)(?:\n|$)',
            r'description:\s*(.+?)(?:\n|$)',
            r'Meta Description:\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in desc_patterns:
            desc_match = re.search(pattern, yaml_content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if desc_match:
                meta_fields['meta_description'] = desc_match.group(1).strip().strip('"\'')
                break
        
        # Extract summary_html - handles various formats
        summary_patterns = [
            r'summary_html:\s*(.+?)(?:\n|$)',
            r'summary_html\s*:\s*(.+?)(?:\n|$)',
            r'summary:\s*(.+?)(?:\n|$)',
            r'Summary HTML:\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in summary_patterns:
            summary_match = re.search(pattern, yaml_content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if summary_match:
                meta_fields['summary_html'] = summary_match.group(1).strip().strip('"\'')
                break
        
        # Extract related_products - handles various formats
        products_patterns = [
            r'related_products:\s*(.+?)(?:\n|$)',
            r'related_products\s*:\s*(.+?)(?:\n|$)',
            r'products:\s*(.+?)(?:\n|$)',
            r'Related Products:\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in products_patterns:
            products_match = re.search(pattern, yaml_content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if products_match:
                meta_fields['related_products'] = products_match.group(1).strip().strip('"\'')
                break
        
        return meta_fields
    
    def find_file_pairs(self, posts_directory: Path) -> List[Tuple[Path, Path]]:
        """
        Find all HTML + metafields file pairs in a directory
        
        Args:
            posts_directory: Directory to search for file pairs
            
        Returns:
            List of tuples (html_file, metafields_file)
        """
        file_pairs = []
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
                file_pairs.append((html_file, metafields_file))
            else:
                print(f"⚠️ No metafields file found for {html_file.name}")
        
        return file_pairs
    
    def process_file_pair(self, html_file: Path, metafields_file: Path) -> Optional[Dict[str, str]]:
        """
        Process a single HTML + metafields file pair
        
        Args:
            html_file: Path to HTML content file
            metafields_file: Path to metafields file
            
        Returns:
            Dictionary with processed data or None if failed
        """
        try:
            # Read content file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Read metafields file
            with open(metafields_file, 'r', encoding='utf-8') as f:
                metafields_content = f.read()
            
            # Extract meta fields
            meta_fields = self.extract_meta_fields(metafields_content)
            
            # Ensure we have required fields
            title = meta_fields.get('meta_title', 'Blog Post Title')
            description = meta_fields.get('meta_description', 'Blog post description')
            summary_html = meta_fields.get('summary_html', description)
            related_products = meta_fields.get('related_products', '')
            
            # Convert content to HTML if it appears to be markdown
            if html_file.suffix.lower() in ['.md', '.markdown']:
                body_html = self.convert_markdown_to_html(content)
            else:
                body_html = content
            
            return {
                'title': title,
                'description': description,
                'summary_html': summary_html,
                'body_html': body_html,
                'related_products': related_products,
                'source_file': html_file.name
            }
            
        except Exception as e:
            print(f"❌ Error processing {html_file.name}: {str(e)}")
            return None
    
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
    
    def generate_consolidated_csv(self, 
                                posts_directory: Path, 
                                output_file: Path,
                                blog_handle: str = None,
                                blog_title: str = None,
                                author: str = None) -> int:
        """
        Generate a single CSV file with multiple blog posts as separate rows
        
        Args:
            posts_directory: Directory containing blog post files
            output_file: Path to the consolidated CSV file
            blog_handle: Shopify blog handle
            blog_title: Blog title for Shopify
            author: Author name
            
        Returns:
            int: Number of posts successfully processed
        """
        try:
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Get brand context if parameters are not provided
            if blog_handle is None or blog_title is None or author is None:
                try:
                    import streamlit as st
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
            
            # Find all file pairs
            file_pairs = self.find_file_pairs(posts_directory)
            
            if not file_pairs:
                print(f"⚠️ No HTML + metafields file pairs found in {posts_directory}")
                return 0
            
            # Define CSV structure based on Shopify template
            fieldnames = [
                'Command', 'Title', 'Author', 'Body HTML', 'Summary HTML', 'Tags', 'Tags Command',
                'Published', 'Template Suffix', 'Blog: Handle', 'Blog: Title', 'Blog: Commentable',
                'Blog: Feedburner URL', 'Blog: Feedburner Path', 'Blog: Template Suffix',
                'Metafield: title_tag [string]', 'Metafield: description_tag [string]',
                'Metafield: custom.produto [list.product_reference]'
            ]
            
            processed_count = 0
            
            # Write CSV file with multiple rows
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=self.delimiter)
                writer.writeheader()
                
                for html_file, metafields_file in file_pairs:
                    # Process the file pair
                    post_data = self.process_file_pair(html_file, metafields_file)
                    
                    if post_data:
                        # Prepare CSV data for this row
                        csv_data = {
                            'Command': 'MERGE',
                            'Title': post_data['title'],
                            'Author': author,
                            'Body HTML': post_data['body_html'],
                            'Summary HTML': post_data['summary_html'],
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
                            'Metafield: title_tag [string]': post_data['title'],
                            'Metafield: description_tag [string]': post_data['description'],
                            'Metafield: custom.produto [list.product_reference]': post_data['related_products']
                        }
                        
                        # Write row to CSV
                        writer.writerow(csv_data)
                        processed_count += 1
                        print(f"✅ Added to CSV: {post_data['source_file']}")
            
            print(f"✅ Consolidated CSV generated with {processed_count} posts: {output_file}")
            return processed_count
            
        except Exception as e:
            print(f"❌ Error generating consolidated CSV: {str(e)}")
            return 0
    
    def get_processing_summary(self, posts_directory: Path) -> Dict[str, int]:
        """
        Get a summary of files available for processing
        
        Args:
            posts_directory: Directory to analyze
            
        Returns:
            Dictionary with file counts and status
        """
        file_pairs = self.find_file_pairs(posts_directory)
        html_files = list(posts_directory.glob('*.html'))
        md_files = list(posts_directory.glob('*.md'))
        
        return {
            'total_html_files': len(html_files),
            'total_metafields_files': len(md_files),
            'matching_pairs': len(file_pairs),
            'orphaned_html': len(html_files) - len(file_pairs),
            'orphaned_metafields': len(md_files) - len(file_pairs)
        }


# Utility functions for easy usage
def generate_consolidated_shopify_csv(posts_directory: str, output_file: str, 
                                    blog_handle: str = None, blog_title: str = None, 
                                    author: str = None) -> int:
    """
    Convenience function to generate a consolidated Shopify CSV
    
    Args:
        posts_directory: Directory containing blog post files (string)
        output_file: Output consolidated CSV path (string)
        blog_handle: Shopify blog handle
        blog_title: Blog title for Shopify
        author: Author name
        
    Returns:
        int: Number of posts successfully processed
    """
    generator = ShopifyBlogCSVGenerator()
    return generator.generate_consolidated_csv(
        Path(posts_directory),
        Path(output_file),
        blog_handle=blog_handle,
        blog_title=blog_title,
        author=author
    )


def get_csv_processing_summary(posts_directory: str) -> Dict[str, int]:
    """
    Get a summary of files available for CSV processing
    
    Args:
        posts_directory: Directory to analyze (string)
        
    Returns:
        Dictionary with file counts and status
    """
    generator = ShopifyBlogCSVGenerator()
    return generator.get_processing_summary(Path(posts_directory))


if __name__ == "__main__":
    # Example usage
    generator = ShopifyBlogCSVGenerator()
    
    # Test with example directory (adjust path as needed)
    posts_dir = Path("posts")
    output_file = Path("consolidated_shopify_import.csv")
    
    if posts_dir.exists():
        # Get processing summary
        summary = generator.get_processing_summary(posts_dir)
        print(f"📊 Processing Summary:")
        print(f"   HTML files: {summary['total_html_files']}")
        print(f"   Metafields files: {summary['total_metafields_files']}")
        print(f"   Matching pairs: {summary['matching_pairs']}")
        print(f"   Orphaned HTML: {summary['orphaned_html']}")
        print(f"   Orphaned Metafields: {summary['orphaned_metafields']}")
        
        # Generate consolidated CSV
        processed_count = generator.generate_consolidated_csv(posts_dir, output_file)
        print(f"✅ CSV generation {'successful' if processed_count > 0 else 'failed'}")
        print(f"   Processed {processed_count} posts")
    else:
        print(f"❌ Directory not found: {posts_dir}")