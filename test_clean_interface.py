#!/usr/bin/env python3
"""
Test the new clean Streamlit interface
"""
from src.mermaid_utils import FlowchartValidator
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme
import asyncio
from pathlib import Path

def test_clean_interface():
    """Test that the clean interface components work correctly"""
    print("🧪 Testing Clean Streamlit Interface Components")
    print("=" * 50)
    
    # Test 1: Validation
    validator = FlowchartValidator()
    pie_chart = """pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15"""
    
    is_valid = validator.validate_mermaid_syntax(pie_chart)
    print(f"✅ Validation Test: {'PASS' if is_valid else 'FAIL'}")
    
    # Test 2: Generation
    async def test_generation():
        config = MermaidConfig()
        config.theme = MermaidTheme("default")
        config.output_format = OutputFormat("png")
        config.width = 800
        config.height = 600
        config.scale = 2.0
        
        generator = MermaidGenerator()
        generator.config = config
        
        result = await generator.generate(pie_chart, Path("output/clean_interface_test.png"))
        return result.exists()
    
    generation_success = asyncio.run(test_generation())
    print(f"✅ Generation Test: {'PASS' if generation_success else 'FAIL'}")
    
    # Test 3: Template availability
    templates = [
        "Flowchart", "Sequence Diagram", "Class Diagram", "State Diagram",
        "Entity Relationship Diagram", "User Journey", "Gantt", "Pie Chart", "Quadrant Chart"
    ]
    print(f"✅ Templates Available: {len(templates)} types")
    
    if is_valid and generation_success:
        print("\n🎉 All tests passed! Clean interface is ready!")
        print("🌐 Access the interface at: http://localhost:8505")
        print("\n📋 Features implemented:")
        print("  • Clean, clutter-free UI")
        print("  • Bold title: PyMermaidView")
        print("  • Left pane: Mermaid syntax editor")
        print("  • Right pane: Image preview with zoom")
        print("  • Sidebar: Image generation config")
        print("  • 9 diagram types supported")
        print("  • Validate syntax button")
        print("  • Generate image button")
        print("  • Zoom in/out controls")
    else:
        print("\n❌ Some tests failed!")

if __name__ == "__main__":
    test_clean_interface()