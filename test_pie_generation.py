#!/usr/bin/env python3
"""
Test pie chart generation
"""
import asyncio
from pathlib import Path
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme

async def test_pie_generation():
    """Test generating a pie chart image"""
    
    pie_syntax = '''pie title NETFLIX
         "Time spent looking for movie" : 90
         "Time spent watching it" : 10'''
    
    # Create config
    config = MermaidConfig()
    config.output_format = OutputFormat.PNG
    config.theme = MermaidTheme.DEFAULT
    config.width = 800
    config.height = 600
    config.background_color = "white"
    
    # Create generator
    generator = MermaidGenerator()
    generator.config = config
    
    output_file = Path("output/netflix_pie_chart.png")
    
    print("🥧 Generating pie chart...")
    print(f"📁 Output: {output_file}")
    
    try:
        result = await generator.generate(pie_syntax, output_file)
        
        if result and result.exists():
            print(f"✅ Successfully generated: {result}")
            print(f"📏 Size: {result.stat().st_size / 1024:.1f} KB")
        else:
            print("❌ Failed to generate pie chart")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pie_generation())