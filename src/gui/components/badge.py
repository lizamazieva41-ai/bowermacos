from typing import Optional, Literal
import dearpygui.dearpygui as dpg
from ..styles.theme import COLORS, SPACING, BORDER_RADIUS


BadgeVariant = Literal["default", "primary", "success", "warning", "danger", "info"]
BadgeSize = Literal["small", "medium", "large"]


class Badge:
    """Badge component for displaying labels, counts, and status indicators."""

    def __init__(
        self,
        text: str,
        variant: BadgeVariant = "default",
        size: BadgeSize = "medium",
        pill: bool = True,
        dot: bool = False,
    ):
        self.text = text
        self.variant = variant
        self.size = size
        self.pill = pill
        self.dot = dot
        self.tag = f"badge_{id(self)}"

    def _get_colors(self) -> tuple:
        variant_colors = {
            "default": (COLORS["text_secondary"], COLORS["surface_elevated"]),
            "primary": ("#FFFFFF", COLORS["accent"]),
            "success": ("#FFFFFF", "#22C55E"),
            "warning": ("#FFFFFF", "#F59E0B"),
            "danger": ("#FFFFFF", "#EF4444"),
            "info": ("#FFFFFF", "#3B82F6"),
        }
        return variant_colors.get(self.variant, variant_colors["default"])

    def _get_size(self) -> tuple:
        size_map = {
            "small": (SPACING[1] - 2, SPACING[0] - 2, 8),
            "medium": (SPACING[2], SPACING[1], 10),
            "large": (SPACING[3], SPACING[2], 12),
        }
        return size_map.get(self.size, size_map["medium"])

    def render(self) -> str:
        text_color, bg_color = self._get_colors()
        padding_x, padding_y, font_size = self._get_size()

        with dpg.group(horizontal=True, horizontal_spacing=4):
            if self.dot:
                dpg.add_text(
                    "●",
                    color=bg_color,
                )

            dpg.add_text(
                self.text,
                color=text_color,
            )

        return self.tag


class StatusBadge(Badge):
    """Badge specifically for status indicators."""

    def __init__(self, status: Literal["active", "inactive", "pending", "error", "running"]):
        status_config = {
            "active": ("Active", "success", True),
            "inactive": ("Inactive", "default", True),
            "pending": ("Pending", "warning", True),
            "error": ("Error", "danger", True),
            "running": ("Running", "info", False),
        }

        text, variant, dot = status_config.get(status, ("Unknown", "default", False))
        super().__init__(text, variant=variant, size="small", dot=dot)


class CountBadge(Badge):
    """Badge for displaying counts/notifications."""

    def __init__(self, count: int, max_count: int = 99, show_plus: bool = True):
        display_text = str(count) if count <= max_count else f"{max_count}+"
        if show_plus and count > max_count:
            display_text = f"{max_count}+"

        super().__init__(
            display_text,
            variant="danger" if count > 0 else "default",
            size="small",
            pill=True,
        )
        self.count = count


class Tag:
    """Tag component for categorization."""

    def __init__(
        self,
        label: str,
        removable: bool = False,
        on_remove: Optional[callable] = None,
    ):
        self.label = label
        self.removable = removable
        self.on_remove = on_remove
        self.tag = f"tag_{id(self)}"

    def render(self) -> str:
        with dpg.group(horizontal=True, horizontal_spacing=4):
            dpg.add_text(
                self.label,
                color=COLORS["text_primary"],
            )

            if self.removable:
                dpg.add_button(
                    label="×",
                    small=True,
                    callback=self.on_remove,
                )

        return self.tag


def create_badge(
    text: str,
    variant: BadgeVariant = "default",
    size: BadgeSize = "medium",
    pill: bool = True,
) -> Badge:
    """Factory function to create a badge."""
    return Badge(text, variant, size, pill)


def create_status_badge(status: str) -> StatusBadge:
    """Factory function to create a status badge."""
    return StatusBadge(status)


def create_count_badge(count: int, max_count: int = 99) -> CountBadge:
    """Factory function to create a count badge."""
    return CountBadge(count, max_count)


def create_tag(label: str, removable: bool = False) -> Tag:
    """Factory function to create a tag."""
    return Tag(label, removable)
