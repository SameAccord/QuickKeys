import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from ..storage import Keybind, KeybindStore
from ..hotkeys import HotkeyManager, HotkeyCapture
from ..config import get_icon_path


class KeybindEditorDialog:

    def __init__(
        self,
        parent: tk.Toplevel,
        store: KeybindStore,
        hotkey_manager: HotkeyManager,
        keybind: Optional[Keybind] = None
    ):
        self.parent = parent
        self.store = store
        self.hotkey_manager = hotkey_manager
        self.keybind = keybind
        self.is_edit = keybind is not None
        self.result = False

        self.root: Optional[tk.Toplevel] = None
        self.hotkey_capture: Optional[HotkeyCapture] = None
        self.is_capturing = False

        self.hotkey_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.action_type_var = tk.StringVar(value='paste')
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.custom_text_var = tk.StringVar()
        self.program_path_var = tk.StringVar()
        self.program_args_var = tk.StringVar()
        self.wait_seconds_var = tk.StringVar(value='2.0')

        if self.keybind:
            self.hotkey_var.set(keybind.hotkey)
            self.name_var.set(keybind.name)
            self.action_type_var.set(keybind.action_type)
            self.username_var.set(keybind.username)
            self.password_var.set(keybind.password)
            self.custom_text_var.set(keybind.custom_text)
            self.program_path_var.set(keybind.program_path)
            self.program_args_var.set(keybind.program_args)
            self.wait_seconds_var.set(str(keybind.wait_seconds))

    def show(self) -> bool:
        self.root = tk.Toplevel(self.parent)
        self.root.title("Edit Keybind" if self.is_edit else "Add Keybind")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        self.root.transient(self.parent)
        self.root.grab_set()

        icon_path = get_icon_path()
        if icon_path:
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.root.update_idletasks()
        px = self.parent.winfo_x()
        py = self.parent.winfo_y()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        x = px + (pw - 450) // 2
        y = py + (ph - 500) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()

        self._on_action_type_changed()

        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.wait_window()

        return self.result

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkey", padding=10)
        hotkey_frame.pack(fill=tk.X, pady=(0, 10))

        hotkey_row = ttk.Frame(hotkey_frame)
        hotkey_row.pack(fill=tk.X)

        self.hotkey_entry = ttk.Entry(
            hotkey_row,
            textvariable=self.hotkey_var,
            width=25,
            state='readonly'
        )
        self.hotkey_entry.pack(side=tk.LEFT)

        self.capture_btn = ttk.Button(
            hotkey_row,
            text="Capture",
            command=self._toggle_capture,
            width=10
        )
        self.capture_btn.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(
            hotkey_frame,
            text="Click Capture, then press your desired key combination",
            foreground='gray',
            font=('Segoe UI', 8)
        ).pack(anchor=tk.W, pady=(5, 0))

        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(name_frame, text="Name:").pack(anchor=tk.W)
        ttk.Entry(
            name_frame,
            textvariable=self.name_var,
            width=50
        ).pack(fill=tk.X, pady=(2, 0))

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(action_frame, text="Action Type:").pack(anchor=tk.W)

        action_combo = ttk.Combobox(
            action_frame,
            textvariable=self.action_type_var,
            values=['paste', 'launch', 'launch_paste'],
            state='readonly',
            width=20
        )
        action_combo.pack(anchor=tk.W, pady=(2, 0))
        action_combo.bind('<<ComboboxSelected>>', lambda e: self._on_action_type_changed())

        self.paste_frame = ttk.LabelFrame(main_frame, text="Paste Settings", padding=10)
        self.paste_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.paste_frame, text="Username:").pack(anchor=tk.W)
        ttk.Entry(
            self.paste_frame,
            textvariable=self.username_var,
            width=50
        ).pack(fill=tk.X, pady=(2, 5))

        ttk.Label(self.paste_frame, text="Password:").pack(anchor=tk.W)

        password_row = ttk.Frame(self.paste_frame)
        password_row.pack(fill=tk.X, pady=(2, 5))

        self.password_entry = ttk.Entry(
            password_row,
            textvariable=self.password_var,
            show="*",
            width=45
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        eye_btn = tk.Button(
            password_row,
            text="\U0001F441",
            font=('Segoe UI', 10),
            width=3,
            relief=tk.FLAT,
            cursor="hand2"
        )
        eye_btn.pack(side=tk.LEFT, padx=(5, 0))
        eye_btn.bind('<ButtonPress-1>', lambda e: self.password_entry.config(show=""))
        eye_btn.bind('<ButtonRelease-1>', lambda e: self.password_entry.config(show="*"))

        ttk.Label(
            self.paste_frame,
            text="Or Custom Text (instead of username/password):"
        ).pack(anchor=tk.W, pady=(10, 0))
        ttk.Entry(
            self.paste_frame,
            textvariable=self.custom_text_var,
            width=50
        ).pack(fill=tk.X, pady=(2, 0))

        self.launch_frame = ttk.LabelFrame(main_frame, text="Launch Settings", padding=10)
        self.launch_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.launch_frame, text="Program Path:").pack(anchor=tk.W)

        path_row = ttk.Frame(self.launch_frame)
        path_row.pack(fill=tk.X, pady=(2, 5))

        ttk.Entry(
            path_row,
            textvariable=self.program_path_var,
            width=40
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            path_row,
            text="Browse...",
            command=self._browse_program
        ).pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(self.launch_frame, text="Arguments (optional):").pack(anchor=tk.W)
        ttk.Entry(
            self.launch_frame,
            textvariable=self.program_args_var,
            width=50
        ).pack(fill=tk.X, pady=(2, 5))

        self.wait_frame = ttk.Frame(self.launch_frame)
        self.wait_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(self.wait_frame, text="Wait before paste (seconds):").pack(side=tk.LEFT)
        ttk.Entry(
            self.wait_frame,
            textvariable=self.wait_seconds_var,
            width=10
        ).pack(side=tk.LEFT, padx=(5, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.RIGHT)

        ttk.Button(
            button_frame,
            text="Save",
            command=self._on_save
        ).pack(side=tk.RIGHT, padx=(0, 5))

    def _on_action_type_changed(self):
        action = self.action_type_var.get()

        if action in ('paste', 'launch_paste'):
            self.paste_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.paste_frame.pack_forget()

        if action in ('launch', 'launch_paste'):
            self.launch_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.launch_frame.pack_forget()

        if action == 'launch_paste':
            self.wait_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.wait_frame.pack_forget()

    def _toggle_capture(self):
        if self.is_capturing:
            self._stop_capture()
        else:
            self._start_capture()

    def _start_capture(self):
        self.is_capturing = True
        self.capture_btn.config(text="Press keys...")
        self.hotkey_var.set("Waiting...")

        self.hotkey_capture = HotkeyCapture(self._on_hotkey_captured)
        self.hotkey_capture.start()

    def _stop_capture(self):
        self.is_capturing = False
        self.capture_btn.config(text="Capture")

        if self.hotkey_capture:
            self.hotkey_capture.stop()
            self.hotkey_capture = None

    def _on_hotkey_captured(self, hotkey: str):
        self.hotkey_var.set(hotkey)
        self.is_capturing = False
        self.capture_btn.config(text="Capture")

    def _browse_program(self):
        import platform

        filetypes = [("All files", "*.*")]
        if platform.system() == "Windows":
            filetypes = [
                ("Executables", "*.exe;*.bat;*.cmd"),
                ("All files", "*.*")
            ]
        elif platform.system() == "Darwin":
            filetypes = [
                ("Applications", "*.app"),
                ("All files", "*.*")
            ]

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Select Program",
            filetypes=filetypes
        )

        if path:
            self.program_path_var.set(path)

    def _validate(self) -> bool:
        hotkey = self.hotkey_var.get()
        if not hotkey or hotkey == "Waiting...":
            messagebox.showerror("Validation Error", "Please capture a hotkey.")
            return False

        exclude_id = self.keybind.id if self.keybind else None
        if self.store.hotkey_exists(hotkey, exclude_id):
            messagebox.showerror(
                "Validation Error",
                f"The hotkey '{hotkey}' is already in use."
            )
            return False

        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Please enter a name.")
            return False

        action = self.action_type_var.get()

        if action in ('paste', 'launch_paste'):
            has_credentials = (
                self.username_var.get().strip() or
                self.password_var.get().strip()
            )
            has_custom = self.custom_text_var.get().strip()

            if not has_credentials and not has_custom:
                messagebox.showerror(
                    "Validation Error",
                    "Please enter username/password or custom text."
                )
                return False

        if action in ('launch', 'launch_paste'):
            if not self.program_path_var.get().strip():
                messagebox.showerror(
                    "Validation Error",
                    "Please select a program to launch."
                )
                return False

            if action == 'launch_paste':
                try:
                    wait = float(self.wait_seconds_var.get())
                    if wait < 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror(
                        "Validation Error",
                        "Wait seconds must be a positive number."
                    )
                    return False

        return True

    def _on_save(self):
        if self.is_capturing:
            self._stop_capture()

        if not self._validate():
            return

        try:
            wait_seconds = float(self.wait_seconds_var.get())
        except ValueError:
            wait_seconds = 2.0

        if self.keybind:
            old_hotkey = self.keybind.hotkey
            new_hotkey = self.hotkey_var.get()

            self.keybind.hotkey = new_hotkey
            self.keybind.name = self.name_var.get().strip()
            self.keybind.action_type = self.action_type_var.get()
            self.keybind.username = self.username_var.get()
            self.keybind.password = self.password_var.get()
            self.keybind.custom_text = self.custom_text_var.get()
            self.keybind.program_path = self.program_path_var.get()
            self.keybind.program_args = self.program_args_var.get()
            self.keybind.wait_seconds = wait_seconds

            if old_hotkey != new_hotkey:
                self.hotkey_manager.unregister(old_hotkey)

            self.store.update(self.keybind)
        else:
            keybind = Keybind.create_new(
                hotkey=self.hotkey_var.get(),
                name=self.name_var.get().strip(),
                action_type=self.action_type_var.get(),
                username=self.username_var.get(),
                password=self.password_var.get(),
                custom_text=self.custom_text_var.get(),
                program_path=self.program_path_var.get(),
                program_args=self.program_args_var.get(),
                wait_seconds=wait_seconds
            )
            self.store.add(keybind)

        self.result = True
        self.root.destroy()

    def _on_cancel(self):
        if self.is_capturing:
            self._stop_capture()

        self.result = False
        self.root.destroy()
