"""
Mermaid CLI - Command Line Interface
This module provides a comprehensive CLI for the Mermaid generator.
"""

import asyncio
import click
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

# Import Windows utilities
from .windows_utils import run_async_with_cleanup, suppress_windows_asyncio_warnings

# Configure Windows-specific settings
suppress_windows_asyncio_warnings()

from .mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme
from .flowchart_builder import FlowchartBuilder, Direction, NodeShape, ArrowType, FlowchartParser
from .mermaid_utils import (
    TemplateManager, FlowchartValidator, MermaidExporter, MermaidImporter, 
    create_quick_flowchart
)


@click.group()
@click.version_option(version="1.0.0", prog_name="PyMermaidView")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """PyMermaidView - A comprehensive Mermaid diagram generator."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file path')
@click.option('--format', '-f', type=click.Choice(['png', 'svg', 'pdf', 'jpeg']), 
              default='png', help='Output format')
@click.option('--theme', '-t', type=click.Choice(['default', 'forest', 'dark', 'neutral', 'base']), 
              default='default', help='Mermaid theme')
@click.option('--width', type=int, default=800, help='Image width')
@click.option('--height', type=int, default=600, help='Image height')
@click.option('--background', '-b', default='white', help='Background color')
@click.option('--scale', type=float, default=1.0, help='Scale factor')
@click.pass_context
async def generate(ctx, input_file, output, format, theme, width, height, background, scale):
    """Generate image from Mermaid file."""
    
    verbose = ctx.obj['verbose']
    
    try:
        if verbose:
            click.echo(f"Reading Mermaid file: {input_file}")
        
        # Read mermaid code
        mermaid_code = input_file.read_text(encoding='utf-8')
        
        # Setup generator
        generator = MermaidGenerator()
        generator.set_config(
            output_format=OutputFormat(format),
            theme=MermaidTheme(theme),
            width=width,
            height=height,
            background_color=background,
            scale=scale
        )
        
        # Generate output filename if not provided
        if not output:
            output = input_file.with_suffix(f'.{format}')
        
        if verbose:
            click.echo(f"Generating {format.upper()} with theme '{theme}'...")
        
        # Generate diagram
        output_path = await generator.generate(mermaid_code, output)
        
        click.echo(f"✓ Diagram generated: {output_path}")
        
        # Show generation history if verbose
        if verbose:
            history = generator.get_generation_history()
            if history:
                last_gen = history[-1]
                click.echo(f"  Generation time: {last_gen['generation_time']:.2f}s")
                click.echo(f"  Output size: {output_path.stat().st_size} bytes")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


# Make the generate command async-compatible
def generate_sync(*args, **kwargs):
    """Synchronous wrapper for the async generate command."""
    return run_async_with_cleanup(generate(*args, **kwargs))

# Replace the async command with sync version
cli.commands['generate'] = click.command()(generate_sync)


@cli.command()
@click.option('--title', '-t', help='Flowchart title')
@click.option('--direction', '-d', type=click.Choice(['TD', 'BT', 'LR', 'RL']), 
              default='TD', help='Flowchart direction')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output .mmd file')
@click.option('--steps', '-s', multiple=True, help='Process steps (can be used multiple times)')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
def create(title, direction, output, steps, interactive):
    """Create a new flowchart interactively or from steps."""
    
    builder = FlowchartBuilder(title=title)
    builder.set_direction(Direction(direction))
    
    if interactive:
        _interactive_creation(builder)
    elif steps:
        _create_from_steps(builder, list(steps))
    else:
        click.echo("Either use --interactive or provide --steps")
        sys.exit(1)
    
    # Save to file
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = Path(f"flowchart_{timestamp}.mmd")
    
    builder.save_to_file(output)
    click.echo(f"✓ Flowchart saved: {output}")


def _interactive_creation(builder: FlowchartBuilder):
    """Interactive flowchart creation."""
    
    click.echo("Interactive Flowchart Creator")
    click.echo("=" * 30)
    
    while True:
        click.echo("\nOptions:")
        click.echo("1. Add node")
        click.echo("2. Add connection")
        click.echo("3. Preview")
        click.echo("4. Done")
        
        choice = click.prompt("Choose option", type=int)
        
        if choice == 1:
            node_id = click.prompt("Node ID")
            label = click.prompt("Node label")
            shape_choices = [shape.name.lower() for shape in NodeShape]
            shape_name = click.prompt(f"Shape ({', '.join(shape_choices[:5])}...)", 
                                    default="rectangle")
            
            try:
                shape = NodeShape[shape_name.upper()]
            except KeyError:
                shape = NodeShape.RECTANGLE
            
            builder.add_node(node_id, label, shape)
            click.echo(f"✓ Added node: {node_id}")
        
        elif choice == 2:
            if not builder.nodes:
                click.echo("Add nodes first!")
                continue
            
            click.echo(f"Available nodes: {', '.join(builder.nodes.keys())}")
            from_node = click.prompt("From node")
            to_node = click.prompt("To node")
            label = click.prompt("Connection label (optional)", default="")
            
            builder.connect(from_node, to_node, ArrowType.ARROW, label or None)
            click.echo(f"✓ Connected: {from_node} -> {to_node}")
        
        elif choice == 3:
            click.echo("\nCurrent flowchart:")
            click.echo("-" * 20)
            click.echo(builder.build())
            click.echo("-" * 20)
        
        elif choice == 4:
            break


def _create_from_steps(builder: FlowchartBuilder, steps: List[str]):
    """Create flowchart from list of steps."""
    
    if not steps:
        return
    
    # Add start node
    builder.add_start_end_node("start", "Start")
    previous_node = "start"
    
    # Add step nodes
    for i, step in enumerate(steps, 1):
        node_id = f"step_{i}"
        builder.add_process_node(node_id, step)
        builder.connect(previous_node, node_id)
        previous_node = node_id
    
    # Add end node
    builder.add_start_end_node("end", "End")
    builder.connect(previous_node, "end")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
def validate(input_file):
    """Validate Mermaid syntax."""
    
    try:
        # Read file
        mermaid_code = input_file.read_text(encoding='utf-8')
        
        # Validate syntax
        validator = FlowchartValidator()
        is_valid = validator.validate_mermaid_syntax(mermaid_code)
        
        # Show results
        click.echo(validator.get_validation_report())
        
        if not is_valid:
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml']), 
              default='json', help='Export format')
def export(input_file, output, format):
    """Export flowchart structure to JSON/YAML."""
    
    try:
        # Parse flowchart
        parser = FlowchartParser()
        builder = parser.parse_file(input_file)
        
        # Generate output filename if not provided
        if not output:
            output = input_file.with_suffix(f'.{format}')
        
        # Export
        exporter = MermaidExporter()
        
        if format == 'json':
            exporter.export_to_json(builder, output)
        else:
            exporter.export_to_yaml(builder, output)
        
        click.echo(f"✓ Exported to: {output}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output .mmd file')
def import_file(input_file, output):
    """Import flowchart from JSON/YAML/CSV."""
    
    try:
        # Determine input format
        suffix = input_file.suffix.lower()
        
        importer = MermaidImporter()
        
        if suffix == '.json':
            builder = importer.from_json(input_file)
        elif suffix in ['.yaml', '.yml']:
            builder = importer.from_yaml(input_file)
        elif suffix == '.csv':
            builder = importer.from_csv(input_file)
        else:
            click.echo(f"Unsupported format: {suffix}")
            sys.exit(1)
        
        # Generate output filename if not provided
        if not output:
            output = input_file.with_suffix('.mmd')
        
        # Save flowchart
        builder.save_to_file(output)
        click.echo(f"✓ Imported flowchart saved: {output}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def template():
    """Template management commands."""
    pass


@template.command('list')
def template_list():
    """List available templates."""
    
    try:
        manager = TemplateManager()
        templates = manager.list_templates()
        
        if not templates:
            click.echo("No templates found.")
            return
        
        click.echo("Available templates:")
        for template_name in templates:
            try:
                tmpl = manager.load_template(template_name)
                click.echo(f"  {template_name}: {tmpl.description}")
            except:
                click.echo(f"  {template_name}: (error loading)")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@template.command('create')
@click.argument('template_name')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output .mmd file')
@click.option('--title', '-t', help='Flowchart title')
def template_create(template_name, output, title):
    """Create flowchart from template."""
    
    try:
        manager = TemplateManager()
        builder = manager.create_flowchart_from_template(template_name, title=title)
        
        # Generate output filename if not provided
        if not output:
            output = Path(f"{template_name}_flowchart.mmd")
        
        builder.save_to_file(output)
        click.echo(f"✓ Created flowchart from template: {output}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--title', '-t', default='Quick Process', help='Flowchart title')
@click.option('--steps', '-s', multiple=True, required=True, help='Process steps')
@click.option('--decision', '-d', is_flag=True, help='Include decision point')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output .mmd file')
def quick(title, steps, decision, output):
    """Quickly create a simple process flowchart."""
    
    try:
        builder = create_quick_flowchart(
            title=title, 
            steps=list(steps), 
            include_decision=decision
        )
        
        # Generate output filename if not provided
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = Path(f"quick_flowchart_{timestamp}.mmd")
        
        builder.save_to_file(output)
        click.echo(f"✓ Quick flowchart created: {output}")
        
        # Show preview
        click.echo("\nPreview:")
        click.echo("-" * 40)
        click.echo(builder.build())
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('mermaid_file', type=click.Path(exists=True, path_type=Path))
def info(mermaid_file):
    """Show information about a Mermaid file."""
    
    try:
        # Parse the file
        parser = FlowchartParser()
        builder = parser.parse_file(mermaid_file)
        
        # Show information
        click.echo(f"File: {mermaid_file}")
        click.echo(f"Title: {builder.title or 'None'}")
        click.echo(f"Direction: {builder.direction.value}")
        click.echo(f"Nodes: {len(builder.nodes)}")
        click.echo(f"Connections: {len(builder.connections)}")
        click.echo(f"Subgraphs: {len(builder.subgraphs)}")
        
        # Validate
        validator = FlowchartValidator()
        is_valid = validator.validate_builder(builder)
        
        click.echo(f"Valid: {'✓' if is_valid else '✗'}")
        
        if validator.warnings or validator.errors:
            click.echo("\nValidation Issues:")
            click.echo(validator.get_validation_report())
        
        # Show node details if verbose
        if builder.nodes:
            click.echo("\nNodes:")
            for node_id, node in builder.nodes.items():
                click.echo(f"  {node_id}: {node.label} ({node.shape.name})")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()