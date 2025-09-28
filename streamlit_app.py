#!/usr/bin/env python3
"""
PyMermaidView Streamlit Web Interface
A user-friendly web interface for creating and previewing Mermaid diagrams.
"""
import streamlit as st
import asyncio
import tempfile
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json

# Import our core modules
from src.mermaid_generator import MermaidGenerator, MermaidConfig, OutputFormat, MermaidTheme
from src.flowchart_builder import FlowchartBuilder, NodeShape, ArrowType
from src.mermaid_utils import FlowchartValidator, TemplateManager

# Page configuration
st.set_page_config(
    page_title="PyMermaidView - Interactive Diagram Creator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #cce7ff;
        border: 1px solid #99d6ff;
        color: #0066cc;
        padding: 1rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitMermaidApp:
    """Main Streamlit application class for PyMermaidView"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.validator = FlowchartValidator()
        
        # Initialize session state
        if 'generated_images' not in st.session_state:
            st.session_state.generated_images = {}
        if 'current_mermaid_code' not in st.session_state:
            st.session_state.current_mermaid_code = self._get_default_example()
        if 'validation_result' not in st.session_state:
            st.session_state.validation_result = None
    
    def _get_default_example(self) -> str:
        """Get a default Mermaid example"""
        return """flowchart TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug it]
    D --> B
    C --> E[End]
    
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class A,E startEnd
    class C,D process
    class B decision"""
    
    def run(self):
        """Main application runner"""
        self._render_header()
        
        # Main layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self._render_input_section()
        
        with col2:
            self._render_preview_section()
        
        # Footer
        self._render_footer()
    
    def _render_header(self):
        """Render the application header"""
        st.markdown('<h1 class="main-header">🎨 PyMermaidView</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Interactive Mermaid Diagram Creator & Previewer</p>', unsafe_allow_html=True)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Templates Available", len(self.template_manager.list_templates()))
        with col2:
            st.metric("Themes Supported", "4")
        with col3:
            st.metric("Output Formats", "4")
        with col4:
            st.metric("Generated Today", len(st.session_state.generated_images))
    
    def _render_input_section(self):
        """Render the input section with editor and controls"""
        st.subheader("📝 Diagram Editor")
        
        # Template selection
        with st.expander("🗂️ Choose from Templates"):
            template_names = self.template_manager.list_templates()
            
            if template_names:
                selected_template = st.selectbox(
                    "Select a template:",
                    options=["None"] + template_names,
                    help="Choose a pre-built template to start with"
                )
                
                if selected_template != "None":
                    if st.button("Load Template"):
                        builder = self.template_manager.create_flowchart_from_template(selected_template)
                        if builder:
                            st.session_state.current_mermaid_code = builder.to_mermaid()
                            st.success(f"Loaded template: {selected_template}")
                            st.rerun()
        
        # Quick builder
        with st.expander("🚀 Quick Builder"):
            st.write("Build a simple flowchart quickly:")
            
            steps = st.text_area(
                "Enter steps (one per line):",
                height=100,
                placeholder="Step 1: Start Process\nStep 2: Validate Data\nStep 3: Generate Report"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                include_decisions = st.checkbox("Include decision points")
            with col2:
                flowchart_direction = st.selectbox("Direction:", ["TD", "LR", "TB", "RL"])
            
            if st.button("Generate Quick Flowchart") and steps.strip():
                quick_code = self._generate_quick_flowchart(steps, include_decisions, flowchart_direction)
                st.session_state.current_mermaid_code = quick_code
                st.success("Quick flowchart generated!")
                st.rerun()
        
        # Main editor
        st.write("**Mermaid Code Editor:**")
        
        # Use text area for Mermaid code input
        mermaid_code = st.text_area(
            "Enter your Mermaid diagram syntax:",
            value=st.session_state.current_mermaid_code,
            height=400,
            help="Enter Mermaid flowchart syntax. Use 'flowchart TD' to start."
        )
        
        # Update session state
        if mermaid_code != st.session_state.current_mermaid_code:
            st.session_state.current_mermaid_code = mermaid_code
        
        # Validation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Validate Syntax", type="secondary"):
                self._validate_syntax(mermaid_code)
        
        with col2:
            if st.button("🎨 Generate Preview", type="primary"):
                self._generate_preview(mermaid_code)
        
        # Display validation results
        if st.session_state.validation_result:
            self._display_validation_results()
    
    def _render_preview_section(self):
        """Render the preview section with image and controls"""
        st.subheader("👁️ Live Preview")
        
        # Configuration panel
        with st.expander("⚙️ Generation Settings", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                theme = st.selectbox(
                    "Theme:",
                    options=[t.value for t in MermaidTheme],
                    index=0,
                    help="Choose the visual theme for your diagram"
                )
                
                output_format = st.selectbox(
                    "Output Format:",
                    options=[f.value for f in OutputFormat],
                    index=0,
                    help="Choose the output image format"
                )
            
            with col2:
                width = st.slider("Width (px):", 400, 2400, 1200, 100)
                height = st.slider("Height (px):", 300, 1800, 800, 100)
                scale = st.slider("Scale Factor:", 0.5, 3.0, 2.0, 0.1)
        
        # Generation controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🖼️ Generate Image", type="primary"):
                self._generate_image(theme, output_format, width, height, scale)
        
        with col2:
            if st.button("📱 Generate All Themes"):
                self._generate_all_themes(output_format, width, height, scale)
        
        # Display preview
        self._display_preview()
        
        # Download section
        self._render_download_section()
    
    def _validate_syntax(self, mermaid_code: str):
        """Validate the Mermaid syntax"""
        try:
            # Validate using our validator
            is_valid = self.validator.validate_mermaid_syntax(mermaid_code)
            
            st.session_state.validation_result = {
                'is_valid': is_valid,
                'errors': self.validator.errors.copy(),
                'warnings': self.validator.warnings.copy()
            }
            
        except Exception as e:
            st.session_state.validation_result = {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': []
            }
    
    def _display_validation_results(self):
        """Display validation results"""
        result = st.session_state.validation_result
        
        if result['is_valid']:
            st.markdown('<div class="success-box">✅ Syntax is valid!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">❌ Syntax errors found</div>', unsafe_allow_html=True)
        
        if result.get('errors'):
            st.error("**Errors:**")
            for error in result['errors']:
                st.write(f"• {error}")
        
        if result.get('warnings'):
            st.warning("**Warnings:**")
            for warning in result['warnings']:
                st.write(f"• {warning}")
    
    def _generate_preview(self, mermaid_code: str):
        """Generate a quick preview of the diagram"""
        try:
            # First validate
            self._validate_syntax(mermaid_code)
            
            if st.session_state.validation_result.get('is_valid', False):
                # Generate with default settings
                self._generate_image(
                    MermaidTheme.DEFAULT.value,
                    OutputFormat.PNG.value,
                    800, 600, 1.0
                )
            else:
                st.error("Please fix syntax errors before generating preview")
                
        except Exception as e:
            st.error(f"Preview generation failed: {str(e)}")
    
    def _generate_image(self, theme: str, output_format: str, width: int, height: int, scale: float):
        """Generate a single image with specified parameters"""
        try:
            with st.spinner("🎨 Generating image..."):
                # Create temporary file for mermaid code
                temp_mermaid = tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False)
                temp_mermaid.write(st.session_state.current_mermaid_code)
                temp_mermaid.close()
                
                # Create output file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_output = tempfile.NamedTemporaryFile(
                    suffix=f'.{output_format.lower()}', 
                    delete=False
                )
                temp_output.close()
                
                # Configure generator
                config = MermaidConfig()
                config.theme = MermaidTheme(theme)
                config.output_format = OutputFormat(output_format.lower())
                config.width = width
                config.height = height
                config.scale = scale
                config.background_color = "white" if theme != "dark" else "#1e1e1e"
                
                # Generate image
                generator = MermaidGenerator()
                generator.config = config
                
                # Run async generation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    generator.generate_from_file(Path(temp_mermaid.name), Path(temp_output.name))
                )
                loop.close()
                
                if result and Path(temp_output.name).exists():
                    # Store in session state
                    image_key = f"{theme}_{output_format}_{timestamp}"
                    st.session_state.generated_images[image_key] = {
                        'path': temp_output.name,
                        'theme': theme,
                        'format': output_format,
                        'size': f"{width}x{height}",
                        'scale': scale,
                        'timestamp': timestamp
                    }
                    
                    st.success(f"✅ Image generated successfully! ({Path(temp_output.name).stat().st_size / 1024:.1f} KB)")
                else:
                    st.error("❌ Failed to generate image")
                
                # Clean up mermaid temp file
                Path(temp_mermaid.name).unlink()
                
        except Exception as e:
            st.error(f"Generation failed: {str(e)}")
    
    def _generate_all_themes(self, output_format: str, width: int, height: int, scale: float):
        """Generate images for all available themes"""
        themes = [theme.value for theme in MermaidTheme]
        
        with st.spinner(f"🎨 Generating {len(themes)} themed versions..."):
            for theme in themes:
                self._generate_image(theme, output_format, width, height, scale)
        
        st.success(f"✅ Generated {len(themes)} themed versions!")
    
    def _display_preview(self):
        """Display the generated image previews"""
        if st.session_state.generated_images:
            st.write("**Generated Images:**")
            
            # Sort by timestamp (most recent first)
            sorted_images = sorted(
                st.session_state.generated_images.items(),
                key=lambda x: x[1]['timestamp'],
                reverse=True
            )
            
            for image_key, image_info in sorted_images:
                with st.expander(f"🖼️ {image_info['theme'].title()} Theme - {image_info['size']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Display image
                        try:
                            st.image(
                                image_info['path'],
                                caption=f"Theme: {image_info['theme']} | Format: {image_info['format']} | Scale: {image_info['scale']}x",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Could not display image: {str(e)}")
                    
                    with col2:
                        st.write("**Image Details:**")
                        st.write(f"• **Theme:** {image_info['theme']}")
                        st.write(f"• **Format:** {image_info['format']}")
                        st.write(f"• **Size:** {image_info['size']}")
                        st.write(f"• **Scale:** {image_info['scale']}x")
                        st.write(f"• **Generated:** {image_info['timestamp']}")
                        
                        # File size
                        try:
                            file_size = Path(image_info['path']).stat().st_size / 1024
                            st.write(f"• **File Size:** {file_size:.1f} KB")
                        except:
                            pass
        else:
            st.info("👈 Generate an image to see the preview here!")
    
    def _render_download_section(self):
        """Render the download section"""
        if st.session_state.generated_images:
            st.subheader("⬇️ Download Images")
            
            for image_key, image_info in st.session_state.generated_images.items():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"📄 {image_info['theme'].title()} - {image_info['size']} ({image_info['format']})")
                
                with col2:
                    try:
                        with open(image_info['path'], 'rb') as file:
                            st.download_button(
                                label="📥 Download",
                                data=file.read(),
                                file_name=f"mermaid_{image_info['theme']}_{image_info['timestamp']}.{image_info['format'].lower()}",
                                mime=f"image/{image_info['format'].lower()}",
                                key=f"download_{image_key}"
                            )
                    except Exception as e:
                        st.error(f"Download failed: {str(e)}")
    
    def _generate_quick_flowchart(self, steps: str, include_decisions: bool, direction: str) -> str:
        """Generate a quick flowchart from step descriptions"""
        lines = [line.strip() for line in steps.split('\n') if line.strip()]
        
        if not lines:
            return self._get_default_example()
        
        # Build flowchart
        mermaid_lines = [f"flowchart {direction}"]
        
        # Add start node
        mermaid_lines.append("    start([Start])")
        
        # Process each step
        prev_node = "start"
        for i, step in enumerate(lines):
            node_id = f"step_{i+1}"
            
            # Clean step text
            step_text = step.replace('"', "'")
            if step_text.lower().startswith(f"step {i+1}:"):
                step_text = step_text[len(f"step {i+1}:"):].strip()
            
            # Determine node shape based on content
            if include_decisions and ('?' in step_text or 'decision' in step_text.lower()):
                mermaid_lines.append(f"    {node_id}{{{step_text}}}")
                mermaid_lines.append(f"    {prev_node} --> {node_id}")
                
                # Add decision branches
                yes_node = f"yes_{i+1}"
                no_node = f"no_{i+1}"
                mermaid_lines.append(f"    {yes_node}[Continue]")
                mermaid_lines.append(f"    {no_node}[Review]")
                mermaid_lines.append(f"    {node_id} -->|Yes| {yes_node}")
                mermaid_lines.append(f"    {node_id} -->|No| {no_node}")
                mermaid_lines.append(f"    {no_node} --> {node_id}")
                prev_node = yes_node
            else:
                mermaid_lines.append(f"    {node_id}[{step_text}]")
                mermaid_lines.append(f"    {prev_node} --> {node_id}")
                prev_node = node_id
        
        # Add end node
        mermaid_lines.append("    end_node([End])")
        mermaid_lines.append(f"    {prev_node} --> end_node")
        
        # Add styling
        mermaid_lines.extend([
            "",
            "    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
            "    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px",
            "    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px",
            "",
            "    class start,end_node startEnd"
        ])
        
        return '\n'.join(mermaid_lines)
    
    def _render_footer(self):
        """Render the application footer"""
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔧 Features:**")
            st.write("• Real-time syntax validation")
            st.write("• Multiple theme generation")
            st.write("• High-resolution output")
            st.write("• Template library")
        
        with col2:
            st.markdown("**📚 Resources:**")
            st.markdown("[Mermaid Documentation](https://mermaid.js.org/)")
            st.markdown("[Flowchart Syntax](https://mermaid.js.org/syntax/flowchart.html)")
            st.markdown("[GitHub Repository](https://github.com)")
        
        with col3:
            st.markdown("**ℹ️ About:**")
            st.write("PyMermaidView v2.0")
            st.write("Built with Streamlit")
            st.write("Powered by Playwright")
            st.write("Made with ❤️")


def main():
    """Main application entry point"""
    app = StreamlitMermaidApp()
    app.run()


if __name__ == "__main__":
    main()