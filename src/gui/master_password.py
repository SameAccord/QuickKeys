import tkinter as tk
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from . import theme


class MasterPasswordDialog:

    MIN_PASSWORD_LENGTH = 8

    def __init__(self, is_new_setup: bool = False, parent=None):
        self.is_new_setup = is_new_setup
        self.parent = parent
        self.is_relock = parent is not None and not is_new_setup
        self.result: Optional[str] = None
        self.root = None

    def show(self) -> Optional[str]:
        if self.parent:
            self.root = ctk.CTkToplevel(self.parent)
            self.root.focus_force()
            if self.is_relock:
                self.root.wm_attributes('-toolwindow', False)
            else:
                self.root.grab_set()
        else:
            self.root = ctk.CTk()

        self.root.title("QuickKeys")
        self.root.resizable(False, False)
        self.root.configure(fg_color=theme.BG_DARK)

        theme.set_window_icon(self.root)

        height = 320 if self.is_new_setup else 300
        width = 420
        self.root.geometry(f"{width}x{height}")

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.attributes('-topmost', True)

        self._create_widgets()

        self.password_entry.focus_set()

        if self.parent:
            self.root.wait_window()
        else:
            self.root.mainloop()

        return self.result

    def _create_widgets(self):
        frame = ctk.CTkFrame(self.root, fg_color=theme.BG_DARK)
        frame.pack(fill="both", expand=True, padx=theme.PAD * 2, pady=(theme.PAD, theme.PAD * 2))

        if self.is_new_setup:
            title = "Create Master Password"
            subtitle = "This password will encrypt your keybinds."
        else:
            title = "Unlock QuickKeys"
            subtitle = "Enter your master password to continue."

        title_label = ctk.CTkLabel(
            frame, text=title,
            font=theme.FONT_HEADING,
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            frame, text=subtitle,
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        subtitle_label.pack(anchor="w", pady=(0, theme.PAD))

        pw_label = ctk.CTkLabel(
            frame, text="Password",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        pw_label.pack(anchor="w", pady=(0, 4))

        pw_row = ctk.CTkFrame(frame, fg_color="transparent")
        pw_row.pack(fill="x", pady=(0, theme.PAD_SM))

        self.password_entry = ctk.CTkEntry(
            pw_row, show="*", width=320,
            **theme.entry_kwargs(),
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        self._pw_visible = False
        self.eye_btn = ctk.CTkButton(
            pw_row, text="\U0001F441", width=40,
            fg_color=theme.SURFACE,
            hover_color=theme.SURFACE_HOVER,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=theme.BUTTON_RADIUS,
            height=theme.ENTRY_HEIGHT,
            font=theme.FONT_BODY,
            command=self._toggle_password_visibility,
        )
        self.eye_btn.pack(side="left", padx=(theme.PAD_SM, 0))

        if self.is_new_setup:
            cf_label = ctk.CTkLabel(
                frame, text="Confirm Password",
                font=theme.FONT_SMALL,
                text_color=theme.TEXT_SECONDARY,
                anchor="w",
            )
            cf_label.pack(anchor="w", pady=(theme.PAD_SM, 4))

            cf_row = ctk.CTkFrame(frame, fg_color="transparent")
            cf_row.pack(fill="x", pady=(0, theme.PAD_SM))

            self.confirm_entry = ctk.CTkEntry(
                cf_row, show="*", width=320,
                **theme.entry_kwargs(),
            )
            self.confirm_entry.pack(side="left", fill="x", expand=True)

            self._cf_visible = False
            self.confirm_eye_btn = ctk.CTkButton(
                cf_row, text="\U0001F441", width=40,
                fg_color=theme.SURFACE,
                hover_color=theme.SURFACE_HOVER,
                text_color=theme.TEXT_SECONDARY,
                corner_radius=theme.BUTTON_RADIUS,
                height=theme.ENTRY_HEIGHT,
                font=theme.FONT_BODY,
                command=self._toggle_confirm_visibility,
            )
            self.confirm_eye_btn.pack(side="left", padx=(theme.PAD_SM, 0))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(theme.PAD, 0))

        submit_text = "Create" if self.is_new_setup else "Unlock"
        submit_btn = ctk.CTkButton(
            btn_frame, text=submit_text,
            command=self._on_submit,
            **theme.accent_button_kwargs(),
        )
        submit_btn.pack(side="right")

        if not self.is_relock:
            cancel_btn = ctk.CTkButton(
                btn_frame, text="Cancel",
                command=self._on_cancel,
                **theme.secondary_button_kwargs(),
            )
            cancel_btn.pack(side="right", padx=(0, theme.PAD_SM))

        if not self.is_new_setup and not self.is_relock:
            forgot_link = ctk.CTkLabel(
                frame,
                text="Forgot your password?",
                font=theme.FONT_SMALL,
                text_color=theme.ACCENT,
                cursor="hand2",
            )
            forgot_link.pack(anchor="w", pady=(theme.PAD, 0))
            forgot_link.bind("<Button-1>", lambda e: self._on_forgot_password())

        self.root.bind('<Return>', lambda e: self._on_submit())
        if not self.is_relock:
            self.root.bind('<Escape>', lambda e: self._on_cancel())

    def _toggle_password_visibility(self):
        self._pw_visible = not self._pw_visible
        self.password_entry.configure(show="" if self._pw_visible else "*")

    def _toggle_confirm_visibility(self):
        self._cf_visible = not self._cf_visible
        self.confirm_entry.configure(show="" if self._cf_visible else "*")

    def _on_submit(self):
        password = self.password_entry.get()

        if not password:
            messagebox.showerror("Error", "Please enter a password.", parent=self.root)
            self.password_entry.focus_set()
            return

        if self.is_new_setup:
            if len(password) < self.MIN_PASSWORD_LENGTH:
                messagebox.showerror(
                    "Error",
                    f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters.",
                    parent=self.root,
                )
                self.password_entry.focus_set()
                return

            confirm = self.confirm_entry.get()
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match.", parent=self.root)
                self.confirm_entry.focus_set()
                return

        self.result = password
        self.root.destroy()

    def _on_cancel(self):
        self.result = None
        self.root.destroy()

    def _on_forgot_password(self):
        from .reset_password import ResetPasswordDialog

        dialog = ResetPasswordDialog(parent=self.root)
        if dialog.show():
            self.result = "__RESET_DATA__"
            self.root.destroy()


class WrongPasswordDialog:

    def __init__(self, parent=None):
        self.parent = parent
        self.result: bool = False

    def show(self) -> bool:
        if self.parent:
            result = messagebox.askretrycancel(
                "Invalid Password",
                "The password you entered is incorrect.\n\nWould you like to try again?",
                parent=self.parent,
            )
        else:
            root = ctk.CTk()
            root.withdraw()
            result = messagebox.askretrycancel(
                "Invalid Password",
                "The password you entered is incorrect.\n\nWould you like to try again?",
            )
            root.destroy()

        return result
