"""
Mermaid Image Generator - Core Module
This module provides the main functionality for generating Mermaid diagrams as images.
"""

import os
import sys
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser
import requests
from PIL import Image
import base64

# Import Windows utilities for better cleanup
from .windows_utils import suppress_windows_asyncio_warnings


class OutputFormat(Enum):
    """Supported output formats for Mermaid diagrams."""
    PNG = "png"
    SVG = "svg" 
    PDF = "pdf"
    JPEG = "jpeg"


class MermaidTheme(Enum):
    """Supported Mermaid themes."""
    DEFAULT = "default"
    FOREST = "forest"
    DARK = "dark"
    NEUTRAL = "neutral"
    BASE = "base"


@dataclass
class MermaidConfig:
    """Configuration class for Mermaid diagram generation."""
    theme: MermaidTheme = MermaidTheme.DEFAULT
    output_format: OutputFormat = OutputFormat.PNG
    width: int = 800
    height: int = 600
    background_color: str = "white"
    scale: float = 1.0
    font_size: int = 16
    animation: bool = False
    custom_css: Optional[str] = None
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    
    def __post_init__(self):
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)


class MermaidError(Exception):
    """Base exception class for Mermaid-related errors."""
    pass


class MermaidSyntaxError(MermaidError):
    """Exception raised for invalid Mermaid syntax."""
    pass


class MermaidGenerationError(MermaidError):
    """Exception raised during diagram generation."""
    pass


class IMermaidRenderer(ABC):
    """Abstract interface for Mermaid diagram renderers."""
    
    @abstractmethod
    async def render(self, mermaid_code: str, config: MermaidConfig) -> bytes:
        """Render Mermaid code to image bytes."""
        pass
    
    @abstractmethod
    async def validate_syntax(self, mermaid_code: str) -> bool:
        """Validate Mermaid syntax."""
        pass


class PlaywrightMermaidRenderer(IMermaidRenderer):
    """Mermaid renderer using Playwright for browser automation."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    def __del__(self):
        """Destructor to ensure cleanup on garbage collection."""
        if self.browser or self.page or self.playwright:
            import warnings
            warnings.warn(
                "PlaywrightMermaidRenderer was not properly closed. "
                "Use 'async with renderer:' context manager for proper cleanup.",
                ResourceWarning
            )
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup()
    
    async def _initialize_browser(self):
        """Initialize Playwright browser."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            
            # Set viewport size
            await self.page.set_viewport_size({"width": 1200, "height": 800})
            
        except Exception as e:
            await self._cleanup()  # Cleanup on error
            raise MermaidGenerationError(f"Failed to initialize browser: {e}")
    
    async def _cleanup(self):
        """Clean up browser resources properly."""
        cleanup_errors = []
        
        try:
            if self.page:
                await self.page.close()
                self.page = None
        except Exception as e:
            cleanup_errors.append(f"Page cleanup: {e}")
        
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            cleanup_errors.append(f"Browser cleanup: {e}")
        
        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            cleanup_errors.append(f"Playwright cleanup: {e}")
        
        # On Windows, give the system a moment to clean up processes
        if sys.platform == "win32":
            try:
                await asyncio.sleep(0.1)
            except Exception:
                pass
    
    async def validate_syntax(self, mermaid_code: str) -> bool:
        """Validate Mermaid syntax by attempting to render."""
        try:
            await self._render_mermaid_html(mermaid_code, MermaidConfig())
            return True
        except Exception:
            return False
    
    async def render(self, mermaid_code: str, config: MermaidConfig) -> bytes:
        """Render Mermaid diagram to image bytes."""
        if not self.page:
            raise MermaidGenerationError("Browser not initialized")
        
        try:
            # Generate HTML with Mermaid diagram
            html_content = await self._render_mermaid_html(mermaid_code, config)
            
            # Load HTML in browser
            await self.page.set_content(html_content)
            
            # Wait for Mermaid to render
            await self.page.wait_for_selector('#mermaid-diagram', timeout=10000)
            
            # Take screenshot based on format
            if config.output_format == OutputFormat.SVG:
                return await self._get_svg_content()
            else:
                return await self._take_screenshot(config)
                
        except Exception as e:
            raise MermaidGenerationError(f"Failed to render diagram: {e}")
    
    async def _render_mermaid_html(self, mermaid_code: str, config: MermaidConfig) -> str:
        """Generate HTML content with Mermaid diagram."""
        mermaid_cdn = "https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Mermaid Diagram</title>
            <script src="{mermaid_cdn}"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: {config.background_color};
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-size: {config.font_size}px;
                }}
                .mermaid {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                {config.custom_css or ""}
            </style>
        </head>
        <body>
            <div class="mermaid" id="mermaid-diagram">
                {mermaid_code}
            </div>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: '{config.theme.value}',
                    flowchart: {{
                        useMaxWidth: false,
                        htmlLabels: true
                    }},
                    themeVariables: {{
                        fontSize: '{config.font_size}px'
                    }}
                }});
            </script>
        </body>
        </html>
        """
        return html_template
    
    async def _get_svg_content(self) -> bytes:
        """Extract SVG content from the rendered diagram."""
        svg_element = await self.page.query_selector('svg')
        if not svg_element:
            raise MermaidGenerationError("No SVG element found in rendered diagram")
        
        svg_content = await svg_element.inner_html()
        svg_full = f'<svg xmlns="http://www.w3.org/2000/svg" {await svg_element.get_attribute("viewBox") or ""}>{svg_content}</svg>'
        return svg_full.encode('utf-8')
    
    async def _take_screenshot(self, config: MermaidConfig) -> bytes:
        """Take screenshot of the rendered diagram."""
        element = await self.page.query_selector('#mermaid-diagram')
        if not element:
            raise MermaidGenerationError("Mermaid diagram element not found")
        
        screenshot_options = {
            'type': config.output_format.value,
            'quality': 95 if config.output_format == OutputFormat.JPEG else None
        }
        
        return await element.screenshot(**screenshot_options)


class OnlineMermaidRenderer(IMermaidRenderer):
    """Mermaid renderer using online Mermaid Live Editor API."""
    
    BASE_URL = "https://mermaid.live"
    
    async def validate_syntax(self, mermaid_code: str) -> bool:
        """Validate syntax using online service."""
        # For now, assume valid - could be enhanced with actual API call
        return len(mermaid_code.strip()) > 0
    
    async def render(self, mermaid_code: str, config: MermaidConfig) -> bytes:
        """Render using Mermaid Live Editor."""
        try:
            # Encode mermaid code for URL
            encoded_code = base64.b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
            
            # Construct URL (this is a simplified version)
            url = f"{self.BASE_URL}/img/{encoded_code}"
            
            # Make request
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            raise MermaidGenerationError(f"Failed to render using online service: {e}")


class MermaidGenerator:
    """Main class for generating Mermaid diagrams."""
    
    def __init__(self, renderer: Optional[IMermaidRenderer] = None):
        self.renderer = renderer or PlaywrightMermaidRenderer()
        self.config = MermaidConfig()
        self._generation_history: List[Dict[str, Any]] = []
    
    def set_config(self, **kwargs) -> 'MermaidGenerator':
        """Set configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: {key}")
        return self
    
    def set_theme(self, theme: MermaidTheme) -> 'MermaidGenerator':
        """Set the theme for diagram generation."""
        self.config.theme = theme
        return self
    
    def set_output_format(self, format: OutputFormat) -> 'MermaidGenerator':
        """Set the output format."""
        self.config.output_format = format
        return self
    
    def set_dimensions(self, width: int, height: int) -> 'MermaidGenerator':
        """Set output dimensions."""
        self.config.width = width
        self.config.height = height
        return self
    
    async def generate_from_file(self, mermaid_file: Path, output_file: Optional[Path] = None) -> Path:
        """Generate diagram from Mermaid file."""
        if not mermaid_file.exists():
            raise FileNotFoundError(f"Mermaid file not found: {mermaid_file}")
        
        mermaid_code = mermaid_file.read_text(encoding='utf-8')
        
        if not output_file:
            output_file = self.config.output_dir / f"{mermaid_file.stem}.{self.config.output_format.value}"
        
        return await self.generate(mermaid_code, output_file)
    
    async def generate(self, mermaid_code: str, output_file: Optional[Path] = None) -> Path:
        """Generate Mermaid diagram from code string."""
        # Validate input
        if not mermaid_code.strip():
            raise MermaidSyntaxError("Empty Mermaid code provided")
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.config.output_dir / f"mermaid_{timestamp}.{self.config.output_format.value}"
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Track generation start
        generation_start = datetime.now()
        
        try:
            # Use context manager for proper resource cleanup
            if isinstance(self.renderer, PlaywrightMermaidRenderer):
                async with self.renderer as renderer:
                    # Validate syntax
                    if not await renderer.validate_syntax(mermaid_code):
                        raise MermaidSyntaxError("Invalid Mermaid syntax")
                    
                    # Generate diagram
                    image_data = await renderer.render(mermaid_code, self.config)
            else:
                # Validate syntax
                if not await self.renderer.validate_syntax(mermaid_code):
                    raise MermaidSyntaxError("Invalid Mermaid syntax")
                
                # Generate diagram
                image_data = await self.renderer.render(mermaid_code, self.config)
            
            # Save to file
            output_file.write_bytes(image_data)
            
            # Record generation history
            generation_time = (datetime.now() - generation_start).total_seconds()
            self._generation_history.append({
                'timestamp': generation_start,
                'output_file': str(output_file),
                'format': self.config.output_format.value,
                'theme': self.config.theme.value,
                'generation_time': generation_time,
                'success': True
            })
            
            return output_file
            
        except Exception as e:
            # Record failed generation
            generation_time = (datetime.now() - generation_start).total_seconds()
            self._generation_history.append({
                'timestamp': generation_start,
                'output_file': str(output_file) if output_file else None,
                'format': self.config.output_format.value,
                'theme': self.config.theme.value,
                'generation_time': generation_time,
                'success': False,
                'error': str(e)
            })
            raise
    
    def get_generation_history(self) -> List[Dict[str, Any]]:
        """Get the history of diagram generations."""
        return self._generation_history.copy()
    
    def clear_history(self) -> None:
        """Clear the generation history."""
        self._generation_history.clear()