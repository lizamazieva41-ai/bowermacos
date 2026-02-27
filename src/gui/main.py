"""
Bower Antidetect Browser - Python GUI Application
Main entry point using DearPyGui
"""

import asyncio
import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo

from src.gui.app import BowerApp
from src.gui.styles.theme import setup_theme


def main():
    dpg.create_context()
    dpg.create_viewport(
        title="Bower Antidetect Browser",
        width=1400,
        height=900,
        min_width=1024,
        min_height=700,
        resizable=True,
    )

    setup_theme()

    app = BowerApp()
    app.setup()

    dpg.set_viewport_vsync(True)

    dpg.setup_dearpygui()
    dpg.show_viewport()

    app.run()

    dpg.destroy_context()


if __name__ == "__main__":
    main()
