#!/usr/bin/env python3
"""
Create multiple themed versions of the AgenticRAG system diagram
"""
from pathlib import Path
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme
import asyncio

async def create_themed_versions():
    """Create multiple themed versions of the diagram"""
    
    input_file = Path("agentic_rag_system.mmd")
    
    # Define themes to generate
    themes = [
        (MermaidTheme.DEFAULT, "default", "white"),
        (MermaidTheme.DARK, "dark", "#1e1e1e"),
        (MermaidTheme.FOREST, "forest", "white"),
        (MermaidTheme.NEUTRAL, "neutral", "white"),
    ]
    
    print("🎨 Creating themed versions of AgenticRAG System Diagram...")
    
    for theme, theme_name, bg_color in themes:
        output_file = Path(f"output/agentic_rag_system_{theme_name}.png")
        
        # Create config for this theme
        config = MermaidConfig()
        config.output_format = OutputFormat.PNG
        config.theme = theme
        config.width = 1920
        config.height = 1200
        config.scale = 2.0
        config.background_color = bg_color
        
        # Create generator
        generator = MermaidGenerator()
        generator.config = config
        
        print(f"🔄 Generating {theme_name} theme...")
        
        try:
            result = await generator.generate_from_file(input_file, output_file)
            
            if result and result.exists():
                print(f"✅ {theme_name.capitalize()} theme: {result} ({result.stat().st_size / 1024:.1f} KB)")
            else:
                print(f"❌ Failed to generate {theme_name} theme")
                
        except Exception as e:
            print(f"❌ Error generating {theme_name} theme: {e}")
    
    print("\n🎉 All themed versions completed!")
    print("📁 Check the 'output' directory for all generated images.")

if __name__ == "__main__":
    asyncio.run(create_themed_versions())