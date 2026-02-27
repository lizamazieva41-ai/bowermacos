from typing import Callable, Optional
import dearpygui.dearpygui as dpg


class KeyboardManager:
    """Manages keyboard shortcuts and navigation."""

    def __init__(self):
        self.shortcuts: dict[str, Callable] = {}
        self.registered_callbacks: list = []

    def register(
        self,
        key: str,
        modifiers: Optional[list[str]] = None,
        callback: Callable = None,
        description: str = "",
    ) -> str:
        """Register a keyboard shortcut."""
        shortcut_id = f"kb_{key}_{id(callback)}"
        modifiers = modifiers or []

        combo = "+".join(modifiers + [key]) if modifiers else key

        self.shortcuts[combo] = {
            "callback": callback,
            "description": description,
            "id": shortcut_id,
        }

        return shortcut_id

    def unregister(self, shortcut_id: str):
        """Unregister a keyboard shortcut."""
        for combo, data in self.shortcuts.items():
            if data["id"] == shortcut_id:
                del self.shortcuts[combo]
                break

    def get_shortcuts(self) -> dict:
        """Get all registered shortcuts."""
        return self.shortcuts.copy()

    def handle_keypress(self, key: int, mods: int) -> bool:
        """Handle a keypress and call registered callbacks."""
        key_name = self._get_key_name(key)
        mod_names = self._get_modifier_names(mods)
        combo = "+".join(mod_names + [key_name]) if mod_names else key_name

        if combo in self.shortcuts and self.shortcuts[combo]["callback"]:
            self.shortcuts[combo]["callback"]()
            return True
        return False

    def _get_key_name(self, key: int) -> str:
        key_map = {
            dpg.mvKey_Return: "Enter",
            dpg.mvKey_Tab: "Tab",
            dpg.mvKey_Space: "Space",
            dpg.mvKey_Backspace: "Backspace",
            dpg.mvKey_Delete: "Delete",
            dpg.mvKey_Up: "Up",
            dpg.mvKey_Down: "Down",
            dpg.mvKey_Left: "Left",
            dpg.mvKey_Right: "Right",
            dpg.mvKey_Home: "Home",
            dpg.mvKey_End: "End",
            dpg.mvKey_PageUp: "PageUp",
            dpg.mvKey_PageDown: "PageDown",
            dpg.mvKey_Escape: "Escape",
            dpg.mvKey_F1: "F1",
            dpg.mvKey_F2: "F2",
            dpg.mvKey_F3: "F3",
            dpg.mvKey_F4: "F4",
            dpg.mvKey_F5: "F5",
            dpg.mvKey_F6: "F6",
            dpg.mvKey_F7: "F7",
            dpg.mvKey_F8: "F8",
            dpg.mvKey_F9: "F9",
            dpg.mvKey_F10: "F10",
            dpg.mvKey_F11: "F11",
            dpg.mvKey_F12: "F12",
        }

        if 65 <= key <= 90:
            return chr(key)
        if 48 <= key <= 57:
            return chr(key)
        if 96 <= key <= 105:
            return f"Num{chr(key - 96 + 48)}"

        return key_map.get(key, f"Key_{key}")

    def _get_modifier_names(self, mods: int) -> list[str]:
        names = []
        if mods & dpg.mvKey_Shift:
            names.append("Shift")
        if mods & dpg.mvKey_Ctrl:
            names.append("Ctrl")
        if mods & dpg.mvKey_Alt:
            names.append("Alt")
        return names


_global_keyboard_manager = KeyboardManager()


def register_shortcut(
    key: str,
    modifiers: Optional[list[str]] = None,
    callback: Callable = None,
    description: str = "",
) -> str:
    """Register a global keyboard shortcut."""
    return _global_keyboard_manager.register(key, modifiers, callback, description)


def unregister_shortcut(shortcut_id: str):
    """Unregister a global keyboard shortcut."""
    _global_keyboard_manager.unregister(shortcut_id)


def get_all_shortcuts() -> dict:
    """Get all registered shortcuts."""
    return _global_keyboard_manager.get_shortcuts()


class FocusManager:
    """Manages focus navigation between elements."""

    def __init__(self):
        self.focusable_items: list[str] = []
        self.current_index: int = 0

    def register(self, tag: str):
        """Register an item as focusable."""
        if tag not in self.focusable_items:
            self.focusable_items.append(tag)

    def unregister(self, tag: str):
        """Unregister a focusable item."""
        if tag in self.focusable_items:
            self.focusable_items.remove(tag)

    def focus_next(self):
        """Move focus to the next item."""
        if not self.focusable_items:
            return
        self.current_index = (self.current_index + 1) % len(self.focusable_items)
        dpg.set_focus(self.focusable_items[self.current_index])

    def focus_previous(self):
        """Move focus to the previous item."""
        if not self.focusable_items:
            return
        self.current_index = (self.current_index - 1) % len(self.focusable_items)
        dpg.set_focus(self.focusable_items[self.current_index])

    def focus_item(self, tag: str):
        """Focus a specific item."""
        if tag in self.focusable_items:
            self.current_index = self.focusable_items.index(tag)
            dpg.set_focus(tag)

    def clear(self):
        """Clear all focusable items."""
        self.focusable_items.clear()
        self.current_index = 0


_global_focus_manager = FocusManager()


def register_focusable(tag: str):
    """Register an item as focusable."""
    _global_focus_manager.register(tag)


def focus_next():
    """Move focus to the next item."""
    _global_focus_manager.focus_next()


def focus_previous():
    """Move focus to the previous item."""
    _global_focus_manager.focus_previous()
