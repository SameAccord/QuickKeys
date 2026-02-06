import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional

import customtkinter as ctk

from ..storage import Keybind, KeybindStore
from ..hotkeys import HotkeyManager, HotkeyCapture
from . import theme


class KeybindEditorDialog:

    def __init__(
        self,
        parent: ctk.CTkToplevel,
        store: KeybindStore,
        hotkey_manager: HotkeyManager,
        keybind: Optional[Keybind] = None,
    ):
        self.parent = parent
        self.store = store
        self.hotkey_manager = hotkey_manager
        self.keybind = keybind
        self.is_edit = keybind is not None
        self.result = False

        self.root: Optional[ctk.CTkToplevel] = None
        self.hotkey_capture: Optional[HotkeyCapture] = None
        self.is_capturing = False

        self.hotkey_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.action_type_var = tk.StringVar(value='paste')
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.program_path_var = tk.StringVar()
        self.program_args_var = tk.StringVar()
        self.wait_seconds_var = tk.StringVar(value='2.0')

        if self.keybind:
            self.hotkey_var.set(keybind.hotkey)
            self.name_var.set(keybind.name)
            self.action_type_var.set(keybind.action_type)
            self.username_var.set(keybind.username)
            self.password_var.set(keybind.password)
            self.program_path_var.set(keybind.program_path)
            self.program_args_var.set(keybind.program_args)
            self.wait_seconds_var.set(str(keybind.wait_seconds))

    def show(self) -> bool:
        self.root = ctk.CTkToplevel(self.parent)
        self.root.title("Edit Keybind" if self.is_edit else "Add Keybind")
        self.root.geometry("470x560")
        self.root.resizable(False, False)
        self.root.transient(self.parent)
        self.root.grab_set()
        self.root.configure(fg_color=theme.BG_DARK)

        theme.set_window_icon(self.root)

        self.root.update_idletasks()
        px = self.parent.winfo_x()
        py = self.parent.winfo_y()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        x = px + (pw - 470) // 2
        y = py + (ph - 560) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._on_action_type_changed(self.action_type_var.get())

        if self.keybind and self.keybind.custom_text:
            self.custom_text_box.insert("1.0", self.keybind.custom_text)

        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.wait_window()

        return self.result

    def _create_widgets(self):
        self.main_frame = ctk.CTkScrollableFrame(
            self.root,
            fg_color=theme.BG_DARK,
            scrollbar_button_color=theme.SURFACE,
            scrollbar_button_hover_color=theme.SURFACE_HOVER,
        )
        self.main_frame.pack(fill="both", expand=True, padx=theme.PAD, pady=(theme.PAD, 0))

        self._section_label(self.main_frame, "Hotkey")

        hotkey_card = ctk.CTkFrame(self.main_frame, fg_color=theme.SURFACE, corner_radius=theme.CORNER_RADIUS)
        hotkey_card.pack(fill="x", pady=(0, theme.PAD_SM))

        hotkey_inner = ctk.CTkFrame(hotkey_card, fg_color="transparent")
        hotkey_inner.pack(fill="x", padx=theme.PAD_SM, pady=theme.PAD_SM)

        self.hotkey_entry = ctk.CTkEntry(
            hotkey_inner,
            textvariable=self.hotkey_var,
            width=200,
            state='readonly',
            **theme.entry_kwargs(),
        )
        self.hotkey_entry.pack(side="left")

        self.capture_btn = ctk.CTkButton(
            hotkey_inner,
            text="Capture",
            command=self._toggle_capture,
            width=100,
            **theme.accent_button_kwargs(),
        )
        self.capture_btn.pack(side="left", padx=(theme.PAD_SM, 0))

        ctk.CTkLabel(
            hotkey_card,
            text="Click Capture, then press your desired key combination",
            font=theme.FONT_TINY,
            text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.PAD_SM, pady=(0, theme.PAD_SM))

        self._section_label(self.main_frame, "Name")
        self.name_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.name_var,
            **theme.entry_kwargs(),
        )
        self.name_entry.pack(fill="x", pady=(0, theme.PAD_SM))

        self._section_label(self.main_frame, "Action Type")
        self.action_combo = ctk.CTkOptionMenu(
            self.main_frame,
            variable=self.action_type_var,
            values=['paste', 'launch', 'launch_paste'],
            command=self._on_action_type_changed,
            width=180,
            height=theme.ENTRY_HEIGHT,
            font=theme.FONT_BODY,
            fg_color=theme.SURFACE,
            button_color=theme.ACCENT,
            button_hover_color=theme.ACCENT_HOVER,
            dropdown_fg_color=theme.SURFACE,
            dropdown_hover_color=theme.SURFACE_HOVER,
            dropdown_text_color=theme.TEXT_PRIMARY,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.BUTTON_RADIUS,
        )
        self.action_combo.pack(anchor="w", pady=(0, theme.PAD_SM))

        self.paste_section = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        self._section_label(self.paste_section, "Paste Settings")

        paste_card = ctk.CTkFrame(self.paste_section, fg_color=theme.SURFACE, corner_radius=theme.CORNER_RADIUS)
        paste_card.pack(fill="x", pady=(0, theme.PAD_SM))
        paste_inner = ctk.CTkFrame(paste_card, fg_color="transparent")
        paste_inner.pack(fill="x", padx=theme.PAD_SM, pady=theme.PAD_SM)

        ctk.CTkLabel(paste_inner, text="Username", font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY).pack(anchor="w")
        ctk.CTkEntry(
            paste_inner, textvariable=self.username_var, **theme.entry_kwargs(),
        ).pack(fill="x", pady=(2, theme.PAD_SM))

        ctk.CTkLabel(paste_inner, text="Password", font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY).pack(anchor="w")

        pw_row = ctk.CTkFrame(paste_inner, fg_color="transparent")
        pw_row.pack(fill="x", pady=(2, theme.PAD_SM))

        self.password_entry = ctk.CTkEntry(
            pw_row, textvariable=self.password_var, show="*",
            **theme.entry_kwargs(),
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        generate_btn = ctk.CTkButton(
            pw_row, text="Generate",
            command=self._open_password_generator,
            width=80,
            **theme.secondary_button_kwargs(),
        )
        generate_btn.pack(side="left", padx=(theme.PAD_SM, 0))

        self._pw_visible = False
        self.eye_btn = ctk.CTkButton(
            pw_row, text="\U0001F441", width=40,
            fg_color=theme.SURFACE_HOVER,
            hover_color=theme.SURFACE_SELECT,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=theme.BUTTON_RADIUS,
            height=theme.ENTRY_HEIGHT,
            font=theme.FONT_BODY,
            command=self._toggle_password_visibility,
        )
        self.eye_btn.pack(side="left", padx=(theme.PAD_SM, 0))

        ctk.CTkLabel(
            paste_inner,
            text="Or Custom Text (instead of username/password):",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(theme.PAD_SM, 0))

        self.custom_text_box = ctk.CTkTextbox(
            paste_inner,
            height=70,
            fg_color=theme.INPUT_BG,
            border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.BUTTON_RADIUS,
            font=theme.FONT_BODY,
            wrap="word",
        )
        self.custom_text_box.pack(fill="x", pady=(2, theme.PAD_SM))

        self._custom_text_actual = ""
        self._custom_text_visible = True

        custom_btn_row = ctk.CTkFrame(paste_inner, fg_color="transparent")
        custom_btn_row.pack(fill="x", pady=(0, 0), anchor="e")

        custom_generate_btn = ctk.CTkButton(
            custom_btn_row, text="Generate",
            command=self._open_custom_text_generator,
            width=80,
            **theme.secondary_button_kwargs(),
        )
        custom_generate_btn.pack(side="right", padx=(theme.PAD_SM, 0))

        self.custom_eye_btn = ctk.CTkButton(
            custom_btn_row, text="\U0001F441", width=40,
            fg_color=theme.SURFACE_HOVER,
            hover_color=theme.SURFACE_SELECT,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=theme.BUTTON_RADIUS,
            height=theme.BUTTON_HEIGHT,
            font=theme.FONT_BODY,
            command=self._toggle_custom_text_visibility,
        )
        self.custom_eye_btn.pack(side="right")

        self.launch_section = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        self._section_label(self.launch_section, "Launch Settings")

        launch_card = ctk.CTkFrame(self.launch_section, fg_color=theme.SURFACE, corner_radius=theme.CORNER_RADIUS)
        launch_card.pack(fill="x", pady=(0, theme.PAD_SM))
        launch_inner = ctk.CTkFrame(launch_card, fg_color="transparent")
        launch_inner.pack(fill="x", padx=theme.PAD_SM, pady=theme.PAD_SM)

        ctk.CTkLabel(launch_inner, text="Program Path", font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY).pack(anchor="w")

        path_row = ctk.CTkFrame(launch_inner, fg_color="transparent")
        path_row.pack(fill="x", pady=(2, theme.PAD_SM))

        ctk.CTkEntry(
            path_row, textvariable=self.program_path_var, **theme.entry_kwargs(),
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            path_row, text="Browse",
            command=self._browse_program,
            width=80,
            **theme.secondary_button_kwargs(),
        ).pack(side="left", padx=(theme.PAD_SM, 0))

        ctk.CTkLabel(launch_inner, text="Arguments (optional)", font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY).pack(anchor="w")
        ctk.CTkEntry(
            launch_inner, textvariable=self.program_args_var, **theme.entry_kwargs(),
        ).pack(fill="x", pady=(2, 0))

        self.wait_section = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        wait_inner = ctk.CTkFrame(self.wait_section, fg_color="transparent")
        wait_inner.pack(fill="x")

        ctk.CTkLabel(wait_inner, text="Wait before paste (seconds):", font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY).pack(side="left")
        ctk.CTkEntry(
            wait_inner, textvariable=self.wait_seconds_var, width=80,
            **theme.entry_kwargs(),
        ).pack(side="left", padx=(theme.PAD_SM, 0))

        btn_frame = ctk.CTkFrame(self.root, fg_color=theme.BG_DARK)
        btn_frame.pack(fill="x", padx=theme.PAD, pady=theme.PAD)

        save_btn = ctk.CTkButton(
            btn_frame, text="Save",
            command=self._on_save,
            **theme.accent_button_kwargs(),
            width=90,
        )
        save_btn.pack(side="right")

        cancel_btn = ctk.CTkButton(
            btn_frame, text="Cancel",
            command=self._on_cancel,
            **theme.secondary_button_kwargs(),
            width=90,
        )
        cancel_btn.pack(side="right", padx=(0, theme.PAD_SM))

    @staticmethod
    def _section_label(parent, text: str):
        ctk.CTkLabel(
            parent,
            text=text,
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(theme.PAD_SM, 4))

    def _toggle_password_visibility(self):
        self._pw_visible = not self._pw_visible
        self.password_entry.configure(show="" if self._pw_visible else "*")

    def _open_password_generator(self):
        from .password_generator import PasswordGeneratorDialog

        dialog = PasswordGeneratorDialog(parent=self.root)
        password = dialog.show()

        if password:
            self.password_var.set(password)
            if not self._pw_visible:
                self._pw_visible = True
                self.password_entry.configure(show="")

    def _toggle_custom_text_visibility(self):
        if self._custom_text_visible:
            self._custom_text_actual = self.custom_text_box.get("1.0", "end-1c")
            self.custom_text_box.delete("1.0", "end")
            self.custom_text_box.insert("1.0", "*" * len(self._custom_text_actual))
            self._custom_text_visible = False
        else:
            self.custom_text_box.delete("1.0", "end")
            self.custom_text_box.insert("1.0", self._custom_text_actual)
            self._custom_text_visible = True

    def _open_custom_text_generator(self):
        from .password_generator import PasswordGeneratorDialog

        dialog = PasswordGeneratorDialog(parent=self.root)
        password = dialog.show()

        if password:
            if not self._custom_text_visible:
                self._custom_text_visible = True

            try:
                self.custom_text_box.delete("sel.first", "sel.last")
            except tk.TclError:
                pass
            self.custom_text_box.insert("insert", password)

    def _get_custom_text(self) -> str:
        if self._custom_text_visible:
            return self.custom_text_box.get("1.0", "end-1c")
        else:
            return self._custom_text_actual

    def _on_action_type_changed(self, value: str = None):
        action = self.action_type_var.get()

        if action in ('paste', 'launch_paste'):
            self.paste_section.pack(fill="x", after=self.action_combo)
        else:
            self.paste_section.pack_forget()

        if action in ('launch', 'launch_paste'):
            self.launch_section.pack(fill="x", after=self.paste_section if self.paste_section.winfo_ismapped() else self.action_combo)
        else:
            self.launch_section.pack_forget()

        if action == 'launch_paste':
            self.wait_section.pack(fill="x", after=self.launch_section, pady=(0, theme.PAD_SM))
        else:
            self.wait_section.pack_forget()

    def _toggle_capture(self):
        if self.is_capturing:
            self._stop_capture()
        else:
            self._start_capture()

    def _start_capture(self):
        self.is_capturing = True
        self.capture_btn.configure(text="Press keys...")
        self.hotkey_var.set("Waiting...")

        self.hotkey_capture = HotkeyCapture(self._on_hotkey_captured)
        self.hotkey_capture.start()

    def _stop_capture(self):
        self.is_capturing = False
        self.capture_btn.configure(text="Capture")

        if self.hotkey_capture:
            self.hotkey_capture.stop()
            self.hotkey_capture = None

    def _on_hotkey_captured(self, hotkey: str):
        self.hotkey_var.set(hotkey)
        self.is_capturing = False
        self.capture_btn.configure(text="Capture")

    def _browse_program(self):
        import platform

        filetypes = [("All files", "*.*")]
        if platform.system() == "Windows":
            filetypes = [
                ("Executables", "*.exe;*.bat;*.cmd"),
                ("All files", "*.*"),
            ]
        elif platform.system() == "Darwin":
            filetypes = [
                ("Applications", "*.app"),
                ("All files", "*.*"),
            ]

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Select Program",
            filetypes=filetypes,
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
                f"The hotkey '{hotkey}' is already in use.",
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
            has_custom = self._get_custom_text().strip()

            if not has_credentials and not has_custom:
                messagebox.showerror(
                    "Validation Error",
                    "Please enter username/password or custom text.",
                )
                return False

        if action in ('launch', 'launch_paste'):
            if not self.program_path_var.get().strip():
                messagebox.showerror(
                    "Validation Error",
                    "Please select a program to launch.",
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
                        "Wait seconds must be a positive number.",
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
            self.keybind.custom_text = self._get_custom_text()
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
                custom_text=self._get_custom_text(),
                program_path=self.program_path_var.get(),
                program_args=self.program_args_var.get(),
                wait_seconds=wait_seconds,
            )
            self.store.add(keybind)

        self.result = True
        self.root.destroy()

    def _on_cancel(self):
        if self.is_capturing:
            self._stop_capture()

        self.result = False
        self.root.destroy()
