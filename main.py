"""
PyMermaidView - Main Entry Point
A comprehensive Python application for generating Mermaid diagrams using OOP principles.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import Windows utilities for better cleanup
from src.windows_utils import run_async_with_cleanup, suppress_windows_asyncio_warnings

# Configure Windows-specific settings
suppress_windows_asyncio_warnings()

from src.mermaid_generator import (
    MermaidGenerator,
    MermaidConfig,
    OutputFormat,
    MermaidTheme,
)
from src.flowchart_builder import (
    FlowchartBuilder,
    NodeShape,
    ArrowType,
    Direction,
    NodeStyle,
)
from src.mermaid_utils import (
    TemplateManager,
    FlowchartValidator,
    create_quick_flowchart,
)
from src.mermaid_cli import cli

# Load environment variables
load_dotenv()


async def demo_basic_flowchart():
    """Demonstrate basic flowchart creation."""
    print("🔄 Creating basic flowchart...")

    # Create a simple flowchart using the builder
    builder = FlowchartBuilder("Sample Login Process")
    builder.set_direction(Direction.TOP_BOTTOM)

    # Add nodes with different shapes
    builder.add_start_end_node("start", "Start")
    builder.add_process_node("login", "User Login")
    builder.add_decision_node("validate", "Valid Credentials?")
    builder.add_process_node("dashboard", "Show Dashboard")
    builder.add_process_node("error", "Show Error")
    builder.add_start_end_node("end", "End")

    # Add connections
    builder.connect("start", "login")
    builder.connect_with_label("login", "validate", "Submit")
    builder.connect_with_label("validate", "dashboard", "Yes")
    builder.connect_with_label("validate", "error", "No")
    builder.connect("dashboard", "end")
    builder.connect("error", "login")

    # Style some nodes
    success_style = NodeStyle(fill_color="#d4f8d4", stroke_color="#28a745")
    error_style = NodeStyle(fill_color="#f8d7da", stroke_color="#dc3545")

    builder.style_node("dashboard", success_style)
    builder.style_node("error", error_style)

    # Save the flowchart
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    mermaid_file = builder.save_to_file(output_dir / "demo_basic.mmd")
    print(f"✅ Mermaid file saved: {mermaid_file}")

    # Generate image
    generator = MermaidGenerator()
    generator.set_config(
        theme=MermaidTheme.DEFAULT,
        output_format=OutputFormat.PNG,
        width=1000,
        height=700,
    )

    try:
        image_file = await generator.generate_from_file(mermaid_file)
        print(f"✅ Image generated: {image_file}")
    except Exception as e:
        print(f"⚠️  Image generation failed: {e}")
        print("   (This is expected if browser dependencies are not installed)")

    return builder


async def demo_advanced_features():
    """Demonstrate advanced features."""
    print("\n🔄 Creating advanced flowchart with subgraphs...")

    builder = FlowchartBuilder("E-Commerce Order Processing")
    builder.set_direction(Direction.LEFT_RIGHT)

    # Main process nodes
    builder.add_start_end_node("start", "Order Received")
    builder.add_process_node("validate_order", "Validate Order")
    builder.add_decision_node("stock_check", "Items in Stock?")
    builder.add_start_end_node("complete", "Order Complete")

    # Add subgraph for payment processing
    payment_subgraph = builder.add_subgraph("payment", "Payment Processing")
    payment_subgraph.add_node(
        FlowchartBuilder()
        .add_process_node("process_payment", "Process Payment")
        .nodes["process_payment"]
    )
    payment_subgraph.add_node(
        FlowchartBuilder()
        .add_decision_node("payment_ok", "Payment Success?")
        .nodes["payment_ok"]
    )

    # Add subgraph for fulfillment
    fulfillment_subgraph = builder.add_subgraph("fulfillment", "Order Fulfillment")
    fulfillment_subgraph.add_node(
        FlowchartBuilder()
        .add_process_node("pick_items", "Pick Items")
        .nodes["pick_items"]
    )
    fulfillment_subgraph.add_node(
        FlowchartBuilder()
        .add_process_node("pack_order", "Pack Order")
        .nodes["pack_order"]
    )
    fulfillment_subgraph.add_node(
        FlowchartBuilder()
        .add_process_node("ship_order", "Ship Order")
        .nodes["ship_order"]
    )

    # Main connections
    builder.connect("start", "validate_order")
    builder.connect("validate_order", "stock_check")
    builder.connect_with_label("stock_check", "process_payment", "Yes")
    builder.connect_with_label("payment_ok", "pick_items", "Success")
    builder.connect("pick_items", "pack_order")
    builder.connect("pack_order", "ship_order")
    builder.connect("ship_order", "complete")

    # Apply custom CSS classes
    builder.add_css_class("highlight", "fill:#ffeb3b,stroke:#f57f17,stroke-width:3px")
    builder.apply_css_class("complete", "highlight")

    # Save advanced flowchart
    output_dir = Path("./output")
    mermaid_file = builder.save_to_file(output_dir / "demo_advanced.mmd")
    print(f"✅ Advanced flowchart saved: {mermaid_file}")

    return builder


def demo_templates():
    """Demonstrate template usage."""
    print("\n🔄 Working with templates...")

    # Create template manager
    manager = TemplateManager()

    # List available templates
    templates = manager.list_templates()
    print(f"📋 Available templates: {', '.join(templates)}")

    # Create flowchart from template
    builder = manager.create_flowchart_from_template(
        "decision_flow",
        title="Customer Support Process",
        input_label="Receive Support Request",
        decision_label="Issue Type Known?",
        process_label="Resolve Issue",
        error_label="Escalate to Specialist",
    )

    # Save template-based flowchart
    output_dir = Path("./output")
    mermaid_file = builder.save_to_file(output_dir / "demo_template.mmd")
    print(f"✅ Template-based flowchart saved: {mermaid_file}")

    return builder


def demo_quick_flowchart():
    """Demonstrate quick flowchart creation."""
    print("\n🔄 Creating quick flowchart...")

    steps = [
        "Analyze Requirements",
        "Design Solution",
        "Implement Code",
        "Test Application",
        "Deploy to Production",
    ]

    builder = create_quick_flowchart(
        title="Software Development Process",
        steps=steps,
        include_decision=True,
        decision_label="Tests Pass?",
    )

    # Save quick flowchart
    output_dir = Path("./output")
    mermaid_file = builder.save_to_file(output_dir / "demo_quick.mmd")
    print(f"✅ Quick flowchart saved: {mermaid_file}")

    return builder


def demo_validation():
    """Demonstrate validation features."""
    print("\n🔄 Demonstrating validation...")

    # Create a flowchart with some issues for testing
    builder = FlowchartBuilder("Test Validation")
    builder.add_process_node("node1", "First Node")
    builder.add_process_node("node2", "Second Node")
    builder.add_process_node("isolated", "Isolated Node")  # This will be isolated
    builder.connect("node1", "node2")

    # Validate the flowchart
    validator = FlowchartValidator()
    is_valid = validator.validate_builder(builder)

    print(f"📊 Validation result: {'✅ Valid' if is_valid else '⚠️  Has issues'}")
    print("Validation report:")
    print(validator.get_validation_report())

    return is_valid


async def main():
    """Main application entry point."""
    print("🚀 PyMermaidView - Mermaid Diagram Generator")
    print("=" * 50)

    try:
        # Create output directory
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)

        # Run demonstrations
        await demo_basic_flowchart()
        await demo_advanced_features()
        demo_templates()
        demo_quick_flowchart()
        demo_validation()

        print("\n🎉 All demonstrations completed successfully!")
        print(f"📁 Check the '{output_dir}' directory for generated files")
        print("\n📖 Usage examples:")
        print("  python -m src.mermaid_cli generate output/demo_basic.mmd")
        print("  python -m src.mermaid_cli quick -s 'Step 1' -s 'Step 2' -s 'Step 3'")
        print("  python -m src.mermaid_cli validate output/demo_basic.mmd")
        print("  python -m src.mermaid_cli template list")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


def cli_entry_point():
    """Entry point for CLI commands."""
    cli()


if __name__ == "__main__":
    # Run the main demo with Windows-safe cleanup
    exit_code = run_async_with_cleanup(main())
