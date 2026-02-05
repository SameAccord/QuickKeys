import platform
import time
from typing import Optional

import pyperclip
from pynput.keyboard import Controller, Key


class ClipboardManager:

    def __init__(self):
        self.keyboard = Controller()
        self.system = platform.system()

    def _get_paste_modifier(self) -> Key:
        if self.system == "Darwin":
            return Key.cmd
        return Key.ctrl

    def copy_to_clipboard(self, text: str) -> None:
        pyperclip.copy(text)

    def get_from_clipboard(self) -> str:
        return pyperclip.paste()

    def simulate_paste(self) -> None:
        modifier = self._get_paste_modifier()
        time.sleep(0.05)
        with self.keyboard.pressed(modifier):
            self.keyboard.tap('v')
        time.sleep(0.05)

    def simulate_tab(self) -> None:
        time.sleep(0.05)
        self.keyboard.tap(Key.tab)
        time.sleep(0.05)

    def simulate_enter(self) -> None:
        time.sleep(0.05)
        self.keyboard.tap(Key.enter)
        time.sleep(0.05)

    def type_text(self, text: str, delay: float = 0.01) -> None:
        for char in text:
            self.keyboard.type(char)
            if delay > 0:
                time.sleep(delay)

    def paste_text(self, text: str, method: str = "clipboard") -> None:
        if method == "type":
            self.type_text(text)
        else:
            self.copy_to_clipboard(text)
            self.simulate_paste()

    def paste_credentials(
        self,
        username: str,
        password: str,
        method: str = "clipboard",
        auto_submit: bool = False
    ) -> None:
        if username:
            self.paste_text(username, method)
            time.sleep(0.1)

            self.simulate_tab()
            time.sleep(0.1)

        if password:
            self.paste_text(password, method)

            if auto_submit:
                time.sleep(0.1)
                self.simulate_enter()

    def paste_custom_text(self, text: str, method: str = "clipboard") -> None:
        self.paste_text(text, method)


class ClipboardBackup:

    def __init__(self):
        self.backup: Optional[str] = None

    def save(self) -> None:
        try:
            self.backup = pyperclip.paste()
        except Exception:
            self.backup = None

    def restore(self) -> None:
        if self.backup is not None:
            try:
                pyperclip.copy(self.backup)
            except Exception:
                pass
            self.backup = None

    def __enter__(self):
        self.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        time.sleep(0.2)
        self.restore()
        return False
