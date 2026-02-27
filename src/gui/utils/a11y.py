from typing import Optional, Literal
import dearpygui.dearpygui as dpg
from ..styles.theme import COLORS


class AriaLabel:
    """ARIA label helper for accessibility."""

    @staticmethod
    def set_label(tag: str, label: str):
        """Set aria-label on an element."""
        dpg.set_item_user_data(tag, {"aria_label": label})

    @staticmethod
    def get_label(tag: str) -> Optional[str]:
        """Get aria-label from an element."""
        user_data = dpg.get_item_user_data(tag)
        if user_data:
            return user_data.get("aria_label")
        return None

    @staticmethod
    def set_description(tag: str, description: str):
        """Set aria-description on an element."""
        dpg.set_item_user_data(tag, {"aria_description": description})


class AriaRole:
    """ARIA roles for semantic HTML equivalent."""

    ROLES = {
        "button": "button",
        "link": "link",
        "menu": "menu",
        "menuitem": "menuitem",
        "dialog": "dialog",
        "navigation": "navigation",
        "region": "region",
        "grid": "grid",
        "gridcell": "gridcell",
        "row": "row",
        "columnheader": "columnheader",
        "checkbox": "checkbox",
        "radio": "radio",
        "slider": "slider",
        "tab": "tab",
        "tablist": "tablist",
        "tabpanel": "tabpanel",
        "tooltip": "tooltip",
        "status": "status",
        "alert": "alert",
    }

    @staticmethod
    def set_role(tag: str, role: str):
        """Set aria-role on an element."""
        if role in AriaRole.ROLES:
            user_data = dpg.get_item_user_data(tag) or {}
            user_data["aria_role"] = AriaRole.ROLES[role]
            dpg.set_item_user_data(tag, user_data)

    @staticmethod
    def get_role(tag: str) -> Optional[str]:
        """Get aria-role from an element."""
        user_data = dpg.get_item_user_data(tag)
        if user_data:
            return user_data.get("aria_role")
        return None


class LiveRegion:
    """Manages live regions for screen reader announcements."""

    def __init__(self, politeness: Literal["polite", "assertive"] = "polite"):
        self.politeness = politeness
        self.tag = f"live_region_{id(self)}"
        self._create()

    def _create(self):
        with dpg.group(tag=self.tag, show=False):
            dpg.add_text("", tag=f"{self.tag}_text")

    def announce(self, message: str):
        """Announce a message to screen readers."""
        text_tag = f"{self.tag}_text"
        dpg.set_value(text_tag, message)
        dpg.show_item(self.tag)

    def clear(self):
        """Clear the announcement."""
        text_tag = f"{self.tag}_text"
        dpg.set_value(text_tag, "")
        dpg.hide_item(self.tag)


class FocusTrap:
    """Trap focus within a container for modal dialogs."""

    def __init__(self, container_tag: str):
        self.container_tag = container_tag
        self.focusable_elements: list[str] = []
        self.original_focus: Optional[str] = None
        self.active = False

    def activate(self):
        """Activate focus trap."""
        self.active = True
        self.original_focus = dpg.get_focus()
        self._find_focusable_elements()
        if self.focusable_elements:
            dpg.set_focus(self.focusable_elements[0])

    def deactivate(self):
        """Deactivate focus trap."""
        self.active = False
        if self.original_focus:
            dpg.set_focus(self.original_focus)
        self.focusable_elements.clear()

    def _find_focusable_elements(self):
        self.focusable_elements = []
        children = dpg.get_item_children(self.container_tag)
        if children:
            for child in children:
                item_type = dpg.get_item_type(child)
                if item_type in ("mvButton", "mvInputText", "mvSliderFloat", "mvSliderInt"):
                    self.focusable_elements.append(child)

    def handle_keydown(self, key: int, mods: int) -> bool:
        """Handle Tab key for focus navigation."""
        if not self.active or not self.focusable_elements:
            return False

        current = dpg.get_focus()
        if current not in self.focusable_elements:
            return False

        current_index = self.focusable_elements.index(current)

        if key == dpg.mvKey_Tab:
            if mods & dpg.mvKey_Shift:
                new_index = (current_index - 1) % len(self.focusable_elements)
            else:
                new_index = (current_index + 1) % len(self.focusable_elements)

            dpg.set_focus(self.focusable_elements[new_index])
            return True

        return False


class ScreenReaderSupport:
    """Screen reader support utilities."""

    def __init__(self):
        self.live_region = LiveRegion()

    def announce(self, message: str, priority: Literal["low", "medium", "high"] = "medium"):
        """Announce a message to screen readers."""
        if priority == "high":
            self.live_region.politeness = "assertive"
        else:
            self.live_region.politeness = "polite"
        self.live_region.announce(message)

    def announce_error(self, message: str):
        """Announce an error message."""
        self.announce(f"Error: {message}", "high")

    def announce_success(self, message: str):
        """Announce a success message."""
        self.announce(f"Success: {message}", "low")

    def announce_navigation(self, message: str):
        """Announce navigation changes."""
        self.announce(f"Navigation: {message}", "medium")


_global_screen_reader = ScreenReaderSupport()


def announce_to_screen_reader(message: str, priority: str = "medium"):
    """Global function to announce messages to screen readers."""
    _global_screen_reader.announce(message, priority)


def announce_error(message: str):
    """Global function to announce errors to screen readers."""
    _global_screen_reader.announce_error(message)


def announce_success(message: str):
    """Global function to announce success to screen readers."""
    _global_screen_reader.announce_success(message)


class ContrastChecker:
    """Check color contrast for accessibility compliance."""

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def get_luminance(r: int, g: int, b: int) -> float:
        """Calculate relative luminance."""
        def adjust(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    @staticmethod
    def get_contrast_ratio(color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors."""
        rgb1 = ContrastChecker.hex_to_rgb(color1)
        rgb2 = ContrastChecker.hex_to_rgb(color2)

        l1 = ContrastChecker.get_luminance(*rgb1)
        l2 = ContrastChecker.get_luminance(*rgb2)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def meets_wcag_aa(ratio: float, is_large_text: bool = False) -> bool:
        """Check if contrast meets WCAG AA standard."""
        return ratio >= 4.5 if not is_large_text else ratio >= 3.0

    @staticmethod
    def meets_wcag_aaa(ratio: float, is_large_text: bool = False) -> bool:
        """Check if contrast meets WCAG AAA standard."""
        return ratio >= 7.0 if not is_large_text else ratio >= 4.5
