import tkinter as tk
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from . import theme


class ResetPasswordDialog:

    CONFIRMATION_WORD = "DELETE"

    def __init__(self, parent=None):
        self.parent = parent
        self.result: bool = False
        self.root: Optional[ctk.CTkToplevel] = None

    def show(self) -> bool:
        self.root = ctk.CTkToplevel(self.parent)
        self.root.title("Reset QuickKeys")
        self.root.resizable(False, False)
        self.root.configure(fg_color=theme.BG_DARK)
        self.root.transient(self.parent)
        self.root.grab_set()

        theme.set_window_icon(self.root)

        width, height = 450, 360
        self.root.geometry(f"{width}x{height}")

        self.root.update_idletasks()
        if self.parent:
            px = self.parent.winfo_x()
            py = self.parent.winfo_y()
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - height) // 2
        else:
            x = (self.root.winfo_screenwidth() - width) // 2
            y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.bind('<Escape>', lambda e: self._on_cancel())

        self.root.wait_window()
        return self.result

    def _create_widgets(self):
        frame = ctk.CTkFrame(self.root, fg_color=theme.BG_DARK)
        frame.pack(fill="both", expand=True, padx=theme.PAD * 2, pady=theme.PAD * 2)

        warning_title = ctk.CTkLabel(
            frame,
            text="⚠️ Reset All Data",
            font=theme.FONT_HEADING,
            text_color=theme.DANGER,
            anchor="w",
        )
        warning_title.pack(anchor="w")

        warning_text = (
            "Your data is protected by strong encryption that cannot be broken "
            "without your master password.\n\n"
            "If you've forgotten your password, the ONLY option is to delete "
            "all your saved keybinds and start fresh.\n\n"
            "This action is PERMANENT and CANNOT be undone."
        )
        warning_label = ctk.CTkLabel(
            frame,
            text=warning_text,
            font=theme.FONT_BODY,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
            justify="left",
            wraplength=400,
        )
        warning_label.pack(anchor="w", pady=(theme.PAD_SM, theme.PAD))

        confirm_label = ctk.CTkLabel(
            frame,
            text=f'Type "{self.CONFIRMATION_WORD}" to confirm:',
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        confirm_label.pack(anchor="w", pady=(0, 4))

        self.confirm_entry = ctk.CTkEntry(
            frame,
            width=200,
            **theme.entry_kwargs(),
        )
        self.confirm_entry.pack(anchor="w", pady=(0, theme.PAD))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(theme.PAD_SM, 0))

        reset_btn = ctk.CTkButton(
            btn_frame,
            text="Reset Everything",
            command=self._on_confirm,
            **theme.danger_button_kwargs(),
            width=140,
        )
        reset_btn.pack(side="right")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self._on_cancel,
            **theme.secondary_button_kwargs(),
            width=80,
        )
        cancel_btn.pack(side="right", padx=(0, theme.PAD_SM))

        self.confirm_entry.focus_set()

    def _on_confirm(self):
        entered = self.confirm_entry.get().strip().upper()
        if entered != self.CONFIRMATION_WORD:
            messagebox.showerror(
                "Confirmation Required",
                f'Please type "{self.CONFIRMATION_WORD}" to confirm.',
                parent=self.root,
            )
            self.confirm_entry.focus_set()
            return

        final_confirm = messagebox.askyesno(
            "Final Confirmation",
            "Are you ABSOLUTELY sure?\n\n"
            "All your keybinds will be permanently deleted.\n"
            "This cannot be undone.",
            icon="warning",
            parent=self.root,
        )

        if final_confirm:
            self.result = True
            self.root.destroy()

    def _on_cancel(self):
        self.result = False
        self.root.destroy()
