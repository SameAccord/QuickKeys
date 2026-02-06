import secrets
import string
import tkinter as tk
from typing import Optional

import customtkinter as ctk

from . import theme


class PasswordGeneratorDialog:

    DEFAULT_LENGTH = 20
    MIN_LENGTH = 8
    MAX_LENGTH = 64

    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SPECIAL = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def __init__(self, parent=None):
        self.parent = parent
        self.result: Optional[str] = None
        self.root: Optional[ctk.CTkToplevel] = None

        self.length_var = tk.IntVar(value=self.DEFAULT_LENGTH)
        self.include_numbers_var = tk.BooleanVar(value=True)
        self.include_special_var = tk.BooleanVar(value=True)
        self.preview_var = tk.StringVar()

    def show(self) -> Optional[str]:
        self.root = ctk.CTkToplevel(self.parent)
        self.root.title("Generate Password")
        self.root.resizable(False, False)
        self.root.configure(fg_color=theme.BG_DARK)
        self.root.transient(self.parent)
        self.root.grab_set()

        theme.set_window_icon(self.root)

        width, height = 380, 380
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(width, height)

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
        self._generate_password()

        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.root.bind('<Escape>', lambda e: self._on_cancel())
        self.root.bind('<Return>', lambda e: self._on_use())

        self.root.wait_window()
        return self.result

    def _create_widgets(self):
        frame = ctk.CTkFrame(self.root, fg_color=theme.BG_DARK)
        frame.pack(fill="both", expand=True, padx=theme.PAD, pady=(theme.PAD, 0))

        title_label = ctk.CTkLabel(
            frame,
            text="Password Generator",
            font=theme.FONT_HEADING,
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            frame,
            text="Generate a secure random password",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        subtitle_label.pack(anchor="w", pady=(0, theme.PAD_SM))

        options_card = ctk.CTkFrame(
            frame,
            fg_color=theme.SURFACE,
            corner_radius=theme.CORNER_RADIUS,
        )
        options_card.pack(fill="x", pady=(0, theme.PAD_SM))

        options_inner = ctk.CTkFrame(options_card, fg_color="transparent")
        options_inner.pack(fill="x", padx=theme.PAD_SM, pady=theme.PAD_SM)

        length_row = ctk.CTkFrame(options_inner, fg_color="transparent")
        length_row.pack(fill="x", pady=(0, theme.PAD_SM))

        ctk.CTkLabel(
            length_row,
            text="Length:",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
        ).pack(side="left")

        self.length_label = ctk.CTkLabel(
            length_row,
            text=str(self.DEFAULT_LENGTH),
            font=theme.FONT_BODY,
            text_color=theme.TEXT_PRIMARY,
            width=30,
        )
        self.length_label.pack(side="right")

        self.length_slider = ctk.CTkSlider(
            length_row,
            from_=self.MIN_LENGTH,
            to=self.MAX_LENGTH,
            number_of_steps=self.MAX_LENGTH - self.MIN_LENGTH,
            variable=self.length_var,
            command=self._on_length_changed,
            fg_color=theme.SURFACE_HOVER,
            progress_color=theme.ACCENT,
            button_color=theme.ACCENT,
            button_hover_color=theme.ACCENT_HOVER,
        )
        self.length_slider.pack(side="right", fill="x", expand=True, padx=(theme.PAD_SM, theme.PAD_SM))

        numbers_check = ctk.CTkCheckBox(
            options_inner,
            text="Include numbers (0-9)",
            variable=self.include_numbers_var,
            command=self._on_option_changed,
            font=theme.FONT_BODY,
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOVER,
            border_color=theme.BORDER,
            checkmark_color=theme.TEXT_PRIMARY,
        )
        numbers_check.pack(anchor="w", pady=(0, theme.PAD_SM))

        special_check = ctk.CTkCheckBox(
            options_inner,
            text="Include special characters (!@#$...)",
            variable=self.include_special_var,
            command=self._on_option_changed,
            font=theme.FONT_BODY,
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOVER,
            border_color=theme.BORDER,
            checkmark_color=theme.TEXT_PRIMARY,
        )
        special_check.pack(anchor="w")

        preview_label = ctk.CTkLabel(
            frame,
            text="Generated Password:",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        preview_label.pack(anchor="w", pady=(theme.PAD_SM, 4))

        preview_row = ctk.CTkFrame(frame, fg_color="transparent")
        preview_row.pack(fill="x")

        entry_kwargs = theme.entry_kwargs()
        entry_kwargs['font'] = ("Consolas", 12)

        self.preview_entry = ctk.CTkEntry(
            preview_row,
            textvariable=self.preview_var,
            state='readonly',
            **entry_kwargs,
        )
        self.preview_entry.pack(side="left", fill="x", expand=True)

        regenerate_btn = ctk.CTkButton(
            preview_row,
            text="🔄",
            width=40,
            command=self._generate_password,
            fg_color=theme.SURFACE,
            hover_color=theme.SURFACE_HOVER,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=theme.BUTTON_RADIUS,
            height=theme.ENTRY_HEIGHT,
            font=theme.FONT_BODY,
        )
        regenerate_btn.pack(side="left", padx=(theme.PAD_SM, 0))

        btn_frame = ctk.CTkFrame(self.root, fg_color=theme.BG_DARK)
        btn_frame.pack(fill="x", padx=theme.PAD, pady=theme.PAD)

        use_btn = ctk.CTkButton(
            btn_frame,
            text="Use Password",
            command=self._on_use,
            **theme.accent_button_kwargs(),
            width=120,
        )
        use_btn.pack(side="right")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self._on_cancel,
            **theme.secondary_button_kwargs(),
            width=80,
        )
        cancel_btn.pack(side="right", padx=(0, theme.PAD_SM))

    def _generate_password(self):
        length = self.length_var.get()

        charset = self.LOWERCASE + self.UPPERCASE

        if self.include_numbers_var.get():
            charset += self.DIGITS

        if self.include_special_var.get():
            charset += self.SPECIAL

        password = ''.join(secrets.choice(charset) for _ in range(length))

        required_chars = []
        required_chars.append(secrets.choice(self.LOWERCASE))
        required_chars.append(secrets.choice(self.UPPERCASE))

        if self.include_numbers_var.get():
            required_chars.append(secrets.choice(self.DIGITS))

        if self.include_special_var.get():
            required_chars.append(secrets.choice(self.SPECIAL))

        password_list = list(password)
        positions = secrets.SystemRandom().sample(range(length), min(len(required_chars), length))

        for i, char in enumerate(required_chars[:len(positions)]):
            password_list[positions[i]] = char

        secrets.SystemRandom().shuffle(password_list)
        password = ''.join(password_list)

        self.preview_var.set(password)

    def _on_length_changed(self, value):
        length = int(value)
        self.length_label.configure(text=str(length))
        self._generate_password()

    def _on_option_changed(self):
        self._generate_password()

    def _on_use(self):
        self.result = self.preview_var.get()
        self.root.destroy()

    def _on_cancel(self):
        self.result = None
        self.root.destroy()
