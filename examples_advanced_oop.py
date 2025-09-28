"""
Advanced OOP Examples for PyMermaidView
Demonstrates sophisticated object-oriented programming concepts in Mermaid diagram generation.
"""

import asyncio
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import Windows utilities
from src.windows_utils import run_async_with_cleanup, suppress_windows_asyncio_warnings

# Configure Windows-specific settings
suppress_windows_asyncio_warnings()

from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme
from src.flowchart_builder import (
    FlowchartBuilder, NodeShape, ArrowType, Direction, NodeStyle, FlowchartNode, FlowchartConnection
)
from src.mermaid_utils import TemplateManager, FlowchartValidator


class DiagramType(Enum):
    """Enumeration of supported diagram types."""
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    STATE = "state"
    GANTT = "gantt"


@dataclass
class DiagramMetadata:
    """Metadata for diagram tracking and management."""
    title: str
    author: str
    version: str
    description: str
    tags: List[str]
    diagram_type: DiagramType
    complexity_score: int = 0
    
    def calculate_complexity(self, node_count: int, connection_count: int) -> int:
        """Calculate diagram complexity score."""
        base_score = node_count + (connection_count * 0.5)
        complexity_multiplier = {
            DiagramType.FLOWCHART: 1.0,
            DiagramType.SEQUENCE: 1.2,
            DiagramType.CLASS: 1.5,
            DiagramType.STATE: 1.3,
            DiagramType.GANTT: 1.1
        }
        self.complexity_score = int(base_score * complexity_multiplier.get(self.diagram_type, 1.0))
        return self.complexity_score


class IDiagramBuilder(ABC):
    """Abstract interface for diagram builders."""
    
    @abstractmethod
    def build(self) -> str:
        """Build the diagram syntax."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> DiagramMetadata:
        """Get diagram metadata."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate diagram structure."""
        pass


class ProcessFlowBuilder(IDiagramBuilder):
    """Specialized builder for process flows with business logic validation."""
    
    def __init__(self, process_name: str, owner: str):
        self.metadata = DiagramMetadata(
            title=f"{process_name} Process Flow",
            author=owner,
            version="1.0",
            description=f"Automated process flow for {process_name}",
            tags=["process", "business", "workflow"],
            diagram_type=DiagramType.FLOWCHART
        )
        
        self.builder = FlowchartBuilder(self.metadata.title)
        self.process_steps: List[ProcessStep] = []
        self.decision_points: List[DecisionPoint] = []
        self.parallel_branches: List[ParallelBranch] = []
    
    def add_process_step(self, step: 'ProcessStep') -> 'ProcessFlowBuilder':
        """Add a process step with business rules."""
        self.process_steps.append(step)
        step.add_to_builder(self.builder)
        return self
    
    def add_decision_point(self, decision: 'DecisionPoint') -> 'ProcessFlowBuilder':
        """Add a decision point with branching logic."""
        self.decision_points.append(decision)
        decision.add_to_builder(self.builder)
        return self
    
    def add_parallel_branch(self, branch: 'ParallelBranch') -> 'ProcessFlowBuilder':
        """Add parallel execution branches."""
        self.parallel_branches.append(branch)
        branch.add_to_builder(self.builder)
        return self
    
    def build(self) -> str:
        """Build the complete process flow."""
        # Connect all steps in sequence
        previous_step = None
        for step in self.process_steps:
            if previous_step:
                self.builder.connect(previous_step.node_id, step.node_id)
            previous_step = step
        
        # Connect decision points
        for decision in self.decision_points:
            decision.connect_branches(self.builder)
        
        # Add parallel branches
        for branch in self.parallel_branches:
            branch.create_parallel_flow(self.builder)
        
        return self.builder.build()
    
    def get_metadata(self) -> DiagramMetadata:
        """Get process metadata with calculated complexity."""
        total_nodes = len(self.process_steps) + len(self.decision_points)
        total_connections = len(self.process_steps) - 1 + sum(len(d.branches) for d in self.decision_points)
        
        self.metadata.calculate_complexity(total_nodes, total_connections)
        return self.metadata
    
    def validate(self) -> bool:
        """Validate process flow business rules."""
        validator = FlowchartValidator()
        
        # Check basic structure
        if not validator.validate_builder(self.builder):
            return False
        
        # Business rule validation
        if len(self.process_steps) < 2:
            validator.errors.append("Process must have at least 2 steps")
            return False
        
        # Check for start and end points
        start_nodes = [step for step in self.process_steps if step.step_type == StepType.START]
        end_nodes = [step for step in self.process_steps if step.step_type == StepType.END]
        
        if not start_nodes:
            validator.warnings.append("Process should have a clear start point")
        
        if not end_nodes:
            validator.warnings.append("Process should have a clear end point")
        
        return len(validator.errors) == 0


class StepType(Enum):
    """Types of process steps."""
    START = "start"
    PROCESS = "process"
    DECISION = "decision"
    END = "end"
    PARALLEL = "parallel"
    MERGE = "merge"


class ProcessStep:
    """Represents a single process step with business context."""
    
    def __init__(self, step_id: str, title: str, step_type: StepType, 
                 description: str = "", duration_minutes: int = 0, 
                 responsible_role: str = "", automation_level: str = "manual"):
        self.step_id = step_id
        self.title = title
        self.step_type = step_type
        self.description = description
        self.duration_minutes = duration_minutes
        self.responsible_role = responsible_role
        self.automation_level = automation_level  # manual, semi-automated, automated
        self.node_id = f"step_{step_id}"
        
        # Business attributes
        self.risk_level = "low"  # low, medium, high
        self.compliance_required = False
        self.approvals_needed: List[str] = []
    
    def add_to_builder(self, builder: FlowchartBuilder) -> None:
        """Add this step to a flowchart builder."""
        # Determine node shape based on step type
        shape_mapping = {
            StepType.START: NodeShape.STADIUM,
            StepType.PROCESS: NodeShape.RECTANGLE,
            StepType.DECISION: NodeShape.RHOMBUS,
            StepType.END: NodeShape.STADIUM,
            StepType.PARALLEL: NodeShape.PARALLELOGRAM,
            StepType.MERGE: NodeShape.CIRCLE
        }
        
        shape = shape_mapping.get(self.step_type, NodeShape.RECTANGLE)
        builder.add_node(self.node_id, self.title, shape)
        
        # Apply styling based on automation level
        if self.automation_level == "automated":
            style = NodeStyle(fill_color="#e8f5e8", stroke_color="#28a745", stroke_width=2)
        elif self.automation_level == "semi-automated":
            style = NodeStyle(fill_color="#fff3cd", stroke_color="#ffc107", stroke_width=2)
        else:  # manual
            style = NodeStyle(fill_color="#f8f9fa", stroke_color="#6c757d", stroke_width=1)
        
        builder.style_node(self.node_id, style)
        
        # Add compliance indicators
        if self.compliance_required:
            builder.add_css_class("compliance", "stroke-dasharray: 5 5")
            builder.apply_css_class(self.node_id, "compliance")
    
    def set_risk_level(self, level: str) -> 'ProcessStep':
        """Set risk level with validation."""
        valid_levels = ["low", "medium", "high"]
        if level in valid_levels:
            self.risk_level = level
        return self
    
    def require_compliance(self, approvers: List[str] = None) -> 'ProcessStep':
        """Mark step as requiring compliance approval."""
        self.compliance_required = True
        if approvers:
            self.approvals_needed.extend(approvers)
        return self
    
    def __repr__(self) -> str:
        return f"ProcessStep(id={self.step_id}, title={self.title}, type={self.step_type.value})"


class DecisionPoint:
    """Represents a decision point with multiple outcome branches."""
    
    def __init__(self, decision_id: str, question: str, 
                 decision_criteria: str = "", timeout_minutes: int = 0):
        self.decision_id = decision_id
        self.question = question
        self.decision_criteria = decision_criteria
        self.timeout_minutes = timeout_minutes
        self.node_id = f"decision_{decision_id}"
        
        self.branches: Dict[str, ProcessStep] = {}
        self.default_branch: Optional[str] = None
        
    def add_branch(self, condition: str, target_step: ProcessStep, 
                   is_default: bool = False) -> 'DecisionPoint':
        """Add a decision branch."""
        self.branches[condition] = target_step
        if is_default:
            self.default_branch = condition
        return self
    
    def add_to_builder(self, builder: FlowchartBuilder) -> None:
        """Add decision node to builder."""
        builder.add_decision_node(self.node_id, self.question)
        
        # Add timeout styling if specified
        if self.timeout_minutes > 0:
            timeout_style = NodeStyle(fill_color="#ffebee", stroke_color="#f44336")
            builder.style_node(self.node_id, timeout_style)
    
    def connect_branches(self, builder: FlowchartBuilder) -> None:
        """Connect decision branches to their target steps."""
        for condition, target_step in self.branches.items():
            # Highlight default branch
            if condition == self.default_branch:
                builder.connect_with_label(self.node_id, target_step.node_id, 
                                         f"{condition} (default)", ArrowType.THICK_ARROW)
            else:
                builder.connect_with_label(self.node_id, target_step.node_id, condition)


class ParallelBranch:
    """Represents parallel execution branches that merge back together."""
    
    def __init__(self, branch_id: str, description: str = ""):
        self.branch_id = branch_id
        self.description = description
        self.parallel_steps: List[List[ProcessStep]] = []
        self.merge_point: Optional[ProcessStep] = None
        
    def add_parallel_path(self, steps: List[ProcessStep]) -> 'ParallelBranch':
        """Add a parallel execution path."""
        self.parallel_steps.append(steps)
        return self
    
    def set_merge_point(self, merge_step: ProcessStep) -> 'ParallelBranch':
        """Set the merge point where parallel branches converge."""
        self.merge_point = merge_step
        return self
    
    def add_to_builder(self, builder: FlowchartBuilder) -> None:
        """Add parallel branch structure to builder."""
        # Add all steps from parallel paths
        for path in self.parallel_steps:
            for step in path:
                step.add_to_builder(builder)
        
        if self.merge_point:
            self.merge_point.add_to_builder(builder)
    
    def create_parallel_flow(self, builder: FlowchartBuilder) -> None:
        """Create the parallel flow structure."""
        if not self.parallel_steps or not self.merge_point:
            return
        
        # Create subgraph for parallel execution
        parallel_subgraph = builder.add_subgraph(
            f"parallel_{self.branch_id}", 
            f"Parallel Execution: {self.description}"
        )
        
        # Connect parallel paths
        for path in self.parallel_steps:
            previous_step = None
            for step in path:
                if previous_step:
                    builder.connect(previous_step.node_id, step.node_id)
                previous_step = step
                
                # Connect last step to merge point
                if step == path[-1]:
                    builder.connect(step.node_id, self.merge_point.node_id, ArrowType.DOTTED_ARROW)


class BusinessProcessFactory:
    """Factory for creating common business processes."""
    
    @staticmethod
    def create_approval_process(process_name: str, approvers: List[str]) -> ProcessFlowBuilder:
        """Create a standard approval process."""
        builder = ProcessFlowBuilder(f"{process_name} Approval", "System")
        
        # Standard approval steps
        start_step = ProcessStep("start", "Request Submitted", StepType.START)
        review_step = ProcessStep("review", "Initial Review", StepType.PROCESS, 
                                automation_level="semi-automated", duration_minutes=30)
        
        # Create decision point
        approval_decision = DecisionPoint("approval", "Approved?", 
                                        "Review against company policies")
        
        # Outcome steps
        approved_step = ProcessStep("approved", "Request Approved", StepType.END)
        rejected_step = ProcessStep("rejected", "Request Rejected", StepType.END)
        revision_step = ProcessStep("revision", "Request Revision", StepType.PROCESS)
        
        # Build the process
        builder.add_process_step(start_step)
        builder.add_process_step(review_step)
        builder.add_decision_point(approval_decision)
        builder.add_process_step(approved_step)
        builder.add_process_step(rejected_step)
        builder.add_process_step(revision_step)
        
        # Configure decision branches
        approval_decision.add_branch("Approved", approved_step)
        approval_decision.add_branch("Rejected", rejected_step)
        approval_decision.add_branch("Needs Revision", revision_step, is_default=True)
        
        return builder
    
    @staticmethod
    def create_deployment_pipeline() -> ProcessFlowBuilder:
        """Create a software deployment pipeline process."""
        builder = ProcessFlowBuilder("CI/CD Pipeline", "DevOps Team")
        
        # Pipeline steps
        steps = [
            ProcessStep("commit", "Code Commit", StepType.START, automation_level="automated"),
            ProcessStep("build", "Build Application", StepType.PROCESS, 
                       automation_level="automated", duration_minutes=10),
            ProcessStep("test", "Run Tests", StepType.PROCESS, 
                       automation_level="automated", duration_minutes=20),
            ProcessStep("security_scan", "Security Scan", StepType.PROCESS,
                       automation_level="automated", duration_minutes=5),
            ProcessStep("deploy_staging", "Deploy to Staging", StepType.PROCESS,
                       automation_level="automated", duration_minutes=5),
            ProcessStep("integration_test", "Integration Tests", StepType.PROCESS,
                       automation_level="automated", duration_minutes=15),
            ProcessStep("deploy_prod", "Deploy to Production", StepType.END,
                       automation_level="semi-automated", duration_minutes=10)
        ]
        
        # Add compliance requirements
        steps[3].require_compliance(["Security Team"])  # Security scan
        steps[6].require_compliance(["Release Manager"])  # Production deployment
        
        # Add all steps
        for step in steps:
            builder.add_process_step(step)
        
        # Add quality gate decision
        quality_gate = DecisionPoint("quality_gate", "All Checks Pass?",
                                   "Code quality, security, and test coverage thresholds")
        
        rollback_step = ProcessStep("rollback", "Rollback Deployment", StepType.PROCESS,
                                  automation_level="automated")
        
        builder.add_decision_point(quality_gate)
        builder.add_process_step(rollback_step)
        
        quality_gate.add_branch("Pass", steps[5])  # Continue to integration tests
        quality_gate.add_branch("Fail", rollback_step)
        
        return builder


class DiagramAnalyzer:
    """Analyzer for diagram metrics and optimization suggestions."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
    
    def analyze_process_flow(self, process_builder: ProcessFlowBuilder) -> Dict[str, Any]:
        """Analyze process flow for efficiency and compliance."""
        metadata = process_builder.get_metadata()
        
        # Calculate process metrics
        total_duration = sum(step.duration_minutes for step in process_builder.process_steps)
        automated_steps = len([s for s in process_builder.process_steps if s.automation_level == "automated"])
        compliance_steps = len([s for s in process_builder.process_steps if s.compliance_required])
        
        automation_percentage = (automated_steps / len(process_builder.process_steps)) * 100
        
        # Risk assessment
        high_risk_steps = [s for s in process_builder.process_steps if s.risk_level == "high"]
        
        analysis = {
            "metadata": metadata,
            "total_duration_minutes": total_duration,
            "automation_percentage": automation_percentage,
            "compliance_steps": compliance_steps,
            "high_risk_steps": len(high_risk_steps),
            "decision_points": len(process_builder.decision_points),
            "parallel_branches": len(process_builder.parallel_branches),
            "optimization_suggestions": []
        }
        
        # Generate optimization suggestions
        if automation_percentage < 50:
            analysis["optimization_suggestions"].append(
                "Consider automating more process steps to improve efficiency"
            )
        
        if total_duration > 240:  # 4 hours
            analysis["optimization_suggestions"].append(
                "Process duration is high - consider parallel execution or step optimization"
            )
        
        if len(high_risk_steps) > 2:
            analysis["optimization_suggestions"].append(
                "Multiple high-risk steps detected - consider additional controls"
            )
        
        return analysis


async def demonstrate_advanced_oop():
    """Demonstrate advanced OOP concepts in diagram generation."""
    
    print("🚀 Advanced OOP Mermaid Generation Demo")
    print("=" * 50)
    
    # 1. Factory Pattern - Create business processes
    print("\n1. 📋 Creating Business Processes with Factory Pattern")
    
    approval_process = BusinessProcessFactory.create_approval_process(
        "Purchase Request", 
        ["Manager", "Finance", "Procurement"]
    )
    
    deployment_pipeline = BusinessProcessFactory.create_deployment_pipeline()
    
    # 2. Strategy Pattern - Different analysis strategies
    print("\n2. 📊 Analyzing Processes with Strategy Pattern")
    
    analyzer = DiagramAnalyzer()
    
    approval_analysis = analyzer.analyze_process_flow(approval_process)
    pipeline_analysis = analyzer.analyze_process_flow(deployment_pipeline)
    
    print(f"Approval Process Analysis:")
    print(f"  - Complexity Score: {approval_analysis['metadata'].complexity_score}")
    print(f"  - Automation: {approval_analysis['automation_percentage']:.1f}%")
    print(f"  - Duration: {approval_analysis['total_duration_minutes']} minutes")
    
    print(f"\nDeployment Pipeline Analysis:")
    print(f"  - Complexity Score: {pipeline_analysis['metadata'].complexity_score}")
    print(f"  - Automation: {pipeline_analysis['automation_percentage']:.1f}%")
    print(f"  - Duration: {pipeline_analysis['total_duration_minutes']} minutes")
    
    # 3. Template Method Pattern - Build and generate
    print("\n3. 🔧 Building Diagrams with Template Method Pattern")
    
    output_dir = Path("./output/advanced")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate approval process
    approval_mermaid = approval_process.build()
    approval_file = output_dir / "approval_process.mmd"
    approval_file.write_text(approval_mermaid, encoding='utf-8')
    print(f"✅ Approval process saved: {approval_file}")
    
    # Generate deployment pipeline
    pipeline_mermaid = deployment_pipeline.build()
    pipeline_file = output_dir / "deployment_pipeline.mmd"
    pipeline_file.write_text(pipeline_mermaid, encoding='utf-8')
    print(f"✅ Deployment pipeline saved: {pipeline_file}")
    
    # 4. Observer Pattern - Validation and feedback
    print("\n4. ✅ Validation with Observer Pattern")
    
    approval_valid = approval_process.validate()
    pipeline_valid = deployment_pipeline.validate()
    
    print(f"Approval Process Valid: {'✅' if approval_valid else '❌'}")
    print(f"Pipeline Valid: {'✅' if pipeline_valid else '❌'}")
    
    # 5. Polymorphism - Different builder implementations
    print("\n5. 🔄 Polymorphism with Different Builders")
    
    builders: List[IDiagramBuilder] = [approval_process, deployment_pipeline]
    
    for i, builder in enumerate(builders, 1):
        metadata = builder.get_metadata()
        print(f"Builder {i}: {metadata.title}")
        print(f"  Type: {metadata.diagram_type.value}")
        print(f"  Complexity: {metadata.complexity_score}")
        print(f"  Valid: {'✅' if builder.validate() else '❌'}")
    
    # 6. Generate images using different themes
    print("\n6. 🎨 Generating Images with Different Themes")
    
    generator = MermaidGenerator()
    themes = [MermaidTheme.DEFAULT, MermaidTheme.FOREST, MermaidTheme.DARK]
    
    try:
        for theme in themes:
            generator.set_theme(theme).set_output_format(OutputFormat.PNG)
            
            # Generate approval process with current theme
            output_file = output_dir / f"approval_{theme.value}.png"
            await generator.generate(approval_mermaid, output_file)
            print(f"✅ Generated with {theme.value} theme: {output_file}")
            
    except Exception as e:
        print(f"⚠️ Image generation failed: {e}")
        print("   (This is expected if Playwright is not properly installed)")
    
    # 7. Demonstrate composition and aggregation
    print("\n7. 🏗️ Composition and Aggregation Examples")
    
    # Create a complex process with parallel branches
    complex_process = ProcessFlowBuilder("Order Fulfillment", "Operations Team")
    
    # Main process steps
    order_received = ProcessStep("order_received", "Order Received", StepType.START)
    validate_order = ProcessStep("validate", "Validate Order", StepType.PROCESS)
    
    complex_process.add_process_step(order_received)
    complex_process.add_process_step(validate_order)
    
    # Parallel processing branch
    parallel_fulfillment = ParallelBranch("fulfillment", "Order Processing")
    
    # Inventory path
    inventory_path = [
        ProcessStep("check_inventory", "Check Inventory", StepType.PROCESS, automation_level="automated"),
        ProcessStep("reserve_items", "Reserve Items", StepType.PROCESS, automation_level="automated")
    ]
    
    # Payment path
    payment_path = [
        ProcessStep("process_payment", "Process Payment", StepType.PROCESS, automation_level="semi-automated"),
        ProcessStep("confirm_payment", "Confirm Payment", StepType.PROCESS, automation_level="automated")
    ]
    
    merge_step = ProcessStep("prepare_shipment", "Prepare Shipment", StepType.MERGE)
    
    parallel_fulfillment.add_parallel_path(inventory_path)
    parallel_fulfillment.add_parallel_path(payment_path)
    parallel_fulfillment.set_merge_point(merge_step)
    
    complex_process.add_parallel_branch(parallel_fulfillment)
    complex_process.add_process_step(merge_step)
    
    # Generate complex process
    complex_mermaid = complex_process.build()
    complex_file = output_dir / "complex_order_process.mmd"
    complex_file.write_text(complex_mermaid, encoding='utf-8')
    print(f"✅ Complex process saved: {complex_file}")
    
    # Final analysis
    complex_analysis = analyzer.analyze_process_flow(complex_process)
    print(f"\nComplex Process Analysis:")
    print(f"  - Total Steps: {len(complex_process.process_steps)}")
    print(f"  - Parallel Branches: {len(complex_process.parallel_branches)}")
    print(f"  - Automation: {complex_analysis['automation_percentage']:.1f}%")
    print(f"  - Optimization Suggestions:")
    for suggestion in complex_analysis['optimization_suggestions']:
        print(f"    • {suggestion}")
    
    print(f"\n✨ Advanced OOP demonstration completed!")
    print(f"📁 Check '{output_dir}' for generated files")
    
    return output_dir


if __name__ == "__main__":
    run_async_with_cleanup(demonstrate_advanced_oop())