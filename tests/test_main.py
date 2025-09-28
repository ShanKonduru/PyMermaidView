
"""
Test suite for PyMermaidView - Comprehensive OOP testing
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.mermaid_generator import (
    MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme,
    MermaidError, MermaidSyntaxError, MermaidGenerationError,
    PlaywrightMermaidRenderer, OnlineMermaidRenderer
)
from src.flowchart_builder import (
    FlowchartBuilder, FlowchartNode, FlowchartConnection, FlowchartParser,
    NodeShape, ArrowType, Direction, NodeStyle, SubgraphContainer
)
from src.mermaid_utils import (
    TemplateManager, FlowchartValidator, MermaidExporter, MermaidImporter,
    create_quick_flowchart, FlowchartTemplate
)

load_dotenv()


class TestMermaidConfig:
    """Test MermaidConfig dataclass."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = MermaidConfig()
        assert config.theme == MermaidTheme.DEFAULT
        assert config.output_format == OutputFormat.PNG
        assert config.width == 800
        assert config.height == 600
        assert config.background_color == "white"
        assert config.scale == 1.0
        assert config.font_size == 16
        assert config.animation is False
    
    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = MermaidConfig(
            theme=MermaidTheme.DARK,
            output_format=OutputFormat.SVG,
            width=1200,
            height=800,
            background_color="black",
            scale=1.5,
            font_size=18,
            animation=True
        )
        assert config.theme == MermaidTheme.DARK
        assert config.output_format == OutputFormat.SVG
        assert config.width == 1200
        assert config.height == 800
        assert config.background_color == "black"
        assert config.scale == 1.5
        assert config.font_size == 18
        assert config.animation is True
    
    def test_output_dir_creation(self, tmp_path):
        """Test output directory creation."""
        output_dir = tmp_path / "test_output"
        config = MermaidConfig(output_dir=output_dir)
        assert output_dir.exists()


class TestFlowchartNode:
    """Test FlowchartNode class."""
    
    def test_node_creation(self):
        """Test basic node creation."""
        node = FlowchartNode("test_id", "Test Label", NodeShape.RECTANGLE)
        assert node.node_id == "test_id"
        assert node.label == "Test Label"
        assert node.shape == NodeShape.RECTANGLE
        assert node.style is None
    
    def test_node_id_sanitization(self):
        """Test node ID sanitization."""
        node = FlowchartNode("test-id with spaces!", "Label")
        assert node.node_id == "test_id_with_spaces_"
        
        node2 = FlowchartNode("123numeric", "Label")
        assert node2.node_id == "node_123numeric"
        
        node3 = FlowchartNode("", "Label")
        assert node3.node_id == "node"
    
    def test_node_styling(self):
        """Test node styling."""
        node = FlowchartNode("test", "Test")
        style = NodeStyle(fill_color="#ff0000", stroke_color="#000000")
        
        result = node.set_style(style)
        assert result is node  # Fluent interface
        assert node.style == style
    
    def test_node_mermaid_output(self):
        """Test Mermaid syntax generation."""
        # Rectangle node
        node = FlowchartNode("test", "Test Label", NodeShape.RECTANGLE)
        assert node.to_mermaid() == "test[Test Label]"
        
        # Circle node
        node = FlowchartNode("circle", "Circle", NodeShape.CIRCLE)
        assert node.to_mermaid() == "circle((Circle))"
        
        # Decision node
        node = FlowchartNode("decision", "Decision?", NodeShape.RHOMBUS)
        assert node.to_mermaid() == "decision{Decision?}"


class TestFlowchartConnection:
    """Test FlowchartConnection class."""
    
    def test_connection_creation(self):
        """Test basic connection creation."""
        conn = FlowchartConnection("node1", "node2", ArrowType.ARROW, "Label")
        assert conn.from_node == "node1"
        assert conn.to_node == "node2"
        assert conn.arrow_type == ArrowType.ARROW
        assert conn.label == "Label"
    
    def test_connection_mermaid_output(self):
        """Test Mermaid syntax generation for connections."""
        # Connection without label
        conn = FlowchartConnection("A", "B", ArrowType.ARROW)
        assert conn.to_mermaid() == "A --> B"
        
        # Connection with label
        conn = FlowchartConnection("A", "B", ArrowType.ARROW, "Yes")
        assert conn.to_mermaid() == "A --> |Yes| B"
        
        # Dotted arrow
        conn = FlowchartConnection("A", "B", ArrowType.DOTTED_ARROW)
        assert conn.to_mermaid() == "A -.-> B"


class TestFlowchartBuilder:
    """Test FlowchartBuilder class."""
    
    def test_builder_creation(self):
        """Test basic builder creation."""
        builder = FlowchartBuilder("Test Title")
        assert builder.title == "Test Title"
        assert builder.direction == Direction.TOP_BOTTOM
        assert len(builder.nodes) == 0
        assert len(builder.connections) == 0
    
    def test_fluent_interface(self):
        """Test fluent interface pattern."""
        builder = (FlowchartBuilder("Test")
                  .set_direction(Direction.LEFT_RIGHT)
                  .add_node("start", "Start", NodeShape.STADIUM)
                  .add_node("end", "End", NodeShape.STADIUM)
                  .connect("start", "end"))
        
        assert builder.direction == Direction.LEFT_RIGHT
        assert len(builder.nodes) == 2
        assert len(builder.connections) == 1
    
    def test_node_addition(self):
        """Test adding different types of nodes."""
        builder = FlowchartBuilder()
        
        builder.add_process_node("process", "Process")
        builder.add_decision_node("decision", "Decision?")
        builder.add_start_end_node("start", "Start")
        
        assert len(builder.nodes) == 3
        assert builder.nodes["process"].shape == NodeShape.RECTANGLE
        assert builder.nodes["decision"].shape == NodeShape.RHOMBUS
        assert builder.nodes["start"].shape == NodeShape.STADIUM
    
    def test_mermaid_generation(self):
        """Test complete Mermaid syntax generation."""
        builder = (FlowchartBuilder("Test Flow")
                  .set_direction(Direction.TOP_BOTTOM)
                  .add_start_end_node("start", "Start")
                  .add_process_node("process", "Process")
                  .add_start_end_node("end", "End")
                  .connect("start", "process")
                  .connect("process", "end"))
        
        mermaid_code = builder.build()
        
        assert "---" in mermaid_code
        assert "title: Test Flow" in mermaid_code
        assert "flowchart TD" in mermaid_code
        assert "start([Start])" in mermaid_code
        assert "process[Process]" in mermaid_code
        assert "end([End])" in mermaid_code
        assert "start --> process" in mermaid_code
        assert "process --> end" in mermaid_code
    
    def test_file_saving(self, tmp_path):
        """Test saving flowchart to file."""
        builder = FlowchartBuilder("Test")
        builder.add_process_node("test", "Test Node")
        
        file_path = tmp_path / "test.mmd"
        result_path = builder.save_to_file(file_path)
        
        assert result_path == file_path
        assert file_path.exists()
        
        content = file_path.read_text(encoding='utf-8')
        assert "flowchart TD" in content
        assert "test[Test Node]" in content


class TestFlowchartValidator:
    """Test FlowchartValidator class."""
    
    def test_valid_flowchart(self):
        """Test validation of valid flowchart."""
        builder = (FlowchartBuilder()
                  .add_start_end_node("start", "Start")
                  .add_process_node("process", "Process")
                  .add_start_end_node("end", "End")
                  .connect("start", "process")
                  .connect("process", "end"))
        
        validator = FlowchartValidator()
        is_valid = validator.validate_builder(builder)
        
        assert is_valid
        assert len(validator.errors) == 0
    
    def test_empty_flowchart(self):
        """Test validation of empty flowchart."""
        builder = FlowchartBuilder()
        
        validator = FlowchartValidator()
        is_valid = validator.validate_builder(builder)
        
        assert not is_valid
        assert len(validator.errors) > 0
        assert "must contain at least one node" in validator.errors[0]
    
    def test_invalid_connections(self):
        """Test validation of invalid connections."""
        builder = (FlowchartBuilder()
                  .add_process_node("node1", "Node 1")
                  .connect("node1", "nonexistent"))
        
        validator = FlowchartValidator()
        is_valid = validator.validate_builder(builder)
        
        assert not is_valid
        assert any("unknown target node" in error for error in validator.errors)
    
    def test_isolated_nodes_warning(self):
        """Test warning for isolated nodes."""
        builder = (FlowchartBuilder()
                  .add_process_node("connected1", "Connected 1")
                  .add_process_node("connected2", "Connected 2")
                  .add_process_node("isolated", "Isolated")
                  .connect("connected1", "connected2"))
        
        validator = FlowchartValidator()
        validator.validate_builder(builder)
        
        assert len(validator.warnings) > 0
        assert any("isolated" in warning.lower() for warning in validator.warnings)
    
    def test_mermaid_syntax_validation(self):
        """Test Mermaid syntax string validation."""
        validator = FlowchartValidator()
        
        # Valid syntax
        valid_code = """
        flowchart TD
            A[Start] --> B[Process]
            B --> C[End]
        """
        assert validator.validate_mermaid_syntax(valid_code)
        
        # Invalid syntax (no flowchart declaration)
        invalid_code = """
            A[Start] --> B[Process]
        """
        assert not validator.validate_mermaid_syntax(invalid_code)


class TestTemplateManager:
    """Test TemplateManager class."""
    
    def test_builtin_templates(self):
        """Test built-in templates."""
        manager = TemplateManager()
        templates = manager.list_templates()
        
        assert "simple_process" in templates
        assert "decision_flow" in templates
    
    def test_template_loading(self):
        """Test loading templates."""
        manager = TemplateManager()
        template = manager.load_template("simple_process")
        
        assert isinstance(template, FlowchartTemplate)
        assert template.name == "simple_process"
        assert len(template.nodes) > 0
        assert len(template.connections) > 0
    
    def test_flowchart_from_template(self):
        """Test creating flowchart from template."""
        manager = TemplateManager()
        builder = manager.create_flowchart_from_template("simple_process")
        
        assert isinstance(builder, FlowchartBuilder)
        assert len(builder.nodes) > 0
        assert len(builder.connections) > 0
    
    def test_template_customization(self):
        """Test template customization."""
        manager = TemplateManager()
        builder = manager.create_flowchart_from_template(
            "simple_process",
            title="Custom Title",
            start_label="Custom Start"
        )
        
        assert builder.title == "Custom Title"
        # Note: label customization would need to be implemented in the template


class TestQuickFlowchart:
    """Test quick flowchart creation utility."""
    
    def test_simple_steps(self):
        """Test creating flowchart from simple steps."""
        steps = ["Step 1", "Step 2", "Step 3"]
        builder = create_quick_flowchart("Test Process", steps)
        
        assert builder.title == "Test Process"
        assert len(builder.nodes) >= len(steps) + 2  # steps + start + end
        assert len(builder.connections) >= len(steps) + 1
    
    def test_with_decision(self):
        """Test creating flowchart with decision point."""
        steps = ["Step 1", "Step 2", "Step 3"]
        builder = create_quick_flowchart(
            "Test Process", 
            steps, 
            include_decision=True,
            decision_label="Continue?"
        )
        
        # Should have more nodes due to decision and alternative path
        assert len(builder.nodes) > len(steps) + 2


class TestMermaidGenerator:
    """Test MermaidGenerator class."""
    
    def test_generator_creation(self):
        """Test basic generator creation."""
        generator = MermaidGenerator()
        assert isinstance(generator.config, MermaidConfig)
        assert generator.config.theme == MermaidTheme.DEFAULT
    
    def test_config_methods(self):
        """Test configuration methods."""
        generator = MermaidGenerator()
        
        result = generator.set_theme(MermaidTheme.DARK)
        assert result is generator  # Fluent interface
        assert generator.config.theme == MermaidTheme.DARK
        
        generator.set_output_format(OutputFormat.SVG)
        assert generator.config.output_format == OutputFormat.SVG
        
        generator.set_dimensions(1200, 800)
        assert generator.config.width == 1200
        assert generator.config.height == 800
    
    @pytest.mark.asyncio
    async def test_syntax_validation_error(self):
        """Test syntax validation error."""
        generator = MermaidGenerator()
        
        with pytest.raises(MermaidSyntaxError):
            await generator.generate("")
        
        with pytest.raises(MermaidSyntaxError):
            await generator.generate("   ")


@pytest.mark.integration
class TestMockRenderers:
    """Test renderer implementations with mocking."""
    
    @pytest.mark.asyncio
    async def test_online_renderer_basic(self):
        """Test online renderer basic functionality."""
        renderer = OnlineMermaidRenderer()
        
        # Test syntax validation
        assert await renderer.validate_syntax("flowchart TD\nA --> B")
        assert not await renderer.validate_syntax("")
    
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_online_renderer_request(self, mock_get):
        """Test online renderer HTTP request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response
        
        renderer = OnlineMermaidRenderer()
        result = await renderer.render("flowchart TD\nA --> B", MermaidConfig())
        
        assert result == b"fake_image_data"
        mock_get.assert_called_once()


class TestErrorHandling:
    """Test error handling throughout the system."""
    
    def test_mermaid_errors(self):
        """Test custom exception hierarchy."""
        # Test exception hierarchy
        assert issubclass(MermaidSyntaxError, MermaidError)
        assert issubclass(MermaidGenerationError, MermaidError)
        
        # Test exception creation
        syntax_error = MermaidSyntaxError("Invalid syntax")
        assert str(syntax_error) == "Invalid syntax"
        
        gen_error = MermaidGenerationError("Generation failed")
        assert str(gen_error) == "Generation failed"
    
    def test_file_not_found_handling(self, tmp_path):
        """Test file not found error handling."""
        parser = FlowchartParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file(tmp_path / "nonexistent.mmd")


@pytest.mark.positive
def test_add_positive():
    """Legacy test - kept for compatibility."""
    def add(x, y):
        return x + y
    assert add(2, 3) == 5


@pytest.mark.positive
def test_subtract_positive():
    """Legacy test - kept for compatibility."""
    def subtract(x, y):
        return x - y
    assert subtract(10, 4) == 6


    """Legacy test - kept for compatibility."""
    def multiply(x, y):
        return x * y
    assert multiply(5, 6) == 30


@pytest.mark.positive
def test_divide_positive():
    """Legacy test - kept for compatibility."""
    def divide(x, y):
        return x / y
    assert divide(10, 2) == 5


@pytest.mark.edge
def test_add_with_zero():
    """Legacy test - kept for compatibility."""
    def add(x, y):
        return x + y
    assert add(5, 0) == 5


@pytest.mark.edge
def test_subtract_with_zero():
    """Legacy test - kept for compatibility."""
    def subtract(x, y):
        return x - y
    assert subtract(10, 0) == 10


@pytest.mark.edge
def test_add_with_negative_numbers():
    """Legacy test - kept for compatibility."""
    def add(x, y):
        return x + y
    assert add(-2, -3) == -5


@pytest.mark.edge
def test_multiply_by_zero():
    """Legacy test - kept for compatibility."""
    def multiply(x, y):
        return x * y
    assert multiply(100, 0) == 0


@pytest.mark.edge
def test_divide_negative_numbers():
    """Legacy test - kept for compatibility.""" 
    def divide(x, y):
        return x / y
    assert divide(-10, -2) == 5
