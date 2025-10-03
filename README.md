# CPG Labs - AI-Powered Content Generation Platform

## 🚀 Overview

CPG Labs is a comprehensive AI-powered platform for content generation, market research, and customer analysis. Built with modern AI technologies including CrewAI, LangChain, and OpenAI, it provides powerful tools for businesses to create, analyze, and optimize their content strategies.

## 🏗️ Architecture

### Core Components

- **Lovable Frontend**: React/TypeScript application with modern UI components
- **CrewAI Integration**: Multi-agent AI system for content generation
- **FastAPI Backend**: Python API services for AI processing
- **Edge Functions**: Serverless functions for seamless integration

### Key Features

- 🤖 **AI Content Generation**: SEO-optimized blog posts and marketing content
- 📊 **Market Research**: Comprehensive market analysis and competitive intelligence
- 🎯 **Customer Segmentation**: RFM analysis and customer insights
- 🌍 **Geographic Analytics**: Location-based commerce analysis
- 📈 **CRM Tools**: Customer relationship management and personalization

## 📁 Project Structure

```
cpg-labs/
├── functions/                 # Core AI modules and services
│   ├── seo_lab/              # SEO content generation with CrewAI
│   ├── insighter/            # Market research and analysis
│   ├── crm_lab/              # CRM and customer personalization
│   ├── geocommerce/          # Geographic commerce analysis
│   ├── rfmify/               # RFM customer analysis
│   └── shopify_connector/    # Shopify API integration
├── lovable-app/              # React/TypeScript frontend
├── apps/                     # Additional applications
└── z_legacy/                 # Legacy components and enhancements
```

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Lovable Cloud** for deployment

### Backend
- **Python 3.10+** with FastAPI
- **CrewAI** for multi-agent AI orchestration
- **LangChain** for LLM integration
- **OpenAI GPT** models for content generation

### AI & ML
- **CrewAI**: Multi-agent AI orchestration
- **LangChain**: LLM framework and tools
- **spaCy**: Natural language processing
- **Pandas**: Data analysis and manipulation

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nami-works/cpg-labs.git
   cd cpg-labs
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   cd lovable-app
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Running the Application

1. **Start the Python API**
   ```bash
   cd functions/seo_lab
   uvicorn api_service:app --reload
   ```

2. **Start the Lovable frontend**
   ```bash
   cd lovable-app
   npm run dev
   ```

## 📚 Modules

### 🔍 SEO Lab
AI-powered SEO content generation using CrewAI multi-agent system.

**Features:**
- Automated blog post generation
- SEO optimization
- Content strategy planning
- Shopify integration

**Usage:**
```python
from functions.seo_lab.src.copywriter_crew.crew import SEOLab_CPG

crew = SEOLab_CPG()
result = crew.run({
    "topic": "AI in Content Marketing",
    "brand": "TechCorp",
    "keywords": ["AI", "content", "marketing"]
})
```

### 📊 Insighter
Comprehensive market research and competitive analysis.

**Features:**
- Market size analysis
- Competitive landscape mapping
- Customer behavior insights
- Strategic recommendations

### 🎯 CRM Lab
Customer relationship management and personalization tools.

**Features:**
- RFM customer segmentation
- Personalized message generation
- Email campaign creation
- Customer journey mapping

### 🌍 GeoCommerce
Geographic commerce analysis and location-based insights.

**Features:**
- Customer geographic distribution
- Market penetration analysis
- Location-based recommendations
- Geographic clustering

## 🔧 API Endpoints

### SEO Content Generation
```http
POST /api/seo/generate
Content-Type: application/json
x-api-key: your-api-key

{
  "brand": "Your Brand",
  "topic": "Content Topic",
  "keywords": ["keyword1", "keyword2"],
  "language": "en-US",
  "wordCount": 1500
}
```

### Market Analysis
```http
POST /api/insighter/analyze
Content-Type: application/json

{
  "topic": "E-commerce Market",
  "analysis_type": "comprehensive",
  "additional_context": "Focus on B2C trends"
}
```

## 🚀 Deployment

### Lovable Cloud (Frontend)
1. Connect your GitHub repository to Lovable
2. Set environment variables in Lovable Cloud dashboard
3. Deploy automatically on push to main branch

### Render.com (Python API)
1. Connect your GitHub repository to Render
2. Set build command: `pip install -r functions/seo_lab/api_requirements.txt`
3. Set start command: `uvicorn functions.seo_lab.api_service:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

## 📖 Documentation

- [API Documentation](./functions/seo_lab/DEPLOYMENT_GUIDE.md)
- [CrewAI Integration](./functions/seo_lab/README.md)
- [Market Research Guide](./functions/insighter/README.md)
- [CRM Lab Setup](./functions/crm_lab/setup_guide.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Contact the development team
- Check the documentation in each module

## 🎯 Roadmap

- [ ] Enhanced AI agent capabilities
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] API rate limiting and optimization
- [ ] Mobile application

---

**Built with ❤️ by the Nami Works team**
