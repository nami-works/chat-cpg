const { processContent, uploadContentToShopify } = require('./crewService');

class ContentService {
  constructor() {
    this.crewService = require('./crewService');
  }

  async processContent(themes, selectedProducts, settings, shop) {
    try {
      // Prepare inputs for the crew system
      const inputs = {
        themes,
        selectedProducts,
        settings,
        shop,
        brand: {
          name: shop.name,
          domain: shop.domain,
          currency: shop.currency
        },
        products: selectedProducts.map(product => ({
          id: product.id,
          title: product.title,
          handle: product.handle,
          product_type: product.product_type,
          vendor: product.vendor,
          tags: product.tags,
          variants: product.variants,
          images: product.images
        })),
        blog: {
          handle: settings.blogHandle,
          title: settings.blogTitle || 'Blog'
        },
        benchmarks: {
          target_word_count: settings.targetWordCount || 1000,
          seo_score_target: settings.seoScoreTarget || 80,
          readability_target: 70
        },
        voice: {
          tone: settings.tone || 'professional',
          language: settings.language || 'en'
        }
      };

      // Process content through the crew system
      const processedContent = await this.crewService.processContent(inputs);
      
      return processedContent;
    } catch (error) {
      console.error('Error processing content:', error);
      throw error;
    }
  }

  async uploadContentToShopify(content, settings, shopify) {
    try {
      const uploadedContent = [];
      
      for (const contentItem of content) {
        // Prepare blog post data for Shopify
        const blogPostData = {
          title: contentItem.title,
          content: contentItem.html,
          blog_id: settings.blogId,
          author: settings.author,
          tags: contentItem.targetKeywords,
          summary: contentItem.metaDescription,
          published_at: settings.autoPublish ? new Date().toISOString() : null
        };

        // Create blog post in Shopify
        const blogPost = await shopify.rest.Article.create({
          session: shopify.session,
          ...blogPostData
        });

        uploadedContent.push({
          id: blogPost.id,
          title: blogPost.title,
          handle: blogPost.handle,
          status: blogPost.published_at ? 'published' : 'draft',
          url: `https://${shopify.session.shop}/blogs/${settings.blogHandle}/${blogPost.handle}`
        });
      }

      return uploadedContent;
    } catch (error) {
      console.error('Error uploading content to Shopify:', error);
      throw error;
    }
  }

  async generateBlogPost(theme, productData, seoKeywords) {
    try {
      // This would integrate with the crew system to generate a single blog post
      const inputs = {
        theme,
        productData,
        seoKeywords,
        single_post: true
      };

      const blogPost = await this.crewService.generateSinglePost(inputs);
      
      return blogPost;
    } catch (error) {
      console.error('Error generating blog post:', error);
      throw error;
    }
  }

  async optimizeContent(content, targetKeywords) {
    try {
      // This would integrate with the crew system to optimize content
      const inputs = {
        content,
        targetKeywords,
        optimization_type: 'seo'
      };

      const optimizedContent = await this.crewService.optimizeContent(inputs);
      
      return optimizedContent;
    } catch (error) {
      console.error('Error optimizing content:', error);
      throw error;
    }
  }
}

module.exports = {
  processContent: (themes, selectedProducts, settings, shop) => new ContentService().processContent(themes, selectedProducts, settings, shop),
  uploadContentToShopify: (content, settings, shopify) => new ContentService().uploadContentToShopify(content, settings, shopify),
  generateBlogPost: (theme, productData, seoKeywords) => new ContentService().generateBlogPost(theme, productData, seoKeywords),
  optimizeContent: (content, targetKeywords) => new ContentService().optimizeContent(content, targetKeywords)
};
