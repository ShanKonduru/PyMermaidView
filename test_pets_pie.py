#!/usr/bin/env python3
"""
Test the pets pie chart generation with correct OutputFormat
"""
import asyncio
from pathlib import Path
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme

async def test_pets_pie_generation():
    """Test generating the pets pie chart"""
    
    pie_syntax = '''pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15'''
    
    print("🥧 Testing pets pie chart generation...")
    print(f"Syntax:\n{pie_syntax}\n")
    
    # Create config with correct enum usage
    config = MermaidConfig()
    config.output_format = OutputFormat.PNG  # Use enum directly
    config.theme = MermaidTheme.DEFAULT
    config.width = 800
    config.height = 600
    config.background_color = "white"
    
    # Create generator
    generator = MermaidGenerator()
    generator.config = config
    
    output_file = Path("output/pets_pie_chart.png")
    
    print(f"📁 Output: {output_file}")
    
    try:
        result = await generator.generate(pie_syntax, output_file)
        
        if result and result.exists():
            print(f"✅ Successfully generated: {result}")
            print(f"📏 Size: {result.stat().st_size / 1024:.1f} KB")
            return True
        else:
            print("❌ Failed to generate pie chart")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_outputformat_enum():
    """Test OutputFormat enum behavior"""
    print("\n🔧 Testing OutputFormat enum...")
    
    # Test different ways to create OutputFormat
    try:
        # This should work
        format1 = OutputFormat.PNG
        print(f"✅ OutputFormat.PNG = {format1} (value: {format1.value})")
        
        # This should work (lowercase)
        format2 = OutputFormat("png")
        print(f"✅ OutputFormat('png') = {format2}")
        
        # This should fail (uppercase)
        try:
            format3 = OutputFormat("PNG")
            print(f"✅ OutputFormat('PNG') = {format3}")
        except ValueError as e:
            print(f"❌ OutputFormat('PNG') failed: {e}")
        
    except Exception as e:
        print(f"❌ Enum test error: {e}")

if __name__ == "__main__":
    # Test enum behavior first
    test_outputformat_enum()
    
    # Test actual generation
    result = asyncio.run(test_pets_pie_generation())
    
    if result:
        print("\n🎉 Pie chart generation test passed!")
    else:
        print("\n❌ Pie chart generation test failed!")