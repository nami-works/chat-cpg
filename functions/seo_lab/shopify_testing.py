import streamlit as st
from pathlib import Path


def display_shopify_testing_interface():
    """
    Display Shopify upload testing interface that allows testing upload functionality
    using existing generated content without regenerating posts.
    """
    st.info("🧪 Shopify testing interface function called")
    st.markdown("---")
    st.markdown("### 🧪 Shopify Upload Testing")
    st.info("💡 Use this section to test and iterate on Shopify upload without regenerating content")
    
    # Get brand context
    context = st.session_state.get('context', {})
    brand_id = context.get('brand_id')
    
    if not brand_id:
        st.error("❌ No brand selected. Please select a brand from the sidebar.")
        return
    
    # Find existing generated content
    base_dir = Path(__file__).parent.parent.parent
    brand_folder = base_dir / 'z_brands' / brand_id
    posts_folder = brand_folder / 'posts'
    
    # Look for existing content folders
    content_folders = []
    if posts_folder.exists():
        content_folders = [f for f in posts_folder.iterdir() if f.is_dir()]
        content_folders.sort(key=lambda x: x.name, reverse=True)  # Most recent first
    
    if not content_folders:
        st.warning("⚠️ No generated content found. Generate some content first, then use this testing section.")
        st.info("💡 Content folders should be in: `apps/{brand_id}/posts/`")
        return
    
    st.success(f"✅ Found {len(content_folders)} content folder(s)")
    
    # Let user select which content to test with
    folder_names = [f.name for f in content_folders]
    selected_folder = st.selectbox(
        "📁 Select content folder to test:",
        folder_names,
        help="Choose which generated content to use for Shopify upload testing"
    )
    
    if selected_folder:
        selected_path = posts_folder / selected_folder
        
        # Show content preview
        html_files = list(selected_path.glob('*.html'))
        metafields_files = list(selected_path.glob('*_metafields.md'))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 HTML Files", len(html_files))
        with col2:
            st.metric("📝 Metafields Files", len(metafields_files))
        
        # Show file list
        with st.expander("📋 Files in selected folder", expanded=False):
            for html_file in html_files:
                st.write(f"• {html_file.name}")
            for md_file in metafields_files:
                st.write(f"• {md_file.name}")
        
        # Test Shopify upload button
        if st.button("🚀 Test Shopify Upload", type="primary", help="Upload selected content to Shopify for testing"):
            st.info("🧪 Starting Shopify upload test...")
            try:
                # Import the upload function from the main module
                from functions.seo_lab._seo_lab import upload_to_shopify_after_generation
                
                # Temporarily override the content path for testing
                original_macro_name = st.session_state.get('macro_name', 'content_campaign')
                # Extract macro name from folder (remove date prefix)
                macro_name = selected_folder
                if '_' in selected_folder:
                    parts = selected_folder.split('_', 1)
                    if len(parts) > 1:
                        macro_name = parts[1]
                st.info(f"🔧 Using macro name: {macro_name} (extracted from folder: {selected_folder})")
                st.session_state['macro_name'] = macro_name
                
                # Call the upload function directly
                success = upload_to_shopify_after_generation(brand_folder, brand_id)
                
                # Restore original macro name
                st.session_state['macro_name'] = original_macro_name
                
                if success:
                    st.success("✅ Shopify upload test completed successfully!")
                else:
                    st.error("❌ Shopify upload test failed. Check the logs above.")
            except Exception as e:
                st.error(f"❌ Test error: {str(e)}")
                # Restore original macro name on error
                st.session_state['macro_name'] = original_macro_name
