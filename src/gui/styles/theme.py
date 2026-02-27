"""
Theme configuration for Bower GUI
"""

import dearpygui.dearpygui as dpg


def setup_theme():
    colors = {
        "primary": (59, 130, 246),
        "primary_hover": (37, 99, 235),
        "primary_active": (29, 78, 216),
        "secondary": (100, 116, 139),
        "success": (34, 197, 94),
        "danger": (239, 68, 68),
        "warning": (234, 179, 8),
        "background": (15, 23, 42),
        "surface": (30, 41, 59),
        "surface_hover": (51, 65, 85),
        "border": (71, 85, 105),
        "text": (226, 232, 240),
        "text_secondary": (148, 163, 184),
        "text_muted": (100, 116, 139),
    }

    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, colors["background"])
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, colors["surface"])
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, colors["surface"])
            dpg.add_theme_color(dpg.mvThemeCol_Border, colors["border"])
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, colors["border"])
            dpg.add_theme_color(dpg.mvThemeCol_Text, colors["text"])
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, colors["text_muted"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, colors["surface"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, colors["surface_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, colors["surface"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, colors["surface"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, colors["secondary"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, colors["text_secondary"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, colors["text"])
            dpg.add_theme_color(dpg.mvThemeCol_Header, colors["surface_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, colors["surface_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_Button, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, colors["primary_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, colors["primary_active"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, colors["surface_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, colors["border"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, colors["primary_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_Separator, colors["border"])
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_Tab, colors["surface"])
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, colors["surface_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, colors["surface_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, colors["surface"])
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, colors["surface_hover"])
            dpg.add_theme_color(dpg.mvThemeCol_NavWindowingHighlight, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, colors["primary"])
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogramHovered, colors["primary_hover"])

    dpg.bind_theme(theme)

    return colors


COLORS = {
    "primary": (59, 130, 246),
    "primary_hover": (37, 99, 235),
    "success": (34, 197, 94),
    "danger": (239, 68, 68),
    "warning": (234, 179, 8),
    "background": (15, 23, 42),
    "surface": (30, 41, 59),
    "surface_hover": (51, 65, 85),
    "border": (71, 85, 105),
    "text": (226, 232, 240),
    "text_secondary": (148, 163, 184),
    "text_muted": (100, 116, 139),
}


FONTS = {
    "primary": "Inter",
    "monospace": "JetBrains Mono",
    "fallback": "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
    "mono_fallback": "Consolas, Monaco, 'Courier New', monospace",
}


TYPE_SCALE = {
    "display_lg": {"size": 48, "weight": 700, "line_height": 1.2},
    "display_md": {"size": 36, "weight": 600, "line_height": 1.25},
    "h1": {"size": 28, "weight": 700, "line_height": 1.3},
    "h2": {"size": 24, "weight": 600, "line_height": 1.35},
    "h3": {"size": 20, "weight": 600, "line_height": 1.4},
    "h4": {"size": 18, "weight": 600, "line_height": 1.4},
    "body_lg": {"size": 16, "weight": 400, "line_height": 1.5},
    "body": {"size": 14, "weight": 400, "line_height": 1.5},
    "body_sm": {"size": 13, "weight": 400, "line_height": 1.5},
    "label": {"size": 12, "weight": 500, "line_height": 1.4},
    "caption": {"size": 11, "weight": 400, "line_height": 1.4},
}


SPACING = {
    "0": 0,
    "1": 4,
    "2": 8,
    "3": 12,
    "4": 16,
    "5": 20,
    "6": 24,
    "8": 32,
    "10": 40,
    "12": 48,
    "16": 64,
}


BORDER_RADIUS = {
    "none": 0,
    "sm": 4,
    "default": 6,
    "md": 8,
    "lg": 12,
    "xl": 16,
    "full": 9999,
}


SHADOWS = {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "default": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
}


TRANSITIONS = {
    "fast": "150ms ease",
    "default": "200ms ease",
    "slow": "300ms ease",
}


Z_INDEX = {
    "dropdown": 1000,
    "sticky": 1020,
    "fixed": 1030,
    "modal_backdrop": 1040,
    "modal": 1050,
    "popover": 1060,
    "tooltip": 1070,
}
