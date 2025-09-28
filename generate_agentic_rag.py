#!/usr/bin/env python3
"""
Script to generate an image from the AgenticRAG system flowchart
"""
import asyncio
from pathlib import Path
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme

async def generate_agentic_rag_diagram():
    """Generate the AgenticRAG system diagram"""
    
    # Create generator with high-quality settings
    config = MermaidConfig(
        output_format=OutputFormat.PNG,
        theme=MermaidTheme.DEFAULT,
        width=1920,
        height=1080,
        scale=2.0,  # High resolution
        background_color="white"
    )
    
    generator = MermaidGenerator(config)
    
    # Input and output paths
    input_file = Path("agentic_rag_system.mmd")
    output_file = Path("output/agentic_rag_system.png")
    
    try:
        print("🚀 Generating AgenticRAG System Diagram...")
        print(f"📁 Input: {input_file}")
        print(f"🖼️ Output: {output_file}")
        
        # Generate the image
        result = await generator.generate_from_file(input_file, output_file)
        
        if result:
            print(f"✅ Successfully generated: {output_file}")
            print(f"📏 Size: {output_file.stat().st_size / 1024:.1f} KB")
            
            # Also create different theme versions
            themes_to_try = [
                (MermaidTheme.DARK, "agentic_rag_system_dark.png"),
                (MermaidTheme.FOREST, "agentic_rag_system_forest.png"),
                (MermaidTheme.NEUTRAL, "agentic_rag_system_neutral.png")
            ]
            
            print("\n🎨 Creating additional theme versions...")
            for theme, filename in themes_to_try:
                theme_config = MermaidConfig(
                    output_format=OutputFormat.PNG,
                    theme=theme,
                    width=1920,
                    height=1080,
                    scale=2.0,
                    background_color="white" if theme != MermaidTheme.DARK else "#1e1e1e"
                )
                theme_generator = MermaidGenerator(theme_config)
                theme_output = Path(f"output/{filename}")
                
                theme_result = await theme_generator.generate_from_file(input_file, theme_output)
                if theme_result:
                    print(f"✅ {theme.value} theme: {theme_output}")
        else:
            print("❌ Failed to generate image")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(generate_agentic_rag_diagram())