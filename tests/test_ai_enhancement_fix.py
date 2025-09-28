#!/usr/bin/env python3
"""
Test AI enhancement functionality directly
"""
import requests
import json
import time

def test_ollama_directly():
    """Test Ollama API directly"""
    print("🧪 Testing Ollama API directly")
    print("-" * 40)
    
    test_diagram = """flowchart TD
    A --> B
    B --> C"""
    
    ollama_url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.2",
        "prompt": f"""You are a Mermaid diagram expert. Please improve and enhance the following Mermaid diagram syntax:

{test_diagram}

Make the diagram more professional, add better styling, improve node names, add colors if appropriate, and ensure best practices. Return ONLY the enhanced Mermaid syntax without any explanations or markdown formatting.""",
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 500
        }
    }
    
    try:
        print(f"📡 Making request to Ollama...")
        start_time = time.time()
        
        response = requests.post(ollama_url, json=payload, timeout=15)
        
        end_time = time.time()
        print(f"⏱️  Request completed in {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            enhanced_code = result.get('response', '').strip()
            
            print(f"✅ Response received:")
            print(f"   Status: {response.status_code}")
            print(f"   Response length: {len(enhanced_code)} characters")
            
            # Clean up response
            if enhanced_code.startswith('```'):
                lines = enhanced_code.split('\n')
                enhanced_code = '\n'.join(lines[1:])
            if enhanced_code.endswith('```'):
                lines = enhanced_code.split('\n')
                enhanced_code = '\n'.join(lines[:-1])
            
            enhanced_code = enhanced_code.replace('mermaid\n', '').strip()
            
            print(f"\n📋 Original diagram:")
            print(test_diagram)
            
            print(f"\n✨ Enhanced diagram:")
            print(enhanced_code)
            
            if enhanced_code and enhanced_code != test_diagram:
                print(f"\n🎉 Enhancement SUCCESS! AI improved the diagram.")
                return True
            else:
                print(f"\n⚠️  Enhancement returned same or empty result.")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (15 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is Ollama running?")
        print("   Start with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Testing AI Enhancement Fix")
    print("=" * 50)
    
    # Test Ollama connection
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama running with {len(models)} models")
        else:
            print("❌ Ollama not accessible")
            return False
    except:
        print("❌ Ollama not running")
        print("💡 Start with: ollama serve")
        return False
    
    # Test enhancement
    success = test_ollama_directly()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 AI Enhancement is working!")
        print("✅ The Streamlit app should now complete AI enhancements")
        print("🌐 Test at: http://localhost:8507")
    else:
        print("❌ AI Enhancement has issues")
        print("🔧 Check Ollama setup and model availability")
    
    return success

if __name__ == "__main__":
    main()