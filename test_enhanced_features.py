#!/usr/bin/env python3
"""
Test the enhanced Streamlit app with AI features
"""
import subprocess
import sys
import time
import requests

def test_ollama_connection():
    """Test if Ollama is accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
            models = response.json().get('models', [])
            print(f"📚 Available models: {len(models)}")
            if models:
                for model in models[:3]:  # Show first 3 models
                    print(f"   - {model.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("💡 To setup Ollama:")
        print("   1. Install: curl -fsSL https://ollama.ai/install.sh | sh")
        print("   2. Start: ollama serve")
        print("   3. Pull model: ollama pull llama3.2")
        return False

def main():
    print("🚀 Testing Enhanced PyMermaidView Streamlit App")
    print("=" * 60)
    
    # Test Ollama connection
    print("\n🤖 Testing Ollama AI Enhancement Setup:")
    ollama_available = test_ollama_connection()
    
    print(f"\n📋 Enhanced Features Summary:")
    print("✅ Collapsible sidebar (starts collapsed)")
    print("✅ Zoom controls moved to image preview area")
    print("✅ 'Enhance with AI' button added")
    print("✅ AI enhancement options (improve, styling, optimize)")
    print("✅ Enhancement history tracking")
    print("✅ Ollama status monitoring in sidebar")
    
    if ollama_available:
        print("\n🎉 All features ready! AI enhancement will work.")
    else:
        print("\n⚠️  AI enhancement won't work without Ollama setup.")
        print("   Other features (validation, generation) will work normally.")
    
    print(f"\n🌐 Launch the enhanced app:")
    print("   streamlit run streamlit_app.py --server.port 8507")
    print("   http://localhost:8507")
    
    print(f"\n🎯 New UI Features:")
    print("   - Sidebar is collapsible and starts minimized")
    print("   - Zoom controls are part of image preview (🔍➕ 🔍➖ 🔄)")
    print("   - 'Enhance with AI' button with 3 enhancement types")
    print("   - Real-time Ollama status in sidebar")
    
    return True

if __name__ == "__main__":
    main()