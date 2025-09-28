#!/usr/bin/env python3
"""
Test quadrant chart generation
"""
import pytest
import asyncio
from pathlib import Path
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme

@pytest.mark.asyncio
async def test_quadrant_generation():
    """Test generating a quadrant chart image"""
    
    quadrant_syntax = """quadrantChart
    title Reach and influence
    x-axis Low Reach --> High Reach
    y-axis Low Influence --> High Influence
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]"""
    
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
    
    output_file = Path("output/quadrant_chart_test.png")
    
    print("📊 Generating quadrant chart...")
    print(f"📁 Output: {output_file}")
    
    try:
        result = await generator.generate(quadrant_syntax, output_file)
        
        if result and result.exists():
            print(f"✅ Successfully generated: {result}")
            print(f"📏 Size: {result.stat().st_size / 1024:.1f} KB")
            return True
        else:
            print("❌ Failed to generate quadrant chart")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_quadrant_generation())
    
    if success:
        print("\n🎉 Quadrant chart generation test passed!")
    else:
        print("\n❌ Quadrant chart generation test failed!")