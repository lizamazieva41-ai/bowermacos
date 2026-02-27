"""
Proxies Page for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class ProxiesPage:
    def __init__(self, app):
        self.app = app
        self.window_id = None

    def create(self):
        with dpg.window(
            tag="proxies_window",
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            no_title_bar=True,
            no_resize=True,
            no_move=True,
        ):
            self.window_id = "proxies_window"

            with dpg.group(horizontal=True):
                self.create_sidebar()
                self.create_main_content()

    def create_sidebar(self):
        with dpg.child_window(
            tag="proxies_sidebar",
            width=220,
            height=-1,
            border=False,
        ):
            dpg.add_text(
                "Bower",
                color=COLORS["primary"],
            )
            dpg.add_text("Antidetect Browser", color=COLORS["text_secondary"])
            dpg.add_separator()
            dpg.add_text(" ")

            dpg.add_button(
                label="Dashboard",
                width=190,
                callback=lambda: self.navigate("dashboard"),
            )
            dpg.add_button(
                label="Profiles",
                width=190,
                callback=lambda: self.navigate("profiles"),
            )
            dpg.add_button(
                label="Sessions",
                width=190,
                callback=lambda: self.navigate("sessions"),
            )
            dpg.add_button(
                label="Proxies",
                width=190,
            )
            dpg.add_button(
                label="Settings",
                width=190,
                callback=lambda: self.navigate("settings"),
            )

            dpg.add_spacer()
            dpg.add_separator()

            with dpg.group():
                dpg.add_text("API Status", color=COLORS["text_muted"])
                dpg.add_text("Connected", color=COLORS["success"])

            dpg.add_button(
                label="Logout",
                width=190,
                callback=self.logout,
            )

    def create_main_content(self):
        with dpg.child_window(
            tag="proxies_content",
            width=-1,
            height=-1,
            border=False,
        ):
            dpg.add_text("Proxies")
            dpg.add_text(
                "Manage your proxy servers",
                color=COLORS["text_secondary"],
            )
            dpg.add_separator()
            dpg.add_text(" ")

            dpg.add_button(
                label="Add New Proxy",
                tag="add_proxy_btn",
                callback=self.show_create_modal,
            )
            dpg.add_button(
                label="Refresh",
                tag="refresh_proxies_btn",
                callback=self.refresh,
            )
            dpg.add_button(
                label="Check Health",
                tag="check_health_btn",
                callback=self.check_health,
            )

            dpg.add_text(" ")
            
            with dpg.collapsing_header(label="Proxy Health Summary", default_open=True):
                with dpg.group(horizontal=True):
                    dpg.add_text("Total:", color=COLORS["text_secondary"])
                    dpg.add_text("0", tag="proxy_total_count")
                    dpg.add_text("  Healthy:", color=COLORS["text_secondary"])
                    dpg.add_text("0", tag="proxy_healthy_count", color=COLORS["success"])
                    dpg.add_text("  Unhealthy:", color=COLORS["text_secondary"])
                    dpg.add_text("0", tag="proxy_unhealthy_count", color=COLORS["danger"])

            dpg.add_text(" ")

            with dpg.child_window(tag="proxies_list", height=-60):
                dpg.add_text(
                    "No proxies configured. Add a proxy to get started.",
                    tag="no_proxies_text",
                    color=COLORS["text_muted"],
                )
                with dpg.table(
                    tag="proxies_table",
                    header_row=True,
                    resizable=True,
                    show=False,
                ):
                    dpg.add_table_column(label="ID")
                    dpg.add_table_column(label="Name")
                    dpg.add_table_column(label="Type")
                    dpg.add_table_column(label="Host:Port")
                    dpg.add_table_column(label="Status")
                    dpg.add_table_column(label="Actions")

    def show_create_modal(self):
        with dpg.modal(tag="create_proxy_modal", label="Add New Proxy"):
            dpg.add_input_text(
                label="Proxy Name",
                tag="new_proxy_name",
                width=300,
            )
            dpg.add_combo(
                label="Proxy Type",
                tag="new_proxy_type",
                items=["http", "https", "socks5"],
                default_value="http",
                width=300,
            )
            dpg.add_input_text(
                label="Host",
                tag="new_proxy_host",
                width=300,
                hint="proxy.example.com",
            )
            dpg.add_input_text(
                label="Port",
                tag="new_proxy_port",
                width=300,
                hint="8080",
            )
            dpg.add_input_text(
                label="Username (optional)",
                tag="new_proxy_username",
                width=300,
            )
            dpg.add_input_text(
                label="Password (optional)",
                tag="new_proxy_password",
                width=300,
                password=True,
            )
            dpg.add_text(" ")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Add Proxy",
                    callback=self.create_proxy,
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.close_modal("create_proxy_modal"),
                )

    def create_proxy(self):
        name = dpg.get_value("new_proxy_name")
        host = dpg.get_value("new_proxy_host")
        port = dpg.get_value("new_proxy_port")

        if not name or not host or not port:
            return

        proxy_data = {
            "name": name,
            "proxy_type": dpg.get_value("new_proxy_type"),
            "host": host,
            "port": int(port),
            "username": dpg.get_value("new_proxy_username") or None,
            "password": dpg.get_value("new_proxy_password") or None,
            "is_active": True,
        }

        try:
            self.app.api_client.create_proxy(proxy_data)
            dpg.close_modal("create_proxy_modal")
            self.refresh()
        except Exception as e:
            print(f"Error creating proxy: {e}")

    def navigate(self, page: str):
        self.app.show_page(page)
        if page in self.app.pages:
            self.app.pages[page].refresh()

    def logout(self):
        self.app.logout()

    def refresh(self):
        try:
            proxies = self.app.api_client.get_proxies()
            self.update_proxies_table(proxies)
            self.update_health_summary(proxies)
        except Exception as e:
            print(f"Error refreshing proxies: {e}")

    def check_health(self):
        """Check health of all proxies."""
        try:
            health = self.app.api_client.get_proxy_health()
            print(f"Proxy health: {health}")
            self.refresh()
        except Exception as e:
            print(f"Error checking proxy health: {e}")

    def update_health_summary(self, proxies):
        """Update proxy health summary counters."""
        total = len(proxies)
        healthy = sum(1 for p in proxies if p.get("health_status") == "healthy")
        unhealthy = sum(1 for p in proxies if p.get("health_status") == "unhealthy")
        
        if dpg.does_item_exist("proxy_total_count"):
            dpg.set_value("proxy_total_count", str(total))
        if dpg.does_item_exist("proxy_healthy_count"):
            dpg.set_value("proxy_healthy_count", str(healthy))
        if dpg.does_item_exist("proxy_unhealthy_count"):
            dpg.set_value("proxy_unhealthy_count", str(unhealthy))

    def update_proxies_table(self, proxies):
        table = "proxies_table"
        no_proxies = "no_proxies_text"

        if not proxies:
            dpg.hide_item(table)
            dpg.show_item(no_proxies)
            return

        dpg.show_item(table)
        dpg.hide_item(no_proxies)

        for child in dpg.get_item_children(table)[1]:
            dpg.delete_item(child)

        for proxy in proxies:
            with dpg.table_row(parent=table):
                dpg.add_text(str(proxy.get("id", "")))
                dpg.add_text(proxy.get("name", ""))
                dpg.add_text(proxy.get("proxy_type", "http"))
                dpg.add_text(f"{proxy.get('host', '')}:{proxy.get('port', '')}")
                dpg.add_text(
                    proxy.get("health_status", "unknown"),
                    color=COLORS["success"]
                    if proxy.get("health_status") == "healthy"
                    else COLORS["danger"]
                    if proxy.get("health_status") == "unhealthy"
                    else COLORS["text_muted"],
                )
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Test",
                        tag=f"test_proxy_{proxy.get('id')}",
                        small=True,
                        callback=lambda: self.test_proxy(proxy.get("id")),
                    )
                    dpg.add_button(
                        label="Edit",
                        tag=f"edit_proxy_{proxy.get('id')}",
                        small=True,
                        callback=lambda: self.show_edit_modal(proxy),
                    )
                    dpg.add_button(
                        label="Delete",
                        tag=f"delete_proxy_{proxy.get('id')}",
                        small=True,
                        callback=lambda: self.delete_proxy(proxy.get("id")),
                    )

    def test_proxy(self, proxy_id: int):
        try:
            result = self.app.api_client.test_proxy(proxy_id)
            print(f"Proxy test result: {result}")
            self.refresh()
        except Exception as e:
            print(f"Error testing proxy: {e}")

    def delete_proxy(self, proxy_id: int):
        try:
            self.app.api_client.delete_proxy(proxy_id)
            self.refresh()
        except Exception as e:
            print(f"Error deleting proxy: {e}")

    def show_edit_modal(self, proxy):
        with dpg.modal(tag="edit_proxy_modal", label="Edit Proxy"):
            dpg.add_input_text(
                label="Proxy Name",
                tag="edit_proxy_name",
                width=300,
                default_value=proxy.get("name", ""),
            )
            dpg.add_combo(
                label="Proxy Type",
                tag="edit_proxy_type",
                items=["http", "https", "socks5"],
                default_value=proxy.get("proxy_type", "http"),
                width=300,
            )
            dpg.add_input_text(
                label="Host",
                tag="edit_proxy_host",
                width=300,
                default_value=proxy.get("host", ""),
            )
            dpg.add_input_text(
                label="Port",
                tag="edit_proxy_port",
                width=300,
                default_value=str(proxy.get("port", "")),
            )
            dpg.add_input_text(
                label="Username (optional)",
                tag="edit_proxy_username",
                width=300,
                default_value=proxy.get("username", ""),
            )
            dpg.add_input_text(
                label="Password (optional)",
                tag="edit_proxy_password",
                width=300,
                password=True,
            )
            dpg.add_checkbox(
                label="Active",
                tag="edit_proxy_active",
                default_value=proxy.get("is_active", True),
            )
            dpg.add_text(" ")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Save Changes",
                    callback=lambda: self.update_proxy(proxy.get("id")),
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.close_modal("edit_proxy_modal"),
                )

    def update_proxy(self, proxy_id: int):
        proxy_data = {
            "name": dpg.get_value("edit_proxy_name"),
            "proxy_type": dpg.get_value("edit_proxy_type"),
            "host": dpg.get_value("edit_proxy_host"),
            "port": int(dpg.get_value("edit_proxy_port")),
            "username": dpg.get_value("edit_proxy_username") or None,
            "password": dpg.get_value("edit_proxy_password") or None,
            "is_active": dpg.get_value("edit_proxy_active"),
        }

        try:
            self.app.api_client.update_proxy(proxy_id, proxy_data)
            dpg.close_modal("edit_proxy_modal")
            self.refresh()
        except Exception as e:
            print(f"Error updating proxy: {e}")

    def show(self):
        if self.window_id:
            dpg.show_item(self.window_id)
            self.refresh()

    def hide(self):
        if self.window_id:
            dpg.hide_item(self.window_id)
