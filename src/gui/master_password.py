import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from ..config import get_icon_path


def _set_window_icon(window):
    icon_path = get_icon_path()
    if icon_path:
        try:
            window.iconbitmap(str(icon_path))
        except Exception:
            pass


class MasterPasswordDialog:

    MIN_PASSWORD_LENGTH = 8

    def __init__(self, is_new_setup: bool = False, parent: Optional[tk.Tk] = None):
        self.is_new_setup = is_new_setup
        self.parent = parent
        self.is_relock = parent is not None and not is_new_setup
        self.result: Optional[str] = None
        self.root: Optional[tk.BaseWidget] = None

    def show(self) -> Optional[str]:
        if self.parent:
            self.root = tk.Toplevel(self.parent)
            self.root.focus_force()
            if self.is_relock:
                self.root.wm_attributes('-toolwindow', False)
            else:
                self.root.grab_set()
        else:
            self.root = tk.Tk()

        self.root.title("QuickKeys")
        self.root.resizable(False, False)

        _set_window_icon(self.root)

        height = 220 if self.is_new_setup else 160
        self.root.geometry(f"400x{height}")

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 400) // 2
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

    def _create_eye_button(self, parent, entry_widget):
        eye_btn = tk.Button(
            parent,
            text="\U0001F441",
            font=('Segoe UI', 10),
            width=3,
            relief=tk.FLAT,
            cursor="hand2"
        )

        def show_password(event):
            entry_widget.config(show="")

        def hide_password(event):
            entry_widget.config(show="*")

        eye_btn.bind('<ButtonPress-1>', show_password)
        eye_btn.bind('<ButtonRelease-1>', hide_password)

        return eye_btn

    def _create_widgets(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        if self.is_new_setup:
            title = "Create Master Password"
            subtitle = "This password will encrypt your keybinds."
        else:
            title = "Unlock QuickKeys"
            subtitle = "Enter your master password to continue."

        title_label = ttk.Label(frame, text=title, font=('Segoe UI', 12, 'bold'))
        title_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(frame, text=subtitle, foreground='gray')
        subtitle_label.pack(anchor=tk.W, pady=(0, 15))

        password_frame = ttk.Frame(frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(password_frame, text="Password:").pack(anchor=tk.W)

        password_row = ttk.Frame(password_frame)
        password_row.pack(fill=tk.X, pady=(2, 0))

        self.password_entry = ttk.Entry(password_row, show="*", width=40)
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        eye_btn = self._create_eye_button(password_row, self.password_entry)
        eye_btn.pack(side=tk.LEFT, padx=(5, 0))

        if self.is_new_setup:
            confirm_frame = ttk.Frame(frame)
            confirm_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(confirm_frame, text="Confirm Password:").pack(anchor=tk.W)

            confirm_row = ttk.Frame(confirm_frame)
            confirm_row.pack(fill=tk.X, pady=(2, 0))

            self.confirm_entry = ttk.Entry(confirm_row, show="*", width=40)
            self.confirm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            confirm_eye_btn = self._create_eye_button(confirm_row, self.confirm_entry)
            confirm_eye_btn.pack(side=tk.LEFT, padx=(5, 0))

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        if not self.is_relock:
            cancel_btn = ttk.Button(
                button_frame,
                text="Cancel",
                command=self._on_cancel
            )
            cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        submit_text = "Create" if self.is_new_setup else "Unlock"
        submit_btn = ttk.Button(
            button_frame,
            text=submit_text,
            command=self._on_submit
        )
        submit_btn.pack(side=tk.RIGHT)

        self.root.bind('<Return>', lambda e: self._on_submit())
        if not self.is_relock:
            self.root.bind('<Escape>', lambda e: self._on_cancel())

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
                    parent=self.root
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


class WrongPasswordDialog:

    def __init__(self, parent: Optional[tk.BaseWidget] = None):
        self.parent = parent
        self.result: bool = False

    def show(self) -> bool:
        if self.parent:
            result = messagebox.askretrycancel(
                "Invalid Password",
                "The password you entered is incorrect.\n\nWould you like to try again?",
                parent=self.parent
            )
        else:
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askretrycancel(
                "Invalid Password",
                "The password you entered is incorrect.\n\nWould you like to try again?"
            )
            root.destroy()

        return result
