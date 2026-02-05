import platform
import re
import threading
from typing import Callable, Dict, Optional, Set

from pynput import keyboard


class HotkeyManager:

    KEY_MAP = {
        'ctrl': 'ctrl',
        'control': 'ctrl',
        'alt': 'alt',
        'shift': 'shift',
        'cmd': 'cmd',
        'command': 'cmd',
        'win': 'cmd',
        'super': 'cmd',
        'tab': 'tab',
        'space': 'space',
        'enter': 'enter',
        'return': 'enter',
        'esc': 'esc',
        'escape': 'esc',
        'backspace': 'backspace',
        'delete': 'delete',
        'home': 'home',
        'end': 'end',
        'pageup': 'page_up',
        'pagedown': 'page_down',
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right',
        'insert': 'insert',
        'printscreen': 'print_screen',
        'scrolllock': 'scroll_lock',
        'pause': 'pause',
        'numlock': 'num_lock',
        'capslock': 'caps_lock',
    }

    for i in range(1, 25):
        KEY_MAP[f'f{i}'] = f'f{i}'

    def __init__(self):
        self.listener: Optional[keyboard.GlobalHotKeys] = None
        self.hotkeys: Dict[str, Callable] = {}
        self.original_hotkeys: Dict[str, str] = {}
        self._lock = threading.Lock()

    def _normalize_key(self, key: str) -> str:
        key_lower = key.lower().strip()

        if key_lower in self.KEY_MAP:
            return f"<{self.KEY_MAP[key_lower]}>"

        if len(key_lower) == 1:
            return key_lower

        if key_lower.startswith('<') and key_lower.endswith('>'):
            return key_lower

        return f"<{key_lower}>"

    def parse_hotkey(self, hotkey_string: str) -> str:
        system = platform.system()

        parts = re.split(r'\s*\+\s*', hotkey_string)
        normalized = [self._normalize_key(part) for part in parts]

        return '+'.join(normalized)

    def register(self, hotkey: str, callback: Callable) -> bool:
        with self._lock:
            pynput_hotkey = self.parse_hotkey(hotkey)

            self.hotkeys[pynput_hotkey] = callback
            self.original_hotkeys[pynput_hotkey] = hotkey

            self._restart_listener()
            return True

    def unregister(self, hotkey: str) -> bool:
        with self._lock:
            pynput_hotkey = self.parse_hotkey(hotkey)

            if pynput_hotkey in self.hotkeys:
                del self.hotkeys[pynput_hotkey]
                if pynput_hotkey in self.original_hotkeys:
                    del self.original_hotkeys[pynput_hotkey]

                self._restart_listener()
                return True

            return False

    def unregister_all(self) -> None:
        with self._lock:
            self.hotkeys.clear()
            self.original_hotkeys.clear()
            self._stop_listener()

    def _restart_listener(self) -> None:
        self._stop_listener()

        if not self.hotkeys:
            return

        self.listener = keyboard.GlobalHotKeys(self.hotkeys)
        self.listener.start()

    def _stop_listener(self) -> None:
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def start(self) -> None:
        with self._lock:
            if self.hotkeys:
                self._restart_listener()

    def stop(self) -> None:
        with self._lock:
            self._stop_listener()

    def get_registered_hotkeys(self) -> Set[str]:
        return set(self.original_hotkeys.values())

    def is_registered(self, hotkey: str) -> bool:
        pynput_hotkey = self.parse_hotkey(hotkey)
        return pynput_hotkey in self.hotkeys


class HotkeyCapture:

    def __init__(self, on_capture: Callable[[str], None]):
        self.on_capture = on_capture
        self.listener: Optional[keyboard.Listener] = None
        self.pressed_keys: Set[str] = set()
        self.modifier_keys = {'ctrl', 'alt', 'shift', 'cmd'}

    def _get_key_name(self, key) -> Optional[str]:
        try:
            if hasattr(key, 'char') and key.char:
                return key.char.upper()

            if hasattr(key, 'name'):
                name = key.name.lower()

                if name.startswith('ctrl'):
                    return 'Ctrl'
                elif name.startswith('alt'):
                    return 'Alt'
                elif name.startswith('shift'):
                    return 'Shift'
                elif name.startswith('cmd') or name == 'super':
                    if platform.system() == 'Darwin':
                        return 'Cmd'
                    return 'Win'
                elif name.startswith('f') and name[1:].isdigit():
                    return name.upper()
                else:
                    return name.capitalize()
        except Exception:
            pass
        return None

    def _on_press(self, key):
        key_name = self._get_key_name(key)
        if key_name:
            self.pressed_keys.add(key_name)

    def _on_release(self, key):
        if not self.pressed_keys:
            return

        modifiers = []
        regular_keys = []

        for k in self.pressed_keys:
            k_lower = k.lower()
            if k_lower in ('ctrl', 'alt', 'shift', 'cmd', 'win'):
                modifiers.append(k)
            else:
                regular_keys.append(k)

        if modifiers and regular_keys:
            order = {'Ctrl': 0, 'Alt': 1, 'Shift': 2, 'Win': 3, 'Cmd': 3}
            modifiers.sort(key=lambda x: order.get(x, 99))

            hotkey = '+'.join(modifiers + regular_keys)
            self.stop()
            self.on_capture(hotkey)

        self.pressed_keys.clear()

    def start(self) -> None:
        self.pressed_keys.clear()
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def stop(self) -> None:
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.pressed_keys.clear()
