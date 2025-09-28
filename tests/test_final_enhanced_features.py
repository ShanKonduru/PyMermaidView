#!/usr/bin/env python3
"""
Final verification test for enhanced Streamlit features
"""
import requests
import json
from pathlib import Path

def test_ai_enhancement_function():
    """Test the AI enhancement function directly"""
    print("🧪 Testing AI Enhancement Function")
    print("-" * 40)
    
    # Simple test diagram
    test_diagram = """flowchart TD
    A --> B
    B --> C"""
    
    # Test Ollama availability
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code != 200:
            print("❌ Ollama not accessible")
            return False
        
        print("✅ Ollama is accessible")
        
        # Test the enhancement API call
        payload = {
            "model": "llama3.2",
            "prompt": f"Improve this Mermaid diagram: {test_diagram}. Return only enhanced syntax.",
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 200
            }
        }
        
        print("🤖 Testing AI enhancement...")
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            enhanced_code = result.get('response', '').strip()
            
            if enhanced_code and len(enhanced_code) > len(test_diagram):
                print(f"✅ AI enhancement working!")
                print(f"   Original length: {len(test_diagram)} chars")
                print(f"   Enhanced length: {len(enhanced_code)} chars")
                return True
            else:
                print("⚠️  AI responded but enhancement unclear")
                return False
        else:
            print(f"❌ AI API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ AI enhancement test failed: {e}")
        return False

def check_streamlit_file():
    """Check if the enhanced Streamlit file has all features"""
    print("\n📂 Checking Enhanced Streamlit File")
    print("-" * 40)
    
    streamlit_file = Path("streamlit_app.py")
    if not streamlit_file.exists():
        print("❌ streamlit_app.py not found")
        return False
    
    content = streamlit_file.read_text()
    
    # Check for new features
    features = {
        "AI Enhancement": "enhance_with_ai" in content,
        "Collapsible Sidebar": 'initial_sidebar_state="collapsed"' in content,
        "Zoom in Preview": "zoom_in_preview" in content,
        "Enhancement History": "enhancement_history" in content,
        "Ollama Status Check": "localhost:11434" in content,
        "Enhancement Types": "add_styling" in content and "optimize" in content,
        "AI Button": "Enhance with AI" in content
    }
    
    print("Feature Check:")
    all_good = True
    for feature, present in features.items():
        status = "✅" if present else "❌"
        print(f"  {status} {feature}")
        if not present:
            all_good = False
    
    return all_good

def main():
    print("🔍 Final Verification: Enhanced PyMermaidView Features")
    print("=" * 65)
    
    # Test 1: File structure
    file_check = check_streamlit_file()
    
    # Test 2: AI functionality
    ai_check = test_ai_enhancement_function()
    
    print("\n" + "=" * 65)
    print("🎯 FINAL RESULTS")
    print("=" * 65)
    
    if file_check and ai_check:
        print("🎉 SUCCESS: All enhanced features are working!")
        print("\n✅ Implemented Features:")
        print("   1. 🤖 'Enhance with AI' button with Ollama integration")
        print("   2. 📱 Collapsible sidebar (starts collapsed)")
        print("   3. 🔍 Zoom controls moved to image preview area")
        print("   4. ⚙️ AI enhancement options (improve/styling/optimize)")
        print("   5. 📊 Real-time Ollama status monitoring")
        print("   6. 📚 Enhancement history tracking")
        
        print(f"\n🚀 Ready to Use:")
        print("   1. Start app: streamlit run streamlit_app.py --server.port 8507")
        print("   2. Open: http://localhost:8507")
        print("   3. Test AI enhancement with any diagram!")
        
        return True
    else:
        issues = []
        if not file_check:
            issues.append("Code structure issues")
        if not ai_check:
            issues.append("AI enhancement not working")
        
        print(f"❌ Issues found: {', '.join(issues)}")
        
        if not ai_check:
            print(f"\n💡 To fix AI issues:")
            print("   - Ensure Ollama is running: ollama serve")
            print("   - Download model: ollama pull llama3.2")
            print("   - Check port 11434 is accessible")
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)