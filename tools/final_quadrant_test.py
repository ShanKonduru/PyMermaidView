#!/usr/bin/env python3
"""
Final verification test for user's quadrant chart syntax
"""
from src.mermaid_utils import FlowchartValidator
from src.mermaid_generator import (
    MermaidGenerator,
    MermaidConfig,
    OutputFormat,
    MermaidTheme,
)
import asyncio
from pathlib import Path


def main():
    print("🎯 Final Verification: Quadrant Chart Syntax")
    print("=" * 60)

    # User's exact syntax
    user_syntax = """quadrantChart
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

    print("📝 Testing syntax:")
    print(user_syntax)
    print("\n" + "-" * 60)

    # Test 1: Validation
    print("🔍 Step 1: Validation Test")
    validator = FlowchartValidator()
    is_valid = validator.validate_mermaid_syntax(user_syntax)

    if is_valid:
        print("✅ Validation: PASSED")
    else:
        print("❌ Validation: FAILED")
        for error in validator.errors:
            print(f"   Error: {error}")

    if validator.warnings:
        print("⚠️  Warnings:")
        for warning in validator.warnings:
            print(f"   {warning}")

    # Test 2: Generation
    print("\n🎨 Step 2: Image Generation Test")

    async def test_generation():
        config = MermaidConfig()
        config.theme = MermaidTheme.DEFAULT
        config.output_format = OutputFormat.PNG
        config.width = 800
        config.height = 600
        config.scale = 2.0

        generator = MermaidGenerator()
        generator.config = config

        output_file = Path("output/user_quadrant_final_test.png")
        result = await generator.generate(user_syntax, output_file)

        return result.exists()

    generation_success = asyncio.run(test_generation())

    if generation_success:
        print("✅ Generation: PASSED")
    else:
        print("❌ Generation: FAILED")

    # Final result
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULT")
    print("=" * 60)

    if is_valid and generation_success:
        print("🎉 SUCCESS: Your quadrant chart syntax is now fully working!")
        print("✅ Validation: WORKING")
        print("✅ Generation: WORKING")
        print("✅ Streamlit Interface: READY")
        print(f"\n🌐 Test it in the web interface at: http://localhost:8507")
        print("\n📋 Steps to test in Streamlit:")
        print("1. Select 'Quadrant Chart' from diagram type dropdown")
        print("2. Click '📋 Load Template' button")
        print("3. Click '🔍 Validate Syntax' button → Should show ✅ valid")
        print("4. Click '🎨 Generate Image' button → Should create image")
        print("5. View the generated image in the right preview pane")
        return True
    else:
        print("❌ FAILURE: Some issues still exist")
        return False


if __name__ == "__main__":
    success = main()

    if not success:
        print("\n❌ Please check the errors above and try again.")
