from typing import Optional, Callable
import dearpygui.dearpygui as dpg
from ..styles.theme import COLORS, SPACING


class Tooltip:
    """Tooltip component for displaying contextual information."""

    def __init__(
        self,
        text: str,
        position: str = "bottom",
        delay: float = 0.5,
        max_width: int = 250,
    ):
        self.text = text
        self.position = position
        self.delay = delay
        self.max_width = max_width
        self.tag = f"tooltip_{id(self)}"
        self.parent_tag: Optional[str] = None

    def attach_to(self, parent_tag: str) -> str:
        self.parent_tag = parent_tag
        return self.tag

    def render(self):
        if not self.parent_tag:
            return

        with dpg.tooltip(parent=self.parent_tag):
            dpg.add_text(
                self.text,
                wrap=self.max_width,
                color=COLORS["text_secondary"],
            )


class TooltipManager:
    """Manager for handling multiple tooltips."""

    def __init__(self):
        self.tooltips: dict[str, Tooltip] = {}

    def create(
        self,
        tag: str,
        text: str,
        position: str = "bottom",
        delay: float = 0.5,
        max_width: int = 250,
    ) -> Tooltip:
        tooltip = Tooltip(text, position, delay, max_width)
        self.tooltips[tag] = tooltip
        return tooltip

    def show(self, tag: str):
        if tag in self.tooltips:
            dpg.show_item(f"{tag}_tooltip")

    def hide(self, tag: str):
        if tag in self.tooltips:
            dpg.hide_item(f"{tag}_tooltip")

    def remove(self, tag: str):
        if tag in self.tooltips:
            del self.tooltips[tag]


_global_tooltip_manager = TooltipManager()


def show_tooltip(
    parent_tag: str,
    text: str,
    position: str = "bottom",
    delay: float = 0.5,
    max_width: int = 250,
) -> str:
    """Helper function to show a tooltip attached to an item."""
    tooltip_tag = f"tooltip_{parent_tag}"

    with dpg.tooltip(parent=parent_tag, tag=tooltip_tag):
        dpg.add_text(
            text,
            wrap=max_width,
            color=COLORS["text_secondary"],
        )

    return tooltip_tag


def create_tooltip(
    text: str,
    position: str = "bottom",
    delay: float = 0.5,
    max_width: int = 250,
) -> Tooltip:
    """Factory function to create a tooltip."""
    return Tooltip(text, position, delay, max_width)
