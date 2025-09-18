const { shopifyApi } = require('@shopify/shopify-api');

class ShopifyService {
  constructor(shopify) {
    this.shopify = shopify;
  }

  // Shop information
  async getShopInfo() {
    try {
      const shop = await this.shopify.rest.Shop.current();
      return {
        id: shop.id,
        name: shop.name,
        domain: shop.domain,
        email: shop.email,
        currency: shop.currency,
        timezone: shop.timezone,
        plan_name: shop.plan_name,
        country: shop.country,
        created_at: shop.created_at,
        updated_at: shop.updated_at
      };
    } catch (error) {
      console.error('Error fetching shop info:', error);
      throw error;
    }
  }

  // Products
  async getProducts(options = {}) {
    try {
      const { limit = 50, page = 1, product_type, status, title } = options;
      
      const params = {
        limit,
        page,
        ...(product_type && { product_type }),
        ...(status && { status }),
        ...(title && { title })
      };

      const products = await this.shopify.rest.Product.all({
        session: this.shopify.session,
        ...params
      });

      return {
        products: products.data.map(product => ({
          id: product.id,
          title: product.title,
          handle: product.handle,
          product_type: product.product_type,
          vendor: product.vendor,
          tags: product.tags.split(',').map(tag => tag.trim()),
          status: product.status,
          created_at: product.created_at,
          updated_at: product.updated_at,
          published_at: product.published_at,
          variants: product.variants.map(variant => ({
            id: variant.id,
            title: variant.title,
            price: variant.price,
            sku: variant.sku,
            inventory_quantity: variant.inventory_quantity,
            weight: variant.weight,
            weight_unit: variant.weight_unit
          })),
          images: product.images.map(image => ({
            id: image.id,
            src: image.src,
            alt: image.alt,
            width: image.width,
            height: image.height
          })),
          options: product.options.map(option => ({
            id: option.id,
            name: option.name,
            values: option.values
          }))
        })),
        total: products.data.length
      };
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  }

  async getProductById(productId) {
    try {
      const product = await this.shopify.rest.Product.find({
        session: this.shopify.session,
        id: productId
      });

      return {
        id: product.id,
        title: product.title,
        handle: product.handle,
        product_type: product.product_type,
        vendor: product.vendor,
        tags: product.tags.split(',').map(tag => tag.trim()),
        status: product.status,
        created_at: product.created_at,
        updated_at: product.updated_at,
        published_at: product.published_at,
        variants: product.variants.map(variant => ({
          id: variant.id,
          title: variant.title,
          price: variant.price,
          sku: variant.sku,
          inventory_quantity: variant.inventory_quantity,
          weight: variant.weight,
          weight_unit: variant.weight_unit
        })),
        images: product.images.map(image => ({
          id: image.id,
          src: image.src,
          alt: image.alt,
          width: image.width,
          height: image.height
        })),
        options: product.options.map(option => ({
          id: option.id,
          name: option.name,
          values: option.values
        }))
      };
    } catch (error) {
      console.error('Error fetching product:', error);
      throw error;
    }
  }

  // Blogs
  async getBlogs() {
    try {
      const blogs = await this.shopify.rest.Blog.all({
        session: this.shopify.session
      });

      return blogs.data.map(blog => ({
        id: blog.id,
        title: blog.title,
        handle: blog.handle,
        commentable: blog.commentable,
        feedburner: blog.feedburner,
        feedburner_location: blog.feedburner_location,
        created_at: blog.created_at,
        updated_at: blog.updated_at
      }));
    } catch (error) {
      console.error('Error fetching blogs:', error);
      throw error;
    }
  }

  async getBlogById(blogId) {
    try {
      const blog = await this.shopify.rest.Blog.find({
        session: this.shopify.session,
        id: blogId
      });

      return {
        id: blog.id,
        title: blog.title,
        handle: blog.handle,
        commentable: blog.commentable,
        feedburner: blog.feedburner,
        feedburner_location: blog.feedburner_location,
        created_at: blog.created_at,
        updated_at: blog.updated_at
      };
    } catch (error) {
      console.error('Error fetching blog:', error);
      throw error;
    }
  }

  // Blog Posts
  async getBlogPosts(options = {}) {
    try {
      const { blog_id, limit = 50, page = 1 } = options;
      
      const params = {
        limit,
        page,
        ...(blog_id && { blog_id })
      };

      const articles = await this.shopify.rest.Article.all({
        session: this.shopify.session,
        ...params
      });

      return {
        articles: articles.data.map(article => ({
          id: article.id,
          title: article.title,
          handle: article.handle,
          author: article.author,
          content: article.content,
          summary: article.summary,
          blog_id: article.blog_id,
          created_at: article.created_at,
          updated_at: article.updated_at,
          published_at: article.published_at,
          tags: article.tags.split(',').map(tag => tag.trim()),
          image: article.image ? {
            src: article.image.src,
            alt: article.image.alt,
            width: article.image.width,
            height: article.image.height
          } : null
        })),
        total: articles.data.length
      };
    } catch (error) {
      console.error('Error fetching blog posts:', error);
      throw error;
    }
  }

  async getBlogPostById(articleId) {
    try {
      const article = await this.shopify.rest.Article.find({
        session: this.shopify.session,
        id: articleId
      });

      return {
        id: article.id,
        title: article.title,
        handle: article.handle,
        author: article.author,
        content: article.content,
        summary: article.summary,
        blog_id: article.blog_id,
        created_at: article.created_at,
        updated_at: article.updated_at,
        published_at: article.published_at,
        tags: article.tags.split(',').map(tag => tag.trim()),
        image: article.image ? {
          src: article.image.src,
          alt: article.image.alt,
          width: article.image.width,
          height: article.image.height
        } : null
      };
    } catch (error) {
      console.error('Error fetching blog post:', error);
      throw error;
    }
  }

  async createBlogPost(blogPostData) {
    try {
      const { title, content, blog_id, author, tags, summary, published_at } = blogPostData;
      
      const article = new this.shopify.rest.Article({
        session: this.shopify.session
      });

      article.title = title;
      article.content = content;
      article.blog_id = blog_id;
      article.author = author;
      article.tags = tags ? tags.join(', ') : '';
      article.summary = summary;
      article.published_at = published_at || new Date().toISOString();

      await article.save({
        update: true
      });

      return {
        id: article.id,
        title: article.title,
        handle: article.handle,
        author: article.author,
        content: article.content,
        summary: article.summary,
        blog_id: article.blog_id,
        created_at: article.created_at,
        updated_at: article.updated_at,
        published_at: article.published_at,
        tags: article.tags.split(',').map(tag => tag.trim())
      };
    } catch (error) {
      console.error('Error creating blog post:', error);
      throw error;
    }
  }

  async updateBlogPost(articleId, blogPostData) {
    try {
      const { title, content, author, tags, summary, published_at } = blogPostData;
      
      const article = await this.shopify.rest.Article.find({
        session: this.shopify.session,
        id: articleId
      });

      if (title) article.title = title;
      if (content) article.content = content;
      if (author) article.author = author;
      if (tags) article.tags = tags.join(', ');
      if (summary) article.summary = summary;
      if (published_at) article.published_at = published_at;

      await article.save({
        update: true
      });

      return {
        id: article.id,
        title: article.title,
        handle: article.handle,
        author: article.author,
        content: article.content,
        summary: article.summary,
        blog_id: article.blog_id,
        created_at: article.created_at,
        updated_at: article.updated_at,
        published_at: article.published_at,
        tags: article.tags.split(',').map(tag => tag.trim())
      };
    } catch (error) {
      console.error('Error updating blog post:', error);
      throw error;
    }
  }

  async deleteBlogPost(articleId) {
    try {
      await this.shopify.rest.Article.delete({
        session: this.shopify.session,
        id: articleId
      });
    } catch (error) {
      console.error('Error deleting blog post:', error);
      throw error;
    }
  }
}

module.exports = {
  getShopInfo: (shopify) => new ShopifyService(shopify).getShopInfo(),
  getProducts: (shopify, options) => new ShopifyService(shopify).getProducts(options),
  getProductById: (shopify, id) => new ShopifyService(shopify).getProductById(id),
  getBlogs: (shopify) => new ShopifyService(shopify).getBlogs(),
  getBlogById: (shopify, id) => new ShopifyService(shopify).getBlogById(id),
  getBlogPosts: (shopify, options) => new ShopifyService(shopify).getBlogPosts(options),
  getBlogPostById: (shopify, id) => new ShopifyService(shopify).getBlogPostById(id),
  createBlogPost: (shopify, data) => new ShopifyService(shopify).createBlogPost(data),
  updateBlogPost: (shopify, id, data) => new ShopifyService(shopify).updateBlogPost(id, data),
  deleteBlogPost: (shopify, id) => new ShopifyService(shopify).deleteBlogPost(id)
};
