#!/usr/bin/env python3
"""
Simple script to generate the AgenticRAG system diagram
"""
from pathlib import Path
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme

def main():
    """Generate the AgenticRAG system diagram using sync interface"""
    
    input_file = Path("agentic_rag_system.mmd")
    output_file = Path("output/agentic_rag_system.png")
    
    # Create config for high-quality output
    config = MermaidConfig()
    config.output_format = OutputFormat.PNG
    config.theme = MermaidTheme.DEFAULT
    config.width = 1920
    config.height = 1200
    config.scale = 2.0
    config.background_color = "white"
    
    # Create generator
    generator = MermaidGenerator()
    generator.config = config
    
    print("🚀 Generating AgenticRAG System Diagram...")
    print(f"📁 Input: {input_file}")
    print(f"🖼️ Output: {output_file}")
    
    try:
        # Read the mermaid file
        mermaid_code = input_file.read_text(encoding='utf-8')
        
        # Use the synchronous generate method or create our own sync wrapper
        import asyncio
        
        async def generate_async():
            return await generator.generate_from_file(input_file, output_file)
        
        # Run the async function
        result = asyncio.run(generate_async())
        
        if result and result.exists():
            print(f"✅ Successfully generated: {result}")
            print(f"📏 Size: {result.stat().st_size / 1024:.1f} KB")
            return True
        else:
            print("❌ Failed to generate image")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Your AgenticRAG system diagram is ready!")
        print("📁 Check the 'output' directory for the generated image.")
    else:
        print("\n❌ Generation failed. Please check the error messages above.")