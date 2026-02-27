"""
Enhanced Input Components for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import Optional, List, Any, Callable
from src.gui.styles.theme import COLORS


class InputStyle:
    """Input style variants."""
    DEFAULT = "default"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Input:
    """Enhanced input component."""
    
    @staticmethod
    def create_text(
        label: str,
        tag: str,
        default_value: str = "",
        width: int = 300,
        hint: str = "",
        password: bool = False,
        readonly: bool = False,
        disabled: bool = False,
        style: str = InputStyle.DEFAULT,
        on_change: Optional[Callable] = None,
    ) -> str:
        """Create a text input field."""
        input_tag = dpg.add_input_text(
            label=label,
            tag=tag,
            default_value=default_value,
            width=width,
            hint=hint,
            password=password,
            readonly=readonly,
            enabled=not disabled,
            callback=on_change,
        )
        
        Input._apply_style(input_tag, style)
        
        return str(input_tag)
    
    @staticmethod
    def create_int(
        label: str,
        tag: str,
        default_value: int = 0,
        width: int = 150,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        step: int = 1,
        style: str = InputStyle.DEFAULT,
    ) -> str:
        """Create an integer input field."""
        input_tag = dpg.add_input_int(
            label=label,
            tag=tag,
            default_value=default_value,
            width=width,
            min_value=min_value,
            max_value=max_value,
            step=step,
        )
        
        Input._apply_style(input_tag, style)
        
        return str(input_tag)
    
    @staticmethod
    def create_float(
        label: str,
        tag: str,
        default_value: float = 0.0,
        width: int = 150,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        step: float = 0.1,
        precision: int = 2,
        style: str = InputStyle.DEFAULT,
    ) -> str:
        """Create a float input field."""
        input_tag = dpg.add_input_float(
            label=label,
            tag=tag,
            default_value=default_value,
            width=width,
            min_value=min_value,
            max_value=max_value,
            step=step,
            format=f".{precision}f",
        )
        
        Input._apply_style(input_tag, style)
        
        return str(input_tag)
    
    @staticmethod
    def _apply_style(tag: str, style: str):
        """Apply style to input."""
        if style == InputStyle.DEFAULT:
            return
        
        colors_map = {
            InputStyle.SUCCESS: COLORS.get("success", (34, 197, 94)),
            InputStyle.WARNING: COLORS.get("warning", (234, 179, 8)),
            InputStyle.ERROR: COLORS.get("danger", (239, 68, 68)),
        }
        
        color = colors_map.get(style, COLORS.get("text_primary"))
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, color)
        
        dpg.bind_item_theme(tag, theme)


class Select:
    """Enhanced select/combo component."""
    
    @staticmethod
    def create(
        label: str,
        tag: str,
        items: List[str],
        default_value: str = "",
        width: int = 200,
        disabled: bool = False,
        style: str = InputStyle.DEFAULT,
    ) -> str:
        """Create a combo/select field."""
        combo_tag = dpg.add_combo(
            label=label,
            tag=tag,
            items=items,
            default_value=default_value or (items[0] if items else ""),
            width=width,
            enabled=not disabled,
        )
        
        Input._apply_style(combo_tag, style)
        
        return str(combo_tag)
    
    @staticmethod
    def create_browser_engine(tag: str, default: str = "chromium") -> str:
        """Create browser engine selector."""
        return Select.create(
            "Browser Engine", tag,
            ["chromium", "firefox", "webkit"],
            default, width=200
        )
    
    @staticmethod
    def create_resolution(tag: str, default: str = "1920x1080") -> str:
        """Create resolution selector."""
        return Select.create(
            "Resolution", tag,
            ["1920x1080", "1366x768", "1280x720", "2560x1440", "3840x2160"],
            default, width=200
        )
    
    @staticmethod
    def create_proxy_type(tag: str, default: str = "http") -> str:
        """Create proxy type selector."""
        return Select.create(
            "Proxy Type", tag,
            ["http", "https", "socks5"],
            default, width=200
        )


class Toggle:
    """Toggle/Checkbox component."""
    
    @staticmethod
    def create_checkbox(
        label: str,
        tag: str,
        default_value: bool = False,
        disabled: bool = False,
    ) -> str:
        """Create a checkbox."""
        checkbox_tag = dpg.add_checkbox(
            label=label,
            tag=tag,
            default_value=default_value,
            enabled=not disabled,
        )
        
        return str(checkbox_tag)
    
    @staticmethod
    def create_switch(
        label: str,
        tag: str,
        default_value: bool = False,
        on_change: Optional[Callable] = None,
    ) -> str:
        """Create a switch-like toggle."""
        checkbox_tag = dpg.add_checkbox(
            label=label,
            tag=tag,
            default_value=default_value,
            callback=on_change,
        )
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvCheckbox):
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, COLORS.get("primary"))
        
        dpg.bind_item_theme(checkbox_tag, theme)
        
        return str(checkbox_tag)


class TextArea:
    """Multi-line text input."""
    
    @staticmethod
    def create(
        label: str,
        tag: str,
        default_value: str = "",
        width: int = 400,
        height: int = 100,
        hint: str = "",
        readonly: bool = False,
    ) -> str:
        """Create a multi-line text input."""
        input_tag = dpg.add_input_text(
            label=label,
            tag=tag,
            default_value=default_value,
            width=width,
            height=height,
            hint=hint,
            readonly=readonly,
            multiline=True,
        )
        
        return str(input_tag)


class SearchInput:
    """Search input with icon."""
    
    @staticmethod
    def create(
        tag: str,
        placeholder: str = "Search...",
        width: int = 300,
        on_search: Optional[Callable] = None,
    ) -> str:
        """Create a search input field."""
        with dpg.group(horizontal=True):
            dpg.add_text("🔍")
            input_tag = dpg.add_input_text(
                tag=tag,
                default_value="",
                width=width - 30,
                hint=placeholder,
                callback=on_search,
            )
        
        return str(input_tag)


class FormField:
    """Form field with label and input."""
    
    @staticmethod
    def create_text(
        label: str,
        tag: str,
        default_value: str = "",
        width: int = 300,
        hint: str = "",
        required: bool = False,
        help_text: str = "",
    ) -> str:
        """Create a form field with text input."""
        label_text = f"{label} *" if required else label
        
        if help_text:
            with dpg.group():
                dpg.add_text(label_text, color=COLORS.get("text_secondary"))
                dpg.add_text(help_text, color=COLORS.get("text_muted"))
        else:
            dpg.add_text(label_text, color=COLORS.get("text_secondary"))
        
        input_tag = Input.create_text(
            label="", tag=tag, default_value=default_value,
            width=width, hint=hint
        )
        
        return str(input_tag)
    
    @staticmethod
    def create_select(
        label: str,
        tag: str,
        items: List[str],
        default_value: str = "",
        width: int = 200,
        required: bool = False,
    ) -> str:
        """Create a form field with select."""
        label_text = f"{label} *" if required else label
        dpg.add_text(label_text, color=COLORS.get("text_secondary"))
        
        return Select.create(label, tag, items, default_value, width)


class Form:
    """Form container with validation."""
    
    def __init__(self, tag: str):
        self.tag = tag
        self.fields = {}
        self.validators = {}
    
    def add_field(self, name: str, tag: str, validator: Optional[Callable] = None):
        """Add a field to the form."""
        self.fields[name] = tag
        if validator:
            self.validators[name] = validator
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate all form fields."""
        errors = []
        
        for name, tag in self.fields.items():
            if dpg.does_item_exist(tag):
                value = dpg.get_value(tag)
                
                if validator := self.validators.get(name):
                    if not validator(value):
                        errors.append(f"{name} is invalid")
                
                if value is None or value == "":
                    errors.append(f"{name} is required")
        
        return len(errors) == 0, errors
    
    def get_data(self) -> dict:
        """Get form data as dictionary."""
        data = {}
        for name, tag in self.fields.items():
            if dpg.does_item_exist(tag):
                data[name] = dpg.get_value(tag)
        return data
    
    def clear(self):
        """Clear all form fields."""
        for name, tag in self.fields.items():
            if dpg.does_item_exist(tag):
                dpg.set_value(tag, "")
    
    def reset(self, defaults: dict):
        """Reset form to default values."""
        for name, tag in self.fields.items():
            if dpg.does_item_exist(tag) and name in defaults:
                dpg.set_value(tag, defaults[name])
