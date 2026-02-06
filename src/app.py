import platform
import sys
import threading
import tkinter as tk
from typing import Optional

import customtkinter as ctk

from .config import get_data_dir, get_icon_path, is_macos
from .encryption import EncryptionManager
from .storage import KeybindStore, Keybind
from .hotkeys import HotkeyManager
from .clipboard import ClipboardManager, ClipboardBackup
from .launcher import Launcher
from .tray import SystemTray
from tkinter import messagebox as _messagebox
from .gui.theme import configure_appearance
from .gui.master_password import MasterPasswordDialog, WrongPasswordDialog
from .gui.config_window import ConfigWindow


class QuickKeysApp:

    def __init__(self):
        self.data_dir = get_data_dir()
        self.encryption = EncryptionManager()
        self.store: Optional[KeybindStore] = None
        self.hotkeys = HotkeyManager()
        self.clipboard = ClipboardManager()
        self.launcher = Launcher()
        self.tray: Optional[SystemTray] = None
        self.config_window: Optional[ConfigWindow] = None

        self._is_unlocked = False
        self._tk_root: Optional[tk.Tk] = None

    def run(self):
        configure_appearance()

        if not self._authenticate_startup():
            return

        self._tk_root = ctk.CTk()
        self._tk_root.withdraw()

        icon_path = get_icon_path()
        if icon_path:
            try:
                self._tk_root.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.store = KeybindStore(self.encryption, self.data_dir)

        if self.store.exists():
            try:
                self.store.load()
            except Exception as e:
                print(f"Failed to load keybinds: {e}")
                self._cleanup()
                return
        else:
            self.store.save()

        self._is_unlocked = True

        self._register_all_hotkeys()

        self._start_tray()

    def _authenticate_startup(self) -> bool:
        store_file = self.data_dir / "keybinds.enc"
        is_new_setup = not store_file.exists()

        while True:
            dialog = MasterPasswordDialog(is_new_setup=is_new_setup)
            password = dialog.show()

            if password == "__RESET_DATA__":
                self._perform_data_reset()
                is_new_setup = True  # Now treat as new setup
                continue

            if password is None:
                return False

            if is_new_setup:
                self.encryption.initialize_new(password)
                return True
            else:
                try:
                    encrypted_data = store_file.read_bytes()
                    if self.encryption.verify_password(password, encrypted_data):
                        self.encryption.initialize_existing(password, encrypted_data)
                        return True
                    else:
                        retry_dialog = WrongPasswordDialog()
                        if not retry_dialog.show():
                            return False
                except Exception as e:
                    print(f"Error reading store: {e}")
                    retry_dialog = WrongPasswordDialog()
                    if not retry_dialog.show():
                        return False

    def _authenticate_relock(self) -> bool:
        store_file = self.data_dir / "keybinds.enc"

        while True:
            dialog = MasterPasswordDialog(
                is_new_setup=False,
                parent=self._tk_root
            )
            password = dialog.show()

            if password is None:
                return False

            try:
                encrypted_data = store_file.read_bytes()
                if self.encryption.verify_password(password, encrypted_data):
                    self.encryption.initialize_existing(password, encrypted_data)
                    return True
                else:
                    _messagebox.showerror(
                        "Invalid Password",
                        "The password you entered is incorrect.\nPlease try again.",
                        parent=self._tk_root
                    )
            except Exception as e:
                print(f"Error reading store: {e}")
                _messagebox.showerror(
                    "Error",
                    f"Error reading encrypted store.\nPlease try again.",
                    parent=self._tk_root
                )

    def _register_all_hotkeys(self):
        if not self.store:
            return

        for keybind in self.store.get_all():
            self._register_hotkey(keybind)

        self.hotkeys.start()

    def _register_hotkey(self, keybind: Keybind):
        def callback(kb=keybind):
            thread = threading.Thread(
                target=self._execute_keybind,
                args=(kb,),
                daemon=True
            )
            thread.start()

        self.hotkeys.register(keybind.hotkey, callback)

    def _unregister_hotkey(self, keybind: Keybind):
        self.hotkeys.unregister(keybind.hotkey)

    def _execute_keybind(self, keybind: Keybind):
        action = keybind.action_type

        try:
            if action == 'paste':
                self._execute_paste(keybind)
            elif action == 'launch':
                self._execute_launch(keybind)
            elif action == 'launch_paste':
                self._execute_launch_paste(keybind)
        except Exception as e:
            print(f"Error executing keybind {keybind.name}: {e}")

    def _execute_paste(self, keybind: Keybind):
        with ClipboardBackup():
            if keybind.custom_text:
                self.clipboard.paste_custom_text(keybind.custom_text)
            else:
                self.clipboard.paste_credentials(
                    keybind.username,
                    keybind.password
                )

    def _execute_launch(self, keybind: Keybind):
        self.launcher.launch(
            keybind.program_path,
            keybind.program_args
        )

    def _execute_launch_paste(self, keybind: Keybind):
        success = self.launcher.launch_and_wait(
            keybind.program_path,
            keybind.program_args,
            keybind.wait_seconds
        )

        if success:
            self._execute_paste(keybind)

    def _start_tray(self):
        self.tray = SystemTray(
            on_configure=self._on_configure,
            on_quit=self._on_quit,
            on_lock=self._on_lock
        )

        self.tray.run_detached()
        self._tk_root.mainloop()

    def _on_configure(self):
        if self._tk_root:
            self._tk_root.after(0, self._handle_configure)

    def _handle_configure(self):
        if not self.store:
            return

        if not self._is_unlocked:
            self._try_unlock()
            if not self._is_unlocked:
                return

        if self.config_window is None:
            self.config_window = ConfigWindow(
                self._tk_root,
                self.store,
                self.hotkeys,
                on_keybinds_changed=self._on_keybinds_changed
            )

        self.config_window.show()

    def _on_keybinds_changed(self):
        self.hotkeys.unregister_all()
        self._register_all_hotkeys()

    def _on_lock(self):
        if self._tk_root:
            self._tk_root.after(0, self._handle_lock)

    def _handle_lock(self):
        if not self._is_unlocked:
            self._try_unlock()
            return

        self.encryption.clear()
        self._is_unlocked = False

        self.hotkeys.unregister_all()

        if self.config_window and self.config_window.root:
            self.config_window.root.destroy()
            self.config_window = None

        self._try_unlock()

    def _try_unlock(self):
        if self._authenticate_relock():
            self._is_unlocked = True
            if self.store:
                self.store.load()
            self._register_all_hotkeys()

    def _on_quit(self):
        if self._tk_root:
            self._tk_root.after(0, self._handle_quit)

    def _handle_quit(self):
        self._cleanup()

        if self._tk_root:
            self._tk_root.quit()

    def _cleanup(self):
        self.hotkeys.stop()

        self.encryption.clear()

        if self.tray:
            self.tray.stop()

        self._is_unlocked = False

    def _perform_data_reset(self):
        store_file = self.data_dir / "keybinds.enc"
        try:
            if store_file.exists():
                store_file.unlink()
            print("Data reset complete. Starting fresh setup.")
        except Exception as e:
            print(f"Error deleting data file: {e}")
            _messagebox.showerror(
                "Reset Error",
                f"Could not delete data file:\n{e}\n\n"
                f"Please manually delete:\n{store_file}"
            )
