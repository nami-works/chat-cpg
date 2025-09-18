#!/usr/bin/env python
"""
Test script for the Insighter Crew
This script tests the basic functionality of the crew structure
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

def test_crew_import():
    """Test that the crew can be imported successfully"""
    try:
        from insighter.crew import Insighter
        print("✅ Crew import successful")
        return True
    except ImportError as e:
        print(f"❌ Crew import failed: {e}")
        return False

def test_agents_config():
    """Test that agents configuration can be loaded"""
    try:
        from insighter.crew import Insighter
        crew = Insighter()
        
        # Check if agents config is loaded
        if hasattr(crew, 'agents_config') and crew.agents_config:
            print("✅ Agents configuration loaded successfully")
            
            # Check for expected agents
            expected_agents = [
                'market_researcher',
                'competitive_analyst', 
                'customer_insights_analyst',
                'data_scientist',
                'industry_expert',
                'strategic_analyst'
            ]
            
            for agent in expected_agents:
                if agent in crew.agents_config:
                    print(f"  ✅ Agent '{agent}' found")
                else:
                    print(f"  ❌ Agent '{agent}' missing")
                    return False
            
            return True
        else:
            print("❌ Agents configuration not loaded")
            return False
            
    except Exception as e:
        print(f"❌ Agents configuration test failed: {e}")
        return False

def test_tasks_config():
    """Test that tasks configuration can be loaded"""
    try:
        from insighter.crew import Insighter
        crew = Insighter()
        
        # Check if tasks config is loaded
        if hasattr(crew, 'tasks_config') and crew.tasks_config:
            print("✅ Tasks configuration loaded successfully")
            
            # Check for expected tasks
            expected_tasks = [
                'market_research_task',
                'competitive_analysis_task',
                'customer_insights_task', 
                'data_analysis_task',
                'industry_expertise_task',
                'strategic_synthesis_task',
                'final_report_task'
            ]
            
            for task in expected_tasks:
                if task in crew.tasks_config:
                    print(f"  ✅ Task '{task}' found")
                else:
                    print(f"  ❌ Task '{task}' missing")
                    return False
            
            return True
        else:
            print("❌ Tasks configuration not loaded")
            return False
            
    except Exception as e:
        print(f"❌ Tasks configuration test failed: {e}")
        return False

def test_crew_creation():
    """Test that the crew can be created successfully"""
    try:
        from insighter.crew import Insighter
        crew = Insighter()
        
        # Test crew creation
        crew_instance = crew.crew()
        print("✅ Crew creation successful")
        
        # Check crew properties
        if hasattr(crew_instance, 'agents') and crew_instance.agents:
            print(f"  ✅ Crew has {len(crew_instance.agents)} agents")
        else:
            print("  ❌ Crew has no agents")
            return False
            
        if hasattr(crew_instance, 'tasks') and crew_instance.tasks:
            print(f"  ✅ Crew has {len(crew_instance.tasks)} tasks")
        else:
            print("  ❌ Crew has no tasks")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Crew creation test failed: {e}")
        return False

def test_main_import():
    """Test that the main module can be imported"""
    try:
        from insighter.main import run, analyze_market
        print("✅ Main module import successful")
        return True
    except ImportError as e:
        print(f"❌ Main module import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Insighter Crew Structure")
    print("=" * 50)
    
    tests = [
        ("Crew Import", test_crew_import),
        ("Agents Configuration", test_agents_config),
        ("Tasks Configuration", test_tasks_config),
        ("Crew Creation", test_crew_creation),
        ("Main Module Import", test_main_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Insighter crew is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 