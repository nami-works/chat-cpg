#!/usr/bin/env python
"""
Example usage of the Insighter Crew
This script demonstrates how to use the crew for market analysis
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

def example_basic_analysis():
    """Example of basic market analysis"""
    print("🔍 Example: Basic Market Analysis")
    print("=" * 50)
    
    try:
        from insighter.main import analyze_market
        
        # Analyze the e-commerce market
        result = analyze_market(
            topic="E-commerce Market in Brazil",
            additional_context="Focus on B2C trends, customer behavior, and competitive landscape",
            output_dir="example_ecommerce_analysis"
        )
        
        print("✅ Analysis completed successfully!")
        print(f"📁 Reports saved in: example_ecommerce_analysis/")
        return result
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def example_custom_analysis():
    """Example of custom analysis with detailed inputs"""
    print("\n🎯 Example: Custom Market Analysis")
    print("=" * 50)
    
    try:
        from insighter.main import run
        
        # Custom analysis inputs
        inputs = {
            'topic': 'AI and Machine Learning Market',
            'current_year': '2024',
            'output_dir': 'example_ai_market_analysis',
            'additional_context': 'Focus on enterprise adoption, competitive landscape, and future trends'
        }
        
        result = run(inputs)
        
        print("✅ Custom analysis completed successfully!")
        print(f"📁 Reports saved in: example_ai_market_analysis/")
        return result
        
    except Exception as e:
        print(f"❌ Custom analysis failed: {e}")
        return None

def example_quick_analysis():
    """Example of quick analysis for a specific topic"""
    print("\n⚡ Example: Quick Market Analysis")
    print("=" * 50)
    
    try:
        from insighter.main import generate_quick_analysis
        
        # Quick analysis of SaaS market
        result = generate_quick_analysis("SaaS Market")
        
        print("✅ Quick analysis completed successfully!")
        print(f"📁 Reports saved in: quick_analysis_saas_market/")
        return result
        
    except Exception as e:
        print(f"❌ Quick analysis failed: {e}")
        return None

def example_multiple_topics():
    """Example of analyzing multiple topics"""
    print("\n📊 Example: Multiple Topics Analysis")
    print("=" * 50)
    
    try:
        from insighter.main import analyze_market
        
        topics = [
            "Sustainable Fashion Market",
            "Fintech Industry",
            "Remote Work Technology"
        ]
        
        results = []
        
        for topic in topics:
            print(f"\n🔍 Analyzing: {topic}")
            result = analyze_market(
                topic=topic,
                additional_context="Focus on current trends and opportunities",
                output_dir=f"example_{topic.lower().replace(' ', '_')}"
            )
            results.append(result)
            print(f"✅ Completed: {topic}")
        
        print(f"\n🎉 All {len(topics)} analyses completed successfully!")
        return results
        
    except Exception as e:
        print(f"❌ Multiple topics analysis failed: {e}")
        return None

def main():
    """Run example analyses"""
    print("🚀 Insighter Crew - Example Usage")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set. Set it to run actual analyses.")
        print("   export OPENAI_API_KEY='your-api-key'")
        print("\n📖 This is a demonstration of the crew structure.")
        print("   The crew is ready to use once you set up your API key.")
        return
    
    # Run examples
    examples = [
        ("Basic Analysis", example_basic_analysis),
        ("Custom Analysis", example_custom_analysis),
        ("Quick Analysis", example_quick_analysis),
        ("Multiple Topics", example_multiple_topics),
    ]
    
    for example_name, example_func in examples:
        try:
            print(f"\n{'='*60}")
            result = example_func()
            if result:
                print(f"✅ {example_name} completed successfully")
            else:
                print(f"❌ {example_name} failed")
        except Exception as e:
            print(f"❌ {example_name} failed with error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Example usage demonstration completed!")
    print("\n📚 Next steps:")
    print("1. Review the generated reports in the output directories")
    print("2. Customize the analysis topics and contexts")
    print("3. Integrate the crew into your applications")
    print("4. Add custom tools and data sources as needed")

if __name__ == "__main__":
    main() 