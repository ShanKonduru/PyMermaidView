"""
Mermaid Flowchart Builder - OOP-based flowchart construction
This module provides classes for building Mermaid flowcharts programmatically.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import re


class NodeShape(Enum):
    """Supported node shapes in Mermaid flowcharts."""
    RECTANGLE = "rect"
    ROUND_RECT = "round"
    STADIUM = "stadium"
    SUBROUTINE = "subroutine"
    CYLINDER = "cylinder"
    CIRCLE = "circle"
    ASYMMETRIC = "asymmetric"
    RHOMBUS = "rhombus"
    HEXAGON = "hexagon"
    PARALLELOGRAM = "parallelogram"
    PARALLELOGRAM_ALT = "parallelogram_alt"
    TRAPEZOID = "trapezoid"
    TRAPEZOID_ALT = "trapezoid_alt"


class ArrowType(Enum):
    """Supported arrow types for connections."""
    ARROW = "-->"
    OPEN = "---"
    DOTTED_ARROW = "-.->"
    DOTTED_OPEN = "-.-"
    THICK_ARROW = "==>"
    THICK_OPEN = "==="
    INVISIBLE = "~~~"


class Direction(Enum):
    """Flowchart directions."""
    TOP_BOTTOM = "TD"
    TOP_DOWN = "TD"
    BOTTOM_TOP = "BT"
    RIGHT_LEFT = "RL" 
    LEFT_RIGHT = "LR"


@dataclass
class NodeStyle:
    """Style configuration for flowchart nodes."""
    fill_color: Optional[str] = None
    stroke_color: Optional[str] = None
    stroke_width: Optional[int] = None
    color: Optional[str] = None  # text color
    font_size: Optional[str] = None
    font_weight: Optional[str] = None
    
    def to_css(self) -> str:
        """Convert style to CSS string."""
        styles = []
        if self.fill_color:
            styles.append(f"fill:{self.fill_color}")
        if self.stroke_color:
            styles.append(f"stroke:{self.stroke_color}")
        if self.stroke_width:
            styles.append(f"stroke-width:{self.stroke_width}px")
        if self.color:
            styles.append(f"color:{self.color}")
        if self.font_size:
            styles.append(f"font-size:{self.font_size}")
        if self.font_weight:
            styles.append(f"font-weight:{self.font_weight}")
        return ",".join(styles)


class FlowchartNode:
    """Represents a node in a Mermaid flowchart."""
    
    def __init__(self, node_id: str, label: str, shape: NodeShape = NodeShape.RECTANGLE):
        self.node_id = self._sanitize_id(node_id)
        self.label = label
        self.shape = shape
        self.style: Optional[NodeStyle] = None
        self.css_class: Optional[str] = None
        self.click_action: Optional[str] = None
        self.href_link: Optional[str] = None
        
    def _sanitize_id(self, node_id: str) -> str:
        """Sanitize node ID to be valid for Mermaid."""
        # Remove special characters and replace with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', node_id)
        # Ensure it starts with a letter or underscore
        if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = 'node_' + sanitized
        return sanitized or 'node'
    
    def set_style(self, style: NodeStyle) -> 'FlowchartNode':
        """Set the style for this node."""
        self.style = style
        return self
    
    def set_css_class(self, css_class: str) -> 'FlowchartNode':
        """Set CSS class for this node."""
        self.css_class = css_class
        return self
    
    def set_click_action(self, action: str) -> 'FlowchartNode':
        """Set click action for this node."""
        self.click_action = action
        return self
    
    def set_href_link(self, url: str, tooltip: Optional[str] = None) -> 'FlowchartNode':
        """Set hyperlink for this node."""
        self.href_link = f'"{url}"' + (f' "{tooltip}"' if tooltip else '')
        return self
    
    def to_mermaid(self) -> str:
        """Convert node to Mermaid syntax."""
        shape_syntax = {
            NodeShape.RECTANGLE: f"{self.node_id}[{self.label}]",
            NodeShape.ROUND_RECT: f"{self.node_id}({self.label})",
            NodeShape.STADIUM: f"{self.node_id}([{self.label}])",
            NodeShape.SUBROUTINE: f"{self.node_id}[[{self.label}]]",
            NodeShape.CYLINDER: f"{self.node_id}[({self.label})]",
            NodeShape.CIRCLE: f"{self.node_id}(({self.label}))",
            NodeShape.ASYMMETRIC: f"{self.node_id}>{self.label}]",
            NodeShape.RHOMBUS: f"{self.node_id}{{{self.label}}}",
            NodeShape.HEXAGON: f"{self.node_id}{{{{{self.label}}}}}",
            NodeShape.PARALLELOGRAM: f"{self.node_id}[/{self.label}/]",
            NodeShape.PARALLELOGRAM_ALT: f"{self.node_id}[\\{self.label}\\]",
            NodeShape.TRAPEZOID: f"{self.node_id}[/{self.label}\\]",
            NodeShape.TRAPEZOID_ALT: f"{self.node_id}[\\{self.label}/]",
        }
        return shape_syntax.get(self.shape, f"{self.node_id}[{self.label}]")


class FlowchartConnection:
    """Represents a connection between nodes in a flowchart."""
    
    def __init__(self, from_node: str, to_node: str, arrow_type: ArrowType = ArrowType.ARROW, label: Optional[str] = None):
        self.from_node = from_node
        self.to_node = to_node
        self.arrow_type = arrow_type
        self.label = label
        
    def to_mermaid(self) -> str:
        """Convert connection to Mermaid syntax."""
        if self.label:
            return f"{self.from_node} {self.arrow_type.value} |{self.label}| {self.to_node}"
        else:
            return f"{self.from_node} {self.arrow_type.value} {self.to_node}"


class SubgraphContainer:
    """Represents a subgraph container in Mermaid flowcharts."""
    
    def __init__(self, subgraph_id: str, title: Optional[str] = None):
        self.subgraph_id = subgraph_id
        self.title = title or subgraph_id
        self.nodes: List[FlowchartNode] = []
        self.connections: List[FlowchartConnection] = []
        self.nested_subgraphs: List['SubgraphContainer'] = []
        
    def add_node(self, node: FlowchartNode) -> 'SubgraphContainer':
        """Add a node to this subgraph."""
        self.nodes.append(node)
        return self
    
    def add_connection(self, connection: FlowchartConnection) -> 'SubgraphContainer':
        """Add a connection to this subgraph."""
        self.connections.append(connection)
        return self
    
    def add_subgraph(self, subgraph: 'SubgraphContainer') -> 'SubgraphContainer':
        """Add a nested subgraph."""
        self.nested_subgraphs.append(subgraph)
        return self
    
    def to_mermaid(self, indent_level: int = 1) -> str:
        """Convert subgraph to Mermaid syntax."""
        indent = "    " * indent_level
        lines = [f"{indent}subgraph {self.subgraph_id} [{self.title}]"]
        
        # Add nodes
        for node in self.nodes:
            lines.append(f"{indent}    {node.to_mermaid()}")
        
        # Add nested subgraphs
        for subgraph in self.nested_subgraphs:
            lines.extend(subgraph.to_mermaid(indent_level + 1).split('\n'))
        
        # Add connections
        for connection in self.connections:
            lines.append(f"{indent}    {connection.to_mermaid()}")
        
        lines.append(f"{indent}end")
        return '\n'.join(lines)


class FlowchartBuilder:
    """Builder class for constructing Mermaid flowcharts using fluent interface."""
    
    def __init__(self, title: Optional[str] = None):
        self.title = title
        self.direction: Direction = Direction.TOP_BOTTOM
        self.nodes: Dict[str, FlowchartNode] = {}
        self.connections: List[FlowchartConnection] = []
        self.subgraphs: List[SubgraphContainer] = []
        self.styles: Dict[str, NodeStyle] = {}
        self.css_classes: Dict[str, str] = {}
        self.click_actions: Dict[str, str] = {}
        self.href_links: Dict[str, str] = {}
        
    def set_direction(self, direction: Direction) -> 'FlowchartBuilder':
        """Set the flowchart direction."""
        self.direction = direction
        return self
    
    def add_node(self, node_id: str, label: str, shape: NodeShape = NodeShape.RECTANGLE) -> 'FlowchartBuilder':
        """Add a node to the flowchart."""
        node = FlowchartNode(node_id, label, shape)
        self.nodes[node.node_id] = node
        return self
    
    def add_decision_node(self, node_id: str, label: str) -> 'FlowchartBuilder':
        """Add a decision (diamond) node."""
        return self.add_node(node_id, label, NodeShape.RHOMBUS)
    
    def add_process_node(self, node_id: str, label: str) -> 'FlowchartBuilder':
        """Add a process (rectangle) node."""
        return self.add_node(node_id, label, NodeShape.RECTANGLE)
    
    def add_start_end_node(self, node_id: str, label: str) -> 'FlowchartBuilder':
        """Add a start/end (stadium) node."""
        return self.add_node(node_id, label, NodeShape.STADIUM)
    
    def connect(self, from_node: str, to_node: str, arrow_type: ArrowType = ArrowType.ARROW, label: Optional[str] = None) -> 'FlowchartBuilder':
        """Connect two nodes."""
        connection = FlowchartConnection(from_node, to_node, arrow_type, label)
        self.connections.append(connection)
        return self
    
    def connect_with_label(self, from_node: str, to_node: str, label: str, arrow_type: ArrowType = ArrowType.ARROW) -> 'FlowchartBuilder':
        """Connect two nodes with a label."""
        return self.connect(from_node, to_node, arrow_type, label)
    
    def add_subgraph(self, subgraph_id: str, title: Optional[str] = None) -> SubgraphContainer:
        """Add a subgraph and return it for further configuration."""
        subgraph = SubgraphContainer(subgraph_id, title)
        self.subgraphs.append(subgraph)
        return subgraph
    
    def style_node(self, node_id: str, style: NodeStyle) -> 'FlowchartBuilder':
        """Apply style to a specific node."""
        if node_id in self.nodes:
            self.nodes[node_id].set_style(style)
        self.styles[node_id] = style
        return self
    
    def add_css_class(self, class_name: str, css_definition: str) -> 'FlowchartBuilder':
        """Add a CSS class definition."""
        self.css_classes[class_name] = css_definition
        return self
    
    def apply_css_class(self, node_id: str, class_name: str) -> 'FlowchartBuilder':
        """Apply CSS class to a node."""
        if node_id in self.nodes:
            self.nodes[node_id].set_css_class(class_name)
        return self
    
    def add_click_action(self, node_id: str, action: str) -> 'FlowchartBuilder':
        """Add click action to a node."""
        if node_id in self.nodes:
            self.nodes[node_id].set_click_action(action)
        self.click_actions[node_id] = action
        return self
    
    def add_href_link(self, node_id: str, url: str, tooltip: Optional[str] = None) -> 'FlowchartBuilder':
        """Add hyperlink to a node."""
        if node_id in self.nodes:
            self.nodes[node_id].set_href_link(url, tooltip)
        self.href_links[node_id] = f'"{url}"' + (f' "{tooltip}"' if tooltip else '')
        return self
    
    def build(self) -> str:
        """Build the complete Mermaid flowchart syntax."""
        lines = []
        
        # Add title if provided
        if self.title:
            lines.append(f"---")
            lines.append(f"title: {self.title}")
            lines.append(f"---")
        
        # Add flowchart declaration with direction
        lines.append(f"flowchart {self.direction.value}")
        
        # Add nodes
        for node in self.nodes.values():
            lines.append(f"    {node.to_mermaid()}")
        
        # Add subgraphs
        for subgraph in self.subgraphs:
            lines.append(subgraph.to_mermaid())
        
        # Add connections
        for connection in self.connections:
            lines.append(f"    {connection.to_mermaid()}")
        
        # Add CSS class definitions
        for class_name, css_def in self.css_classes.items():
            lines.append(f"    classDef {class_name} {css_def}")
        
        # Add node styles
        for node_id, style in self.styles.items():
            if style.to_css():
                lines.append(f"    style {node_id} {style.to_css()}")
        
        # Add click actions
        for node_id, action in self.click_actions.items():
            lines.append(f"    click {node_id} {action}")
        
        # Add href links
        for node_id, link in self.href_links.items():
            lines.append(f"    click {node_id} href {link}")
        
        return '\n'.join(lines)
    
    def save_to_file(self, file_path: Path) -> Path:
        """Save the flowchart to a .mmd file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        mermaid_code = self.build()
        file_path.write_text(mermaid_code, encoding='utf-8')
        
        return file_path


class FlowchartParser:
    """Parser for existing Mermaid flowchart syntax."""
    
    def __init__(self):
        self.current_builder: Optional[FlowchartBuilder] = None
    
    def parse_file(self, file_path: Path) -> FlowchartBuilder:
        """Parse a Mermaid file and return a FlowchartBuilder."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path.read_text(encoding='utf-8')
        return self.parse_string(content)
    
    def parse_string(self, mermaid_code: str) -> FlowchartBuilder:
        """Parse Mermaid code string and return a FlowchartBuilder."""
        self.current_builder = FlowchartBuilder()
        lines = [line.strip() for line in mermaid_code.split('\n') if line.strip()]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip comments
            if line.startswith('%%'):
                i += 1
                continue
            
            # Parse title
            if line == '---':
                i += 1
                while i < len(lines) and lines[i] != '---':
                    if lines[i].startswith('title:'):
                        self.current_builder.title = lines[i][6:].strip()
                    i += 1
                i += 1
                continue
            
            # Parse flowchart direction
            if line.startswith('flowchart '):
                direction_str = line[10:].strip()
                try:
                    direction = Direction(direction_str)
                    self.current_builder.set_direction(direction)
                except ValueError:
                    pass  # Unknown direction, use default
                i += 1
                continue
            
            # Parse nodes and connections
            self._parse_flowchart_line(line)
            i += 1
        
        return self.current_builder
    
    def _parse_flowchart_line(self, line: str):
        """Parse individual flowchart line."""
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('%%'):
            return
        
        # Parse connections (contains arrows)
        if any(arrow.value in line for arrow in ArrowType):
            self._parse_connection(line)
        
        # Parse node definitions
        elif any(char in line for char in ['[', '(', '{', '>']):
            self._parse_node_definition(line)
        
        # Parse style definitions
        elif line.startswith('style '):
            self._parse_style_definition(line)
        
        # Parse CSS class definitions
        elif line.startswith('classDef '):
            self._parse_class_definition(line)
        
        # Parse click actions
        elif line.startswith('click '):
            self._parse_click_action(line)
    
    def _parse_connection(self, line: str):
        """Parse connection/arrow syntax."""
        # This is a simplified parser - could be enhanced for complex cases
        for arrow_type in ArrowType:
            if arrow_type.value in line:
                parts = line.split(arrow_type.value)
                if len(parts) == 2:
                    from_node = parts[0].strip()
                    to_part = parts[1].strip()
                    
                    # Check for label
                    if '|' in to_part:
                        # Handle labeled connections
                        label_match = re.search(r'\|([^|]+)\|', line)
                        if label_match:
                            label = label_match.group(1).strip()
                            to_node = re.sub(r'\|[^|]+\|', '', to_part).strip()
                        else:
                            label = None
                            to_node = to_part
                    else:
                        label = None
                        to_node = to_part
                    
                    self.current_builder.connect(from_node, to_node, arrow_type, label)
                    break
    
    def _parse_node_definition(self, line: str):
        """Parse node definition syntax."""
        # Extract node ID and shape/label
        # This is simplified - could be enhanced for all shape types
        
        # Rectangle [label]
        rect_match = re.match(r'(\w+)\[([^\]]+)\]', line)
        if rect_match:
            node_id, label = rect_match.groups()
            self.current_builder.add_node(node_id, label, NodeShape.RECTANGLE)
            return
        
        # Round (label)
        round_match = re.match(r'(\w+)\(([^)]+)\)', line)
        if round_match:
            node_id, label = round_match.groups()
            self.current_builder.add_node(node_id, label, NodeShape.ROUND_RECT)
            return
        
        # Diamond {label}
        diamond_match = re.match(r'(\w+)\{([^}]+)\}', line)
        if diamond_match:
            node_id, label = diamond_match.groups()
            self.current_builder.add_node(node_id, label, NodeShape.RHOMBUS)
            return
    
    def _parse_style_definition(self, line: str):
        """Parse style definition."""
        # Example: style A fill:#f9f,stroke:#333,stroke-width:4px
        parts = line.split(' ', 2)
        if len(parts) >= 3:
            node_id = parts[1]
            style_str = parts[2]
            # Parse CSS-like style string into NodeStyle
            # This is simplified implementation
            style = NodeStyle()
            for style_part in style_str.split(','):
                if ':' in style_part:
                    prop, value = style_part.split(':', 1)
                    prop = prop.strip()
                    value = value.strip()
                    
                    if prop == 'fill':
                        style.fill_color = value
                    elif prop == 'stroke':
                        style.stroke_color = value
                    elif prop == 'stroke-width':
                        style.stroke_width = int(value.replace('px', ''))
                    elif prop == 'color':
                        style.color = value
            
            self.current_builder.style_node(node_id, style)
    
    def _parse_class_definition(self, line: str):
        """Parse CSS class definition."""
        # Example: classDef default fill:#f9f,stroke:#333,stroke-width:2px
        parts = line.split(' ', 2)
        if len(parts) >= 3:
            class_name = parts[1]
            css_def = parts[2]
            self.current_builder.add_css_class(class_name, css_def)
    
    def _parse_click_action(self, line: str):
        """Parse click action definition."""
        # Example: click A href "http://example.com"
        parts = line.split(' ', 2)
        if len(parts) >= 3:
            node_id = parts[1]
            action = parts[2]
            
            if action.startswith('href'):
                # Extract URL from quotes
                url_match = re.search(r'"([^"]+)"', action)
                if url_match:
                    url = url_match.group(1)
                    # Check for tooltip
                    tooltip_match = re.search(r'"[^"]+" "([^"]+)"', action)
                    tooltip = tooltip_match.group(1) if tooltip_match else None
                    self.current_builder.add_href_link(node_id, url, tooltip)
            else:
                self.current_builder.add_click_action(node_id, action)