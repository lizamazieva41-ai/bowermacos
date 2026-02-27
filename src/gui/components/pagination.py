"""
Pagination component for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional, List, Any
from src.gui.styles.theme import COLORS


class Pagination:
    """Pagination component."""
    
    def __init__(
        self,
        current_page: int = 1,
        total_pages: int = 1,
        page_size: int = 10,
        total_items: int = 0,
    ):
        self.current_page = current_page
        self.total_pages = total_pages
        self.page_size = page_size
        self.total_items = total_items
        
        self.on_page_change: Optional[Callable] = None
        self.on_page_size_change: Optional[Callable] = None
    
    def set_callbacks(
        self,
        on_page_change: Callable = None,
        on_page_size_change: Callable = None,
    ):
        """Set pagination callbacks."""
        self.on_page_change = on_page_change
        self.on_page_size_change = on_page_size_change
    
    def create(self, tag: str = "pagination") -> str:
        """Create pagination UI."""
        container_tag = f"{tag}_container"
        
        with dpg.group(horizontal=True, tag=container_tag):
            dpg.add_text(
                f"Page {self.current_page} of {self.total_pages}",
                color=COLORS["text_secondary"],
            )
            
            dpg.add_text("", width=20)
            
            dpg.add_button(
                label="« First",
                tag=f"{tag}_first",
                width=60,
                callback=lambda: self._go_to_page(1),
                enabled=self.current_page > 1,
            )
            
            dpg.add_button(
                label="‹ Prev",
                tag=f"{tag}_prev",
                width=60,
                callback=lambda: self._go_to_page(self.current_page - 1),
                enabled=self.current_page > 1,
            )
            
            dpg.add_button(
                label="Next ›",
                tag=f"{tag}_next",
                width=60,
                callback=lambda: self._go_to_page(self.current_page + 1),
                enabled=self.current_page < self.total_pages,
            )
            
            dpg.add_button(
                label="Last »",
                tag=f"{tag}_last",
                width=60,
                callback=lambda: self._go_to_page(self.total_pages),
                enabled=self.current_page < self.total_pages,
            )
            
            if self.total_items > 0:
                dpg.add_text("", width=20)
                dpg.add_text(
                    f"({self.total_items} items)",
                    color=COLORS["text_muted"],
                )
        
        return container_tag
    
    def _go_to_page(self, page: int):
        """Go to specific page."""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            if self.on_page_change:
                self.on_page_change(page)
    
    def next_page(self):
        """Go to next page."""
        self._go_to_page(self.current_page + 1)
    
    def prev_page(self):
        """Go to previous page."""
        self._go_to_page(self.current_page - 1)
    
    def first_page(self):
        """Go to first page."""
        self._go_to_page(1)
    
    def last_page(self):
        """Go to last page."""
        self._go_to_page(self.total_pages)
    
    @staticmethod
    def create_simple(
        current_page: int,
        total_pages: int,
        on_page_change: Callable = None,
        tag: str = "pagination",
    ) -> str:
        """Create simple pagination."""
        pag = Pagination(current_page, total_pages)
        pag.on_page_change = on_page_change
        return pag.create(tag)


class PageSizeSelector:
    """Page size selector component."""
    
    def __init__(self, page_size: int = 10):
        self.page_size = page_size
        self.options = [10, 25, 50, 100]
        self.on_change: Optional[Callable] = None
    
    def set_callback(self, on_change: Callable):
        """Set change callback."""
        self.on_change = on_change
    
    def create(self, tag: str = "page_size") -> str:
        """Create page size selector."""
        container_tag = f"{tag}_container"
        
        with dpg.group(horizontal=True, tag=container_tag):
            dpg.add_text("Show:", color=COLORS["text_secondary"])
            dpg.add_text("", width=10)
            
            dpg.add_combo(
                tag=tag,
                items=[str(n) for n in self.options],
                default_value=str(self.page_size),
                width=80,
                callback=self._on_change,
            )
        
        return container_tag
    
    def _on_change(self):
        """Handle page size change."""
        value = dpg.get_value(tag)
        if value and self.on_change:
            self.on_change(int(value))


class PaginationInfo:
    """Pagination info display."""
    
    @staticmethod
    def create(
        current_page: int,
        page_size: int,
        total_items: int,
        tag: str = "pagination_info",
    ) -> str:
        """Create pagination info."""
        start = (current_page - 1) * page_size + 1
        end = min(current_page * page_size, total_items)
        
        info_text = f"Showing {start}-{end} of {total_items}"
        
        return dpg.add_text(
            info_text,
            tag=tag,
            color=COLORS["text_muted"],
        )


class TablePagination:
    """Combined table pagination with info."""
    
    def __init__(
        self,
        current_page: int = 1,
        total_pages: int = 1,
        page_size: int = 10,
        total_items: int = 0,
    ):
        self.pagination = Pagination(current_page, total_pages, page_size, total_items)
        self.page_size_selector = PageSizeSelector(page_size)
    
    def set_callbacks(
        self,
        on_page_change: Callable = None,
        on_page_size_change: Callable = None,
    ):
        """Set callbacks."""
        self.pagination.on_page_change = on_page_change
        self.page_size_selector.on_change = on_page_size_change
    
    def create(self, tag: str = "table_pagination") -> str:
        """Create table pagination."""
        container_tag = f"{tag}_container"
        
        with dpg.group(horizontal=True, tag=container_tag):
            self.page_size_selector.create(f"{tag}_page_size")
            dpg.add_text("", width=20)
            self.pagination.create(tag)
        
        return container_tag
