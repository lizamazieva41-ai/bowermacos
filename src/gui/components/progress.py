from typing import Optional
import dearpygui.dearpygui as dpg
from ..styles.theme import COLORS, SPACING, BORDER_RADIUS


class ProgressBar:
    """Progress bar component for displaying task completion."""

    def __init__(
        self,
        value: float = 0.0,
        label: Optional[str] = None,
        show_percentage: bool = True,
        height: int = 8,
        color: Optional[str] = None,
        bg_color: Optional[str] = None,
        animated: bool = True,
    ):
        self.value = max(0.0, min(1.0, value))
        self.label = label
        self.show_percentage = show_percentage
        self.height = height
        self.color = color or "accent"
        self.bg_color = bg_color or "surface"
        self.animated = animated
        self.tag = f"progress_{id(self)}"

    def render(self) -> str:
        with dpg.group(horizontal=True):
            if self.label:
                dpg.add_text(self.label, color=COLORS["text_primary"])

            with dpg.group():
                dpg.add_progress_bar(
                    default_value=self.value,
                    width=-1,
                    height=self.height,
                    overlay=f"{int(self.value * 100)}%" if self.show_percentage else "",
                    border=False,
                )

        return self.tag

    def update(self, value: float):
        self.value = max(0.0, min(1.0, value))
        dpg.set_value(self.tag, self.value)
        if self.show_percentage:
            dpg.set_item_label(self.tag, f"{int(self.value * 100)}%")


class CircularProgress:
    """Circular progress indicator."""

    def __init__(
        self,
        value: float = 0.0,
        size: int = 60,
        thickness: float = 4.0,
        show_percentage: bool = True,
        color: Optional[str] = "accent",
    ):
        self.value = max(0.0, min(1.0, value))
        self.size = size
        self.thickness = thickness
        self.show_percentage = show_percentage
        self.color = color
        self.tag = f"circular_progress_{id(self)}"

    def render(self) -> str:
        dpg.addLoadingIndicator(
            circle_count=32,
            speed=1.0,
            radius=self.size // 2,
            thickness=self.thickness,
            color=COLORS[self.color],
        )
        return self.tag

    def update(self, value: float):
        self.value = max(0.0, min(1.0, value))


class ProgressGroup:
    """Group of progress bars for multi-step operations."""

    def __init__(self, steps: list[str]):
        self.steps = steps
        self.current_step = 0
        self.tags: list[str] = []

    def render(self) -> list[str]:
        self.tags = []
        for i, step in enumerate(self.steps):
            tag = f"progress_step_{i}"
            self.tags.append(tag)

            with dpg.group(horizontal=True):
                dpg.add_text(step, color=COLORS["text_secondary"])

                with dpg.group(width=200):
                    dpg.add_progress_bar(
                        default_value=1.0 if i < self.current_step else 0.0,
                        height=4,
                        border=False,
                        tag=tag,
                    )

        return self.tags

    def set_step(self, step: int):
        if 0 <= step < len(self.steps):
            self.current_step = step
            for i, tag in enumerate(self.tags):
                if i < step:
                    dpg.set_value(tag, 1.0)
                elif i == step:
                    dpg.set_value(tag, 0.5)
                else:
                    dpg.set_value(tag, 0.0)


def create_progress_bar(
    value: float = 0.0,
    label: Optional[str] = None,
    show_percentage: bool = True,
    height: int = 8,
) -> ProgressBar:
    """Factory function to create a progress bar."""
    return ProgressBar(value, label, show_percentage, height)


def create_circular_progress(
    value: float = 0.0,
    size: int = 60,
    show_percentage: bool = True,
) -> CircularProgress:
    """Factory function to create a circular progress indicator."""
    return CircularProgress(value, size, show_percentage=show_percentage)
