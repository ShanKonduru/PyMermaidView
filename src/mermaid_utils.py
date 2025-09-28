"""
Mermaid Utilities - Helper classes and functions
This module provides utility classes for common Mermaid operations.
"""

import json
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from .flowchart_builder import FlowchartBuilder, NodeShape, ArrowType, Direction, NodeStyle
from .mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme


@dataclass
class FlowchartTemplate:
    """Template for creating common flowchart patterns."""
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    styles: Optional[Dict[str, Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowchartTemplate':
        """Create template from dictionary."""
        return cls(**data)


class TemplateManager:
    """Manager for flowchart templates."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path("./templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._templates: Dict[str, FlowchartTemplate] = {}
        self._load_builtin_templates()
    
    def _load_builtin_templates(self):
        """Load built-in templates."""
        # Simple process flow template
        process_flow = FlowchartTemplate(
            name="simple_process",
            description="Simple linear process flow",
            nodes=[
                {"id": "start", "label": "Start", "shape": "stadium"},
                {"id": "process1", "label": "Process Step 1", "shape": "rect"},
                {"id": "process2", "label": "Process Step 2", "shape": "rect"},
                {"id": "end", "label": "End", "shape": "stadium"}
            ],
            connections=[
                {"from": "start", "to": "process1", "arrow_type": "-->"},
                {"from": "process1", "to": "process2", "arrow_type": "-->"},
                {"from": "process2", "to": "end", "arrow_type": "-->"}
            ]
        )
        
        # Decision flow template
        decision_flow = FlowchartTemplate(
            name="decision_flow",
            description="Flow with decision points",
            nodes=[
                {"id": "start", "label": "Start", "shape": "stadium"},
                {"id": "input", "label": "Get Input", "shape": "rect"},
                {"id": "decision", "label": "Valid Input?", "shape": "rhombus"},
                {"id": "process", "label": "Process Data", "shape": "rect"},
                {"id": "error", "label": "Show Error", "shape": "rect"},
                {"id": "end", "label": "End", "shape": "stadium"}
            ],
            connections=[
                {"from": "start", "to": "input", "arrow_type": "-->"},
                {"from": "input", "to": "decision", "arrow_type": "-->"},
                {"from": "decision", "to": "process", "label": "Yes", "arrow_type": "-->"},
                {"from": "decision", "to": "error", "label": "No", "arrow_type": "-->"},
                {"from": "process", "to": "end", "arrow_type": "-->"},
                {"from": "error", "to": "input", "arrow_type": "-->"}
            ],
            styles={
                "error": {"fill_color": "#ffcccc", "stroke_color": "#ff0000"},
                "process": {"fill_color": "#ccffcc", "stroke_color": "#00aa00"}
            }
        )
        
        self._templates["simple_process"] = process_flow
        self._templates["decision_flow"] = decision_flow
    
    def save_template(self, template: FlowchartTemplate, filename: Optional[str] = None) -> Path:
        """Save template to file."""
        if not filename:
            filename = f"{template.name}.json"
        
        file_path = self.templates_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2)
        
        self._templates[template.name] = template
        return file_path
    
    def load_template(self, name_or_path: Union[str, Path]) -> FlowchartTemplate:
        """Load template by name or file path."""
        # Check if it's a built-in template
        if isinstance(name_or_path, str) and name_or_path in self._templates:
            return self._templates[name_or_path]
        
        # Try to load from file
        if isinstance(name_or_path, str):
            file_path = self.templates_dir / f"{name_or_path}.json"
        else:
            file_path = Path(name_or_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        template = FlowchartTemplate.from_dict(data)
        self._templates[template.name] = template
        return template
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        # Get built-in templates
        templates = list(self._templates.keys())
        
        # Get file-based templates
        for file_path in self.templates_dir.glob("*.json"):
            template_name = file_path.stem
            if template_name not in templates:
                templates.append(template_name)
        
        return sorted(templates)
    
    def create_flowchart_from_template(self, template_name: str, **kwargs) -> FlowchartBuilder:
        """Create a flowchart from template with optional customizations."""
        template = self.load_template(template_name)
        
        builder = FlowchartBuilder(title=kwargs.get('title'))
        
        # Set direction if provided
        if 'direction' in kwargs:
            builder.set_direction(Direction(kwargs['direction']))
        
        # Add nodes
        for node_data in template.nodes:
            node_id = node_data['id']
            label = kwargs.get(f'{node_id}_label', node_data['label'])
            shape = NodeShape(node_data.get('shape', 'rect'))
            builder.add_node(node_id, label, shape)
        
        # Add connections
        for conn_data in template.connections:
            from_node = conn_data['from']
            to_node = conn_data['to']
            label = conn_data.get('label')
            arrow_type_str = conn_data.get('arrow_type', '-->')
            
            # Convert string to ArrowType enum
            arrow_type = ArrowType.ARROW  # default
            for at in ArrowType:
                if at.value == arrow_type_str:
                    arrow_type = at
                    break
            
            builder.connect(from_node, to_node, arrow_type, label)
        
        # Apply styles
        if template.styles:
            for node_id, style_data in template.styles.items():
                style = NodeStyle(**style_data)
                builder.style_node(node_id, style)
        
        return builder


class FlowchartValidator:
    """Validator for flowchart structure and syntax."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_builder(self, builder: FlowchartBuilder) -> bool:
        """Validate a FlowchartBuilder instance."""
        self.errors.clear()
        self.warnings.clear()
        
        # Check for nodes
        if not builder.nodes:
            self.errors.append("Flowchart must contain at least one node")
            return False
        
        # Check node IDs
        node_ids = set(builder.nodes.keys())
        
        # Validate connections
        for connection in builder.connections:
            if connection.from_node not in node_ids:
                self.errors.append(f"Connection references unknown source node: {connection.from_node}")
            
            if connection.to_node not in node_ids:
                self.errors.append(f"Connection references unknown target node: {connection.to_node}")
        
        # Check for isolated nodes
        connected_nodes = set()
        for connection in builder.connections:
            connected_nodes.add(connection.from_node)
            connected_nodes.add(connection.to_node)
        
        isolated_nodes = node_ids - connected_nodes
        if isolated_nodes:
            self.warnings.append(f"Isolated nodes found: {', '.join(isolated_nodes)}")
        
        # Check for potential start/end nodes
        source_nodes = set()
        target_nodes = set()
        for connection in builder.connections:
            source_nodes.add(connection.from_node)
            target_nodes.add(connection.to_node)
        
        start_candidates = source_nodes - target_nodes
        end_candidates = target_nodes - source_nodes
        
        if not start_candidates:
            self.warnings.append("No clear start node found (node with no incoming connections)")
        
        if not end_candidates:
            self.warnings.append("No clear end node found (node with no outgoing connections)")
        
        return len(self.errors) == 0
    
    def validate_mermaid_syntax(self, mermaid_code: str) -> bool:
        """Validate Mermaid syntax string for various diagram types."""
        self.errors.clear()
        self.warnings.clear()
        
        lines = [line.strip() for line in mermaid_code.split('\n') if line.strip()]
        
        if not lines:
            self.errors.append("Empty diagram")
            return False
        
        # Detect diagram type from first line
        first_line = lines[0].lower()
        diagram_type = None
        
        # Supported diagram types
        if first_line.startswith('flowchart '):
            diagram_type = 'flowchart'
        elif first_line.startswith('graph '):
            diagram_type = 'graph'
        elif first_line.startswith('pie'):
            diagram_type = 'pie'
        elif first_line.startswith('quadrantchart'):
            diagram_type = 'quadrant'
        elif first_line.startswith('gitgraph'):
            diagram_type = 'gitgraph'
        elif first_line.startswith('gantt'):
            diagram_type = 'gantt'
        elif first_line.startswith('sequencediagram') or first_line.startswith('sequencediagram'):
            diagram_type = 'sequence'
        elif first_line.startswith('classDiagram'):
            diagram_type = 'class'
        elif first_line.startswith('statediagram'):
            diagram_type = 'state'
        elif first_line.startswith('erdiagram'):
            diagram_type = 'er'
        elif first_line.startswith('journey'):
            diagram_type = 'journey'
        
        if not diagram_type:
            # Try to detect from content patterns
            content = ' '.join(lines).lower()
            if 'pie title' in content:
                diagram_type = 'pie'
            elif '-->' in content or '---' in content:
                self.warnings.append("Detected flowchart connections but missing diagram declaration")
                diagram_type = 'flowchart'
            else:
                self.errors.append("Could not determine diagram type - please add proper diagram declaration")
                return False
        
        # Type-specific validation
        if diagram_type in ['flowchart', 'graph']:
            return self._validate_flowchart_syntax(lines)
        elif diagram_type == 'pie':
            return self._validate_pie_syntax(lines)
        elif diagram_type == 'quadrant':
            return self._validate_quadrant_syntax(lines)
        else:
            # For other types, do basic validation
            self.warnings.append(f"Basic validation only for {diagram_type} diagrams")
            return True
    
    def _validate_flowchart_syntax(self, lines) -> bool:
        """Validate flowchart-specific syntax."""
        has_declaration = False
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.startswith('%%'):
                continue
            
            # Check for flowchart declaration
            if line.startswith('flowchart ') or line.startswith('graph '):
                has_declaration = True
                if line.startswith('flowchart '):
                    direction = line[10:].strip()
                else:
                    direction = line[6:].strip()
                    
                valid_directions = ['TD', 'TB', 'BT', 'RL', 'LR']
                if direction and direction not in valid_directions:
                    self.warnings.append(f"Line {line_num}: Unknown direction '{direction}'")
            
            # Basic syntax checks
            if '-->' in line or '---' in line:
                # Connection line
                if line.count('-->') + line.count('---') > 1:
                    self.warnings.append(f"Line {line_num}: Multiple arrows in single line")
        
        if not has_declaration:
            self.errors.append("Missing 'flowchart' or 'graph' declaration")
        
        return len(self.errors) == 0
    
    def _validate_pie_syntax(self, lines) -> bool:
        """Validate pie chart syntax."""
        has_title = False
        has_data = False
        
        for line_num, line in enumerate(lines, 1):
            if line.startswith('%%'):
                continue
                
            if line.startswith('pie'):
                if 'title' in line:
                    has_title = True
            elif ':' in line and '"' in line:
                has_data = True
        
        if not has_title:
            self.warnings.append("Pie chart should have a title")
        
        if not has_data:
            self.errors.append("Pie chart must have data entries")
        
        return len(self.errors) == 0
    
    def _validate_quadrant_syntax(self, lines) -> bool:
        """Validate quadrant chart syntax."""
        has_title = False
        has_x_axis = False
        has_y_axis = False
        has_quadrants = False
        has_data_points = False
        
        for line_num, line in enumerate(lines, 1):
            if line.startswith('%%'):
                continue
                
            line_lower = line.lower()
            
            if line_lower.startswith('quadrantchart'):
                continue
            elif line_lower.strip().startswith('title '):
                has_title = True
            elif line_lower.strip().startswith('x-axis '):
                has_x_axis = True
            elif line_lower.strip().startswith('y-axis '):
                has_y_axis = True
            elif line_lower.strip().startswith('quadrant-'):
                has_quadrants = True
            elif ':' in line and '[' in line and ']' in line:
                # Data point format: "Name: [x, y]"
                has_data_points = True
        
        # Check required elements
        if not has_title:
            self.warnings.append("Quadrant chart should have a title")
        
        if not has_x_axis:
            self.errors.append("Quadrant chart must have x-axis definition")
        
        if not has_y_axis:
            self.errors.append("Quadrant chart must have y-axis definition")
        
        if not has_quadrants:
            self.warnings.append("Quadrant chart should define quadrant labels")
        
        if not has_data_points:
            self.warnings.append("Quadrant chart should have data points")
        
        return len(self.errors) == 0
    
    def get_validation_report(self) -> str:
        """Get formatted validation report."""
        report_lines = []
        
        if self.errors:
            report_lines.append("ERRORS:")
            for error in self.errors:
                report_lines.append(f"  - {error}")
        
        if self.warnings:
            report_lines.append("WARNINGS:")
            for warning in self.warnings:
                report_lines.append(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            report_lines.append("✓ Validation passed")
        
        return '\n'.join(report_lines)


class MermaidExporter:
    """Exporter for converting flowcharts to various formats."""
    
    def __init__(self):
        self.generator = MermaidGenerator()
    
    async def export_to_image(self, builder: FlowchartBuilder, output_path: Path, 
                            format: OutputFormat = OutputFormat.PNG,
                            theme: MermaidTheme = MermaidTheme.DEFAULT,
                            **config_kwargs) -> Path:
        """Export flowchart to image file."""
        # Configure generator
        self.generator.set_config(
            output_format=format,
            theme=theme,
            **config_kwargs
        )
        
        # Generate mermaid code
        mermaid_code = builder.build()
        
        # Generate image
        return await self.generator.generate(mermaid_code, output_path)
    
    def export_to_json(self, builder: FlowchartBuilder, output_path: Path) -> Path:
        """Export flowchart structure to JSON."""
        data = {
            'title': builder.title,
            'direction': builder.direction.value,
            'nodes': {
                node_id: {
                    'label': node.label,
                    'shape': node.shape.value,
                    'style': asdict(node.style) if node.style else None,
                    'css_class': node.css_class,
                    'click_action': node.click_action,
                    'href_link': node.href_link
                }
                for node_id, node in builder.nodes.items()
            },
            'connections': [
                {
                    'from': conn.from_node,
                    'to': conn.to_node,
                    'arrow_type': conn.arrow_type.value,
                    'label': conn.label
                }
                for conn in builder.connections
            ],
            'subgraphs': [
                {
                    'id': sg.subgraph_id,
                    'title': sg.title,
                    'nodes': len(sg.nodes),
                    'connections': len(sg.connections)
                }
                for sg in builder.subgraphs
            ],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'node_count': len(builder.nodes),
                'connection_count': len(builder.connections),
                'subgraph_count': len(builder.subgraphs)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def export_to_yaml(self, builder: FlowchartBuilder, output_path: Path) -> Path:
        """Export flowchart structure to YAML."""
        # First export to JSON format, then convert to YAML
        json_data = json.loads(self.export_to_json(Path("temp.json"), output_path).read_text())
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(json_data, f, default_flow_style=False, sort_keys=False)
        
        return output_path


class MermaidImporter:
    """Importer for creating flowcharts from various sources."""
    
    def __init__(self):
        pass
    
    def from_json(self, json_path: Path) -> FlowchartBuilder:
        """Import flowchart from JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        builder = FlowchartBuilder(title=data.get('title'))
        
        # Set direction
        if 'direction' in data:
            builder.set_direction(Direction(data['direction']))
        
        # Import nodes
        for node_id, node_data in data.get('nodes', {}).items():
            shape = NodeShape(node_data.get('shape', 'rect'))
            builder.add_node(node_id, node_data['label'], shape)
            
            # Apply style if present
            if node_data.get('style'):
                style = NodeStyle(**node_data['style'])
                builder.style_node(node_id, style)
            
            # Apply other properties
            if node_data.get('css_class'):
                builder.apply_css_class(node_id, node_data['css_class'])
            
            if node_data.get('click_action'):
                builder.add_click_action(node_id, node_data['click_action'])
            
            if node_data.get('href_link'):
                # Parse href link (simplified)
                builder.add_href_link(node_id, node_data['href_link'])
        
        # Import connections
        for conn_data in data.get('connections', []):
            arrow_type_str = conn_data.get('arrow_type', '-->')
            
            # Convert string to ArrowType enum
            arrow_type = ArrowType.ARROW  # default
            for at in ArrowType:
                if at.value == arrow_type_str:
                    arrow_type = at
                    break
            
            builder.connect(
                conn_data['from'],
                conn_data['to'],
                arrow_type,
                conn_data.get('label')
            )
        
        return builder
    
    def from_yaml(self, yaml_path: Path) -> FlowchartBuilder:
        """Import flowchart from YAML file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Convert YAML data to JSON format and use existing JSON importer
        json_path = yaml_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        try:
            return self.from_json(json_path)
        finally:
            # Clean up temporary JSON file
            if json_path.exists():
                json_path.unlink()
    
    def from_csv(self, csv_path: Path, 
                node_columns: Dict[str, str] = None,
                connection_columns: Dict[str, str] = None) -> FlowchartBuilder:
        """Import flowchart from CSV file.
        
        Args:
            csv_path: Path to CSV file
            node_columns: Mapping of CSV columns to node properties
            connection_columns: Mapping of CSV columns to connection properties
        """
        import csv
        
        builder = FlowchartBuilder()
        
        # Default column mappings
        node_cols = node_columns or {'id': 'id', 'label': 'label', 'shape': 'shape'}
        conn_cols = connection_columns or {'from': 'from', 'to': 'to', 'label': 'label'}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Check if this row defines a node or connection
                if all(col in row for col in node_cols.values()):
                    # Node row
                    node_id = row[node_cols['id']]
                    label = row[node_cols['label']]
                    shape_str = row.get(node_cols.get('shape'), 'rect')
                    
                    try:
                        shape = NodeShape(shape_str)
                    except ValueError:
                        shape = NodeShape.RECTANGLE
                    
                    builder.add_node(node_id, label, shape)
                
                elif all(col in row for col in ['from', 'to']):
                    # Connection row
                    from_node = row[conn_cols['from']]
                    to_node = row[conn_cols['to']]
                    label = row.get(conn_cols.get('label'))
                    
                    builder.connect(from_node, to_node, ArrowType.ARROW, label)
        
        return builder


def create_quick_flowchart(title: str, steps: List[str], 
                          include_decision: bool = False,
                          decision_step: int = -1,
                          decision_label: str = "Continue?") -> FlowchartBuilder:
    """Quickly create a simple flowchart from a list of steps."""
    
    builder = FlowchartBuilder(title=title)
    
    # Add start node
    builder.add_start_end_node("start", "Start")
    
    previous_node = "start"
    
    # Add process steps
    for i, step in enumerate(steps):
        node_id = f"step_{i+1}"
        
        if include_decision and i == (decision_step if decision_step >= 0 else len(steps)//2):
            # Add decision node
            decision_id = f"decision_{i+1}"
            builder.add_decision_node(decision_id, decision_label)
            builder.connect(previous_node, decision_id)
            
            # Add the step as process after decision
            builder.add_process_node(node_id, step)
            builder.connect_with_label(decision_id, node_id, "Yes")
            
            # Add alternative path
            alt_node_id = f"alt_{i+1}"
            builder.add_process_node(alt_node_id, "Alternative Action")
            builder.connect_with_label(decision_id, alt_node_id, "No")
            
            previous_node = node_id
        else:
            # Regular process step
            builder.add_process_node(node_id, step)
            builder.connect(previous_node, node_id)
            previous_node = node_id
    
    # Add end node
    builder.add_start_end_node("end", "End")
    builder.connect(previous_node, "end")
    
    return builder