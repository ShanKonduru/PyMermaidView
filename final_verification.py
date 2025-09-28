#!/usr/bin/env python3
"""
Final verification that the web interface works with user's pie charts
"""
from src.mermaid_utils import FlowchartValidator
from src.mermaid_generator import (
    MermaidGenerator,
    MermaidConfig,
    OutputFormat,
    MermaidTheme,
)
import asyncio


def test_validation():
    """Test validation for both pie charts"""
    print("🔍 Testing Validation...")

    validator = FlowchartValidator()

    # Test 1: Netflix pie chart
    netflix_pie = """pie title NETFLIX
         "Time spent looking for movie" : 90
         "Time spent watching it" : 10"""

    result1 = validator.validate_mermaid_syntax(netflix_pie)
    print(f"Netflix pie chart - Valid: {result1}")

    # Test 2: Pets pie chart
    pets_pie = """pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15"""

    result2 = validator.validate_mermaid_syntax(pets_pie)
    print(f"Pets pie chart - Valid: {result2}")

    return result1 and result2


async def test_generation():
    """Test image generation"""
    print("\n🎨 Testing Generation...")

    pets_pie = """pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15"""

    # Create config (exactly as web interface does)
    config = MermaidConfig()
    config.output_format = OutputFormat("png")  # Using string as web interface does
    config.theme = MermaidTheme("default")
    config.width = 800
    config.height = 600
    config.scale = 2.0
    config.background_color = "white"

    generator = MermaidGenerator()
    generator.config = config

    try:
        from pathlib import Path

        result = await generator.generate(
            pets_pie, Path("output/web_interface_test.png")
        )
        print(f"Generation successful: {result.exists()}")
        return result.exists()
    except Exception as e:
        print(f"Generation failed: {e}")
        return False


def main():
    """Run complete test suite"""
    print("🚀 PyMermaidView Web Interface - Final Verification")
    print("=" * 60)

    # Test validation
    validation_ok = test_validation()

    # Test generation
    generation_ok = asyncio.run(test_generation())

    print("\n📊 Test Results:")
    print(f"✅ Validation: {'PASS' if validation_ok else 'FAIL'}")
    print(f"✅ Generation: {'PASS' if generation_ok else 'FAIL'}")

    if validation_ok and generation_ok:
        print("\n🎉 All tests passed! The web interface should work perfectly.")
        print("🌐 Access it at: http://localhost:8503")
        print("\n📝 Try your pie chart syntax:")
        print("pie title Pets adopted by volunteers")
        print('    "Dogs" : 386')
        print('    "Cats" : 85')
        print('    "Rats" : 15')
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
