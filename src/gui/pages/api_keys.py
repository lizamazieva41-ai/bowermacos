"""
API Keys Management Page for Bower GUI
Manages user API keys with permissions and expiry.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.gui.styles.theme import COLORS, SPACING
from src.gui.components.cards import Card
from src.gui.components.buttons import Button, ButtonVariant
from src.gui.components.inputs import Input, Select
from src.gui.components.modals import Modal
from src.gui.components.tables import DataTable
from src.gui.components.common import EmptyState


@dataclass
class ApiKey:
    """API key data structure."""
    id: int
    name: str
    key: str
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    is_active: bool


class ApiKeysPage:
    """API keys management page."""

    def __init__(self, app):
        self.app = app
        self.window_id: Optional[str] = None
        self._api_keys: List[ApiKey] = []
        self._create_modal: Optional[Modal] = None

    def create(self):
        """Create the API keys page."""
        with dpg.window(
            tag="api_keys_window",
            width=dpg.get_viewport_width(),
            height=dpg.get_viewviewport_height() if hasattr(dpg, 'get_viewviewport_height') else 800,
            no_title_bar=True,
            no_resize=True,
            no_move=True,
        ):
            self.window_id = "api_keys_window"
            self._create_content()

    def _create_content(self):
        """Create main content."""
        with dpg.group(horizontal=True):
            self._create_sidebar()
            self._create_main_panel()

    def _create_sidebar(self):
        """Create sidebar."""
        with dpg.child_window(
            tag="api_keys_sidebar",
            width=220,
            height=-1,
            border=False,
        ):
            dpg.add_text(
                "Bower",
                color=COLORS["primary"],
            )
            dpg.add_text("API Keys", color=COLORS["text_secondary"])
            dpg.add_separator()
            dpg.add_text(" ")

            nav_items = [
                ("Dashboard", "nav_apikeys_dashboard"),
                ("API Keys", "nav_apikeys_list"),
                ("Documentation", "nav_apikeys_docs"),
                ("Settings", "nav_apikeys_settings"),
            ]

            for label, tag in nav_items:
                dpg.add_button(
                    label=label,
                    tag=tag,
                    width=190,
                    callback=lambda s=tag: self._handle_navigation(s),
                )

    def _create_main_panel(self):
        """Create main panel."""
        with dpg.group():
            with dpg.child_window(
                tag="api_keys_main",
                width=-1,
                height=-1,
                border=False,
            ):
                self._create_header()
                dpg.add_text(" ")
                self._create_api_keys_table()
                dpg.add_text(" ")
                self._create_key_details()

    def _create_header(self):
        """Create page header."""
        with dpg.group(horizontal=True):
            dpg.add_text(
                "API Keys",
                color=COLORS["text_primary"],
            )

            dpg.add_spacer()

            dpg.add_button(
                label="+ Create New Key",
                tag="btn_create_api_key",
                callback=self._show_create_modal,
            )

        dpg.add_text(
            "Manage API keys for programmatic access to Bower",
            color=COLORS["text_secondary"],
        )

    def _create_api_keys_table(self):
        """Create API keys table."""
        with dpg.group():
            with dpg.table(
                tag="api_keys_table",
                resizable=True,
                sortable=True,
                headers=["Name", "Key", "Permissions", "Created", "Expires", "Status", "Actions"],
                widths=[150, 200, 150, 120, 120, 80, 100],
            ):
                if not self._api_keys:
                    with dpg.table_row():
                        dpg.add_text(
                            "No API keys yet. Create one to get started.",
                            color=COLORS["text_secondary"],
                        )
                else:
                    for key in self._api_keys:
                        self._render_api_key_row(key)

    def _render_api_key_row(self, key: ApiKey):
        """Render a single API key row."""
        with dpg.table_row():
            dpg.add_text(key.name, color=COLORS["text_primary"])

            masked_key = f"{key.key[:8]}...{key.key[-4:]}" if len(key.key) > 12 else "***"
            dpg.add_text(masked_key, color=COLORS["text_secondary"])

            permissions = ", ".join(key.permissions) if key.permissions else "None"
            dpg.add_text(permissions, color=COLORS["text_secondary"])

            dpg.add_text(
                key.created_at.strftime("%Y-%m-%d"),
                color=COLORS["text_secondary"],
            )

            expires = key.expires_at.strftime("%Y-%m-%d") if key.expires_at else "Never"
            dpg.add_text(expires, color=COLORS["text_secondary"])

            status_color = COLORS["success"] if key.is_active else COLORS["danger"]
            dpg.add_text(
                "Active" if key.is_active else "Inactive",
                color=status_color,
            )

            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Copy",
                    small=True,
                    callback=lambda: self._copy_key(key.key),
                )
                dpg.add_button(
                    label="Revoke",
                    small=True,
                    callback=lambda: self._revoke_key(key.id),
                )

    def _create_key_details(self):
        """Create key details section."""
        with dpg.collapsing_header(
            tag="key_details_header",
            label="Quick Start Guide",
            default_open=True,
        ):
            dpg.add_text(
                "1. Create an API key using the button above",
                color=COLORS["text_secondary"],
            )
            dpg.add_text(
                "2. Copy the key and store it securely",
                color=COLORS["text_secondary"],
            )
            dpg.add_text(
                "3. Use the key in your requests:",
                color=COLORS["text_secondary"],
            )
            dpg.add_text(
                "   Authorization: Bearer YOUR_API_KEY",
                color=COLORS["accent"],
            )
            dpg.add_text(" ")
            dpg.add_text(
                "Example:",
                color=COLORS["text_primary"],
            )
            dpg.add_text(
                'curl -H "Authorization: Bearer sk_live_xxx" https://api.bower/v1/profiles',
                color=COLORS["text_secondary"],
            )

    def _show_create_modal(self):
        """Show create API key modal."""
        if not self._create_modal:
            self._create_modal = Modal(
                title="Create API Key",
                width=500,
                height=400,
            )

        self._create_modal.open()

    def _copy_key(self, key: str):
        """Copy API key to clipboard."""
        import pyperclip
        try:
            pyperclip.copy(key)
            self._show_notification("API key copied to clipboard")
        except Exception:
            dpg.set_clipboard_text(key)
            self._show_notification("API key copied to clipboard")

    def _revoke_key(self, key_id: int):
        """Revoke an API key."""
        pass

    def _handle_navigation(self, tag: str):
        """Handle navigation."""
        pass

    def _show_notification(self, message: str):
        """Show notification."""
        pass

    def load_api_keys(self, keys: List[ApiKey]):
        """Load API keys into the page."""
        self._api_keys = keys

    def destroy(self):
        """Clean up resources."""
        if self.window_id:
            dpg.delete_item(self.window_id)


class ApiKeyForm:
    """Form for creating/editing API keys."""

    def __init__(self):
        self.name_input: Optional[Input] = None
        self.permissions_select: Optional[Select] = None
        self.expiry_select: Optional[Select] = None

    def render(self) -> dict:
        """Render the form and return data."""
        result = {}

        with dpg.group():
            dpg.add_text("Key Name", color=COLORS["text_primary"])
            dpg.add_input_text(
                tag="api_key_name",
                hint="Enter a name for this key",
                width=400,
            )

            dpg.add_text(" ")

            dpg.add_text("Permissions", color=COLORS["text_primary"])
            dpg.add_combo(
                tag="api_key_permissions",
                items=["Read Only", "Read/Write", "Admin"],
                default_value="Read Only",
                width=400,
            )

            dpg.add_text(" ")

            dpg.add_text("Expires", color=COLORS["text_primary"])
            dpg.add_combo(
                tag="api_key_expiry",
                items=["Never", "30 days", "90 days", "1 year"],
                default_value="Never",
                width=400,
            )

            dpg.add_text(" ")

            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Create Key",
                    tag="btn_confirm_create_key",
                    callback=self._on_submit,
                )
                dpg.add_button(
                    label="Cancel",
                    tag="btn_cancel_create_key",
                )

        return result

    def _on_submit(self):
        """Handle form submission."""
        name = dpg.get_value("api_key_name")
        permissions = dpg.get_value("api_key_permissions")
        expiry = dpg.get_value("api_key_expiry")

        expiry_days = {
            "Never": None,
            "30 days": 30,
            "90 days": 90,
            "1 year": 365,
        }.get(expiry)

        return {
            "name": name,
            "permissions": permissions,
            "expires_in_days": expiry_days,
        }


def create_api_keys_page(app) -> ApiKeysPage:
    """Factory function to create API keys page."""
    return ApiKeysPage(app)
