"""
Typography utilities for Bower GUI
"""

from src.gui.styles.theme import FONTS, TYPE_SCALE, COLORS


class Typography:
    """Typography utility class."""
    
    @staticmethod
    def get_font(font_type: str = "primary") -> str:
        """Get font family by type."""
        return FONTS.get(font_type, FONTS["primary"])
    
    @staticmethod
    def get_type_style(style: str) -> dict:
        """Get type scale style by name."""
        return TYPE_SCALE.get(style, TYPE_SCALE["body"])
    
    @staticmethod
    def create_text(
        text: str,
        style: str = "body",
        color: str = "text",
        **kwargs
    ) -> dict:
        """Create text style configuration."""
        type_style = Typography.get_type_style(style)
        text_color = COLORS.get(color, COLORS["text"])
        
        return {
            "text": text,
            "size": type_style["size"],
            "weight": type_style["weight"],
            "color": text_color,
            **kwargs
        }
    
    @staticmethod
    def get_display_large() -> dict:
        """Get display large text style."""
        return Typography.create_text("", "display_lg")
    
    @staticmethod
    def get_display_medium() -> dict:
        """Get display medium text style."""
        return Typography.create_text("", "display_md")
    
    @staticmethod
    def get_heading_1() -> dict:
        """Get h1 text style."""
        return Typography.create_text("", "h1")
    
    @staticmethod
    def get_heading_2() -> dict:
        """Get h2 text style."""
        return Typography.create_text("", "h2")
    
    @staticmethod
    def get_heading_3() -> dict:
        """Get h3 text style."""
        return Typography.create_text("", "h3")
    
    @staticmethod
    def get_body_large() -> dict:
        """Get body large text style."""
        return Typography.create_text("", "body_lg")
    
    @staticmethod
    def get_body() -> dict:
        """Get body text style."""
        return Typography.create_text("", "body")
    
    @staticmethod
    def get_body_small() -> dict:
        """Get body small text style."""
        return Typography.create_text("", "body_sm")
    
    @staticmethod
    def get_label() -> dict:
        """Get label text style."""
        return Typography.create_text("", "label")
    
    @staticmethod
    def get_caption() -> dict:
        """Get caption text style."""
        return Typography.create_text("", "caption", color="text_muted")


class FontLoader:
    """Font loading utilities."""
    
    _fonts_loaded = False
    
    @classmethod
    def load_fonts(cls):
        """Load fonts for the application."""
        if cls._fonts_loaded:
            return
        
        try:
            import dearpygui.dearpygui as dpg
            
            with dpg.font_registry():
                dpg.add_font(
                    FONTS["fallback"],
                    14,
                    tag="default_font",
                )
            
            cls._fonts_loaded = True
        except Exception as e:
            print(f"Font loading not available: {e}")
    
    @classmethod
    def are_fonts_loaded(cls) -> bool:
        """Check if fonts are loaded."""
        return cls._fonts_loaded


class TextStyle:
    """Text styling helpers."""
    
    @staticmethod
    def bold(text: str) -> str:
        """Make text bold."""
        return f"**{text}**"
    
    @staticmethod
    def italic(text: str) -> str:
        """Make text italic."""
        return f"*{text}*"
    
    @staticmethod
    def muted(text: str) -> str:
        """Make text muted color."""
        return text
    
    @staticmethod
    def truncate(text: str, max_length: int = 50) -> str:
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."


class TextColor:
    """Text color constants."""
    
    PRIMARY = "primary"
    SECONDARY = "text_secondary"
    MUTED = "text_muted"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"


class FontWeight:
    """Font weight constants."""
    
    NORMAL = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700
