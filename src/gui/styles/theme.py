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
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHover, colors["text_secondary"])
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
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, (16, 16))
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, (8, 8))
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, (8, 8))
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, (8, 8))

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
