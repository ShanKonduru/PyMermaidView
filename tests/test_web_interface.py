#!/usr/bin/env python3
"""
Test script for the PyMermaidView Streamlit web interface
"""
import requests
import time
import subprocess
import sys
from pathlib import Path

def check_streamlit_running(port=8501, max_attempts=30):
    """Check if Streamlit is running on the specified port"""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"http://localhost:{port}", timeout=2)
            if response.status_code == 200:
                return True
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(1)
    return False

def test_web_interface():
    """Test the web interface functionality"""
    print("🧪 Testing PyMermaidView Web Interface")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        "streamlit_app.py",
        "src/mermaid_generator.py",
        "src/flowchart_builder.py", 
        "src/mermaid_utils.py"
    ]
    
    print("📁 Checking required files...")
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Missing file: {file}")
            return False
        else:
            print(f"✅ Found: {file}")
    
    # Try to import core modules
    print("\n📦 Testing imports...")
    try:
        from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme
        from src.flowchart_builder import FlowchartBuilder
        from src.mermaid_utils import TemplateManager, FlowchartValidator
        print("✅ All core modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test TemplateManager
    print("\n🗂️ Testing TemplateManager...")
    try:
        template_manager = TemplateManager()
        templates = template_manager.list_templates()
        print(f"✅ Found {len(templates)} templates: {templates}")
    except Exception as e:
        print(f"❌ TemplateManager error: {e}")
        return False
    
    # Test FlowchartBuilder
    print("\n🏗️ Testing FlowchartBuilder...")
    try:
        builder = FlowchartBuilder("Test Flowchart")
        builder.add_node("start", "Start")
        builder.add_node("end", "End") 
        builder.connect("start", "end")
        mermaid_code = builder.build()
        print("✅ FlowchartBuilder working correctly")
        print(f"   Generated {len(mermaid_code)} characters of Mermaid code")
    except Exception as e:
        print(f"❌ FlowchartBuilder error: {e}")
        return False
    
    # Test MermaidGenerator
    print("\n🎨 Testing MermaidGenerator...")
    try:
        generator = MermaidGenerator()
        config = MermaidConfig()
        print("✅ MermaidGenerator initialized successfully")
    except Exception as e:
        print(f"❌ MermaidGenerator error: {e}")
        return False
    
    # Check Streamlit installation
    print("\n🌐 Testing Streamlit...")
    try:
        import streamlit as st
        print(f"✅ Streamlit version: {st.__version__}")
    except ImportError:
        print("❌ Streamlit not installed")
        return False
    
    print("\n🎉 All tests passed!")
    print("\n🚀 To start the web interface:")
    print("   Method 1: Double-click 'start_web_ui.bat'")
    print("   Method 2: Run 'streamlit run streamlit_app.py'")
    print("   Then open: http://localhost:8501")
    
    return True

def main():
    """Main test function"""
    if test_web_interface():
        print("\n✅ Web interface is ready to use!")
        
        # Ask if user wants to start the interface
        try:
            choice = input("\n❓ Would you like to start the web interface now? (y/n): ")
            if choice.lower() in ['y', 'yes']:
                print("\n🚀 Starting web interface...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("\n❌ Web interface tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())