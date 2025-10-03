# 🦊 Nami Insighter

Comprehensive market research and strategic analysis powered by CrewAI.

## 🚀 Features

### **Analysis Request Interface**
- **Comprehensive Analysis**: Full market research with 7 detailed reports
- **Quick Analysis**: Fast insights for common market topics
- **Customizable Parameters**: Analysis type, depth, and focus areas
- **Progress Tracking**: Real-time progress indicators
- **Report Generation**: Automated report creation and organization

### **Analysis Types Available**
- 📊 **Comprehensive Market Analysis** - Full market research
- 🏆 **Competitive Analysis** - Competitor positioning and benchmarking
- 👥 **Customer Insights Analysis** - Customer behavior and needs
- 📈 **Industry Trend Analysis** - Market trends and dynamics
- 🎯 **Strategic Opportunity Analysis** - Growth opportunities and strategies
- ⚡ **Quick Market Overview** - Fast market insights

### **Quick Analysis Templates**
- 🏪 **E-commerce Market** - Online retail trends and opportunities
- 💻 **SaaS Industry** - Software-as-a-Service competitive landscape
- 🤖 **AI Market** - Artificial Intelligence market analysis

## 📋 Installation

### Prerequisites
- Python 3.8+
- OpenAI API key or other LLM provider
- Internet connection for research

### Install Dependencies
```bash
# Navigate to the insighter directory
cd chats/insighter

# Install required packages
pip install -r requirements.txt
```

### Required Packages
- `crewai>=0.28.0` - AI agent framework
- `langchain>=0.1.0` - LLM integration
- `langchain-openai>=0.0.5` - OpenAI integration
- `pandas>=2.0.0` - Data analysis
- `matplotlib>=3.7.0` - Data visualization
- `plotly>=5.15.0` - Interactive charts
- `scikit-learn>=1.3.0` - Machine learning
- `beautifulsoup4>=4.12.0` - Web scraping
- `requests>=2.31.0` - HTTP requests

## 🎯 Usage

### **In Nami UI**
1. Select "Insighter" from the Chats tab
2. Use the "Launch Comprehensive Analysis" expander for detailed research
3. Use "Quick Analysis Templates" for fast insights
4. Chat with Insighter for additional questions and guidance

### **Analysis Parameters**
- **Topic**: Market, industry, or specific area to analyze
- **Analysis Type**: Choose from 6 different analysis types
- **Depth**: Quick Overview, Standard Analysis, or Deep Dive
- **Additional Context**: Specific focus areas or requirements
- **Recommendations**: Include strategic recommendations
- **Visualizations**: Include charts and data visualizations

### **Generated Reports**
Each analysis generates 7 comprehensive reports:
1. **Market Research Report** - Market size, growth, segmentation
2. **Competitive Analysis Report** - Competitor positioning and benchmarking
3. **Customer Insights Report** - Customer behavior and pain points
4. **Data Analysis Report** - Statistical analysis and predictions
5. **Industry Expertise Report** - Industry dynamics and regulations
6. **Strategic Analysis Report** - SWOT, PESTEL, opportunities
7. **Comprehensive Market Analysis Report** - Executive summary and recommendations

## 🔧 Configuration

### **Agents Configuration** (`src/insighter/config/agents.yaml`)
- Market Researcher
- Competitive Analyst
- Customer Insights Analyst
- Data Scientist
- Industry Expert
- Strategic Analyst

### **Tasks Configuration** (`src/insighter/config/tasks.yaml`)
- Market Research Task
- Competitive Analysis Task
- Customer Insights Task
- Data Analysis Task
- Industry Expertise Task
- Strategic Synthesis Task
- Final Report Task

## 📁 Output Structure

```
insighter_analysis_[topic]_[timestamp]/
├── market_research_report.md
├── competitive_analysis_report.md
├── customer_insights_report.md
├── data_analysis_report.md
├── industry_expertise_report.md
├── strategic_analysis_report.md
└── comprehensive_market_analysis_report.md
```

## 🛠️ Development

### **Crew Structure**
- **6 Specialized Agents**: Each with specific expertise
- **7 Sequential Tasks**: Structured analysis workflow
- **Comprehensive Output**: Multiple report formats
- **Error Handling**: Robust error management

### **Customization**
- Modify `agents.yaml` for agent behavior
- Update `tasks.yaml` for task definitions
- Add custom tools in `src/insighter/tools/`
- Extend analysis types in the UI

## 🚨 Troubleshooting

### **Common Issues**
1. **Missing Dependencies**: Install requirements with `pip install -r requirements.txt`
2. **API Key Issues**: Ensure OpenAI API key is set in environment
3. **Import Errors**: Check Python path and module structure
4. **Analysis Failures**: Simplify topic or check internet connection

### **Error Messages**
- `Missing dependencies`: Install required packages
- `Analysis failed`: Check topic complexity and network
- `Not loaded`: Initialize model in Nami sidebar

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure proper API key configuration
4. Test with simple analysis topics first

---

**Powered by CrewAI and Nami** 🦊
