"""
Enhanced Table Components for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional, List, Any, Dict
from src.gui.styles.theme import COLStyleORS


class Table:
    """Table style variants."""
    DEFAULT = "default"
    STRIPED = "striped"
    BORDERLESS = "borderless"


class Table:
    """Enhanced table component."""
    
    @staticmethod
    def create(
        tag: str,
        columns: List[str],
        height: int = 400,
        resizable: bool = True,
        reorderable: bool = False,
        sortable: bool = True,
        style: str = TableStyle.STRIPED,
    ) -> str:
        """Create a table with columns."""
        table_tag = dpg.add_table(
            tag=tag,
            header_row=True,
            resizable=resizable,
            reorderable=reorderable,
            height=height,
            borders_inner=True,
            borders_outer=True,
            borders_h=True,
        )
        
        for col in columns:
            dpg.add_table_column(
                label=col,
                width_fixed=False,
                width_stretch=True,
                sortable=sortable,
            )
        
        table_theme = Table._get_theme(style)
        dpg.bind_item_theme(table_tag, table_theme)
        
        return str(table_tag)
    
    @staticmethod
    def _get_theme(style: str):
        """Get theme for table style."""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvTable):
                if style == TableStyle.STRIPED:
                    dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (51, 65, 85))
                elif style == TableStyle.BORDERLESS:
                    dpg.add_theme_color(dpg.mvThemeCol_TableBorder, (0, 0, 0, 0))
        
        return theme
    
    @staticmethod
    def add_row(
        tag: str,
        data: List[str],
        colors: Optional[List[tuple]] = None,
        on_click: Optional[Callable] = None,
    ) -> str:
        """Add a row to the table."""
        row_tag = None
        
        with dpg.table_row(parent=tag):
            for i, item in enumerate(data):
                color = colors[i] if colors and i < len(colors) else None
                
                if on_click:
                    row_tag = dpg.add_text(item, color=color, wrap=0)
                else:
                    dpg.add_text(item, color=color, wrap=0)
        
        return str(row_tag) if row_tag else ""
    
    @staticmethod
    def clear_rows(tag: str):
        """Clear all rows from table."""
        if dpg.does_item_exist(tag):
            for child in dpg.get_item_children(tag)[1]:
                dpg.delete_item(child)
    
    @staticmethod
    def set_sort(tag: str, column: int, direction: str = "ascending"):
        """Set sort order for table."""
        dpg.set_table_sort(tag, column, direction)


class DataTable:
    """Data table with pagination and selection."""
    
    def __init__(self, tag: str, columns: List[str], page_size: int = 10):
        self.tag = tag
        self.columns = columns
        self.page_size = page_size
        self.current_page = 0
        self.data = []
        self.selected_rows = []
    
    def set_data(self, data: List[Dict]):
        """Set table data."""
        self.data = data
        self.current_page = 0
        self.render()
    
    def render(self):
        """Render current page."""
        Table.clear_rows(self.tag)
        
        start = self.current_page * self.page_size
        end = start + self.page_size
        page_data = self.data[start:end]
        
        for row in page_data:
            values = [str(row.get(col, "")) for col in self.columns]
            Table.add_row(self.tag, values)
    
    def next_page(self):
        """Go to next page."""
        if (self.current_page + 1) * self.page_size < len(self.data):
            self.current_page += 1
            self.render()
    
    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.render()
    
    def get_total_pages(self) -> int:
        """Get total number of pages."""
        return (len(self.data) + self.page_size - 1) // self.page_size


class SortableTable(Table):
    """Table with sorting functionality."""
    
    @staticmethod
    def create_sorted(
        tag: str,
        columns: List[dict],
        height: int = 400,
    ) -> str:
        """Create a sortable table."""
        table_tag = Table.create(tag, [c["label"] for c in columns], height)
        
        return str(table_tag)
    
    @staticmethod
    def sort_data(data: List[Dict], column: str, direction: str = "asc") -> List[Dict]:
        """Sort data by column."""
        reverse = direction == "desc"
        return sorted(data, key=lambda x: x.get(column, ""), reverse=reverse)


class ActionTable(Table):
    """Table with action buttons in rows."""
    
    @staticmethod
    def create_with_actions(
        tag: str,
        columns: List[str],
        actions: List[dict],
        height: int = 400,
    ) -> str:
        """Create table with action columns."""
        all_columns = columns + [a["label"] for a in actions]
        return Table.create(tag, all_columns, height)
    
    @staticmethod
    def add_row_with_actions(
        tag: str,
        data: List[str],
        actions: List[dict],
        row_data: Any = None,
    ):
        """Add row with action buttons."""
        with dpg.table_row(parent=tag):
            for item in data:
                dpg.add_text(str(item))
            
            with dpg.group(horizontal=True):
                for action in actions:
                    dpg.add_button(
                        label=action.get("label", ""),
                        callback=lambda: action.get("callback")(row_data),
                        small=True,
                        width=action.get("width", 60),
                    )


class ExpandableRow:
    """Table row with expandable detail view."""
    
    @staticmethod
    def create(
        tag: str,
        main_data: List[str],
        detail_content: Callable,
    ) -> str:
        """Create an expandable row."""
        with dpg.table_row(parent=tag):
            dpg.add_text(f"▶ {main_data[0]}")
            for item in main_data[1:]:
                dpg.add_text(str(item))
    
    @staticmethod
    def create_detail_row(tag: str, content: Callable):
        """Create detail row below main row."""
        with dpg.table_row(parent=tag, nested=True):
            with dpg.child_window(width=-1, height=100):
                content()


class TablePagination:
    """Pagination controls for table."""
    
    @staticmethod
    def create(
        tag: str,
        current_page: int,
        total_pages: int,
        on_prev: Callable,
        on_next: Callable,
        on_page_select: Optional[Callable] = None,
    ) -> str:
        """Create pagination controls."""
        pagination_tag = f"{tag}_pagination"
        
        with dpg.group(horizontal=True, parent=pagination_tag):
            dpg.add_button(
                label="◀ Prev",
                callback=on_prev,
                enabled=current_page > 0,
                width=80,
            )
            
            dpg.add_text(
                f"Page {current_page + 1} of {total_pages}",
                tag=f"{tag}_page_info",
            )
            
            dpg.add_button(
                label="Next ▶",
                callback=on_next,
                enabled=current_page < total_pages - 1,
                width=80,
            )
        
        return str(pagination_tag)


class ColumnFilter:
    """Column filter for table."""
    
    @staticmethod
    def create(
        tag: str,
        columns: List[str],
        on_filter: Callable,
    ) -> str:
        """Create column filter inputs."""
        filter_tag = f"{tag}_filters"
        
        with dpg.group(horizontal=True, parent=filter_tag):
            dpg.add_text("Filter:", color=COLORS.get("text_secondary"))
            
            for col in columns:
                dpg.add_input_text(
                    tag=f"{tag}_filter_{col}",
                    hint=f"Filter {col}",
                    width=100,
                    callback=on_filter,
                )
        
        return str(filter_tag)
