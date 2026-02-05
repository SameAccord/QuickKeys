import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from ..storage import Keybind, KeybindStore
from ..hotkeys import HotkeyManager
from ..config import get_icon_path


def _set_window_icon(window):
    icon_path = get_icon_path()
    if icon_path:
        try:
            window.iconbitmap(str(icon_path))
        except Exception:
            pass


class ConfigWindow:

    ACTION_TYPE_DISPLAY = {
        'paste': 'Paste',
        'launch': 'Launch',
        'launch_paste': 'Launch + Paste'
    }

    COLUMN_HEADERS = {
        'hotkey': 'Hotkey',
        'name': 'Name',
        'type': 'Action Type'
    }

    def __init__(
        self,
        store: KeybindStore,
        hotkey_manager: HotkeyManager,
        on_keybinds_changed: Optional[Callable] = None
    ):
        self.store = store
        self.hotkey_manager = hotkey_manager
        self.on_keybinds_changed = on_keybinds_changed
        self.root: Optional[tk.Toplevel] = None
        self.tree: Optional[ttk.Treeview] = None

        self._sort_column: Optional[str] = None
        self._sort_cycle: int = 0

    def show(self):
        if self.root is not None:
            try:
                self.root.lift()
                self.root.focus_force()
                return
            except tk.TclError:
                self.root = None

        self.root = tk.Toplevel()
        self.root.title("QuickKeys - Configure Keybinds")
        self.root.geometry("600x400")
        self.root.minsize(500, 300)

        _set_window_icon(self.root)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 600) // 2
        y = (self.root.winfo_screenheight() - 400) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._refresh_list()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            main_frame,
            text="Keybinds",
            font=('Segoe UI', 14, 'bold')
        )
        header.pack(anchor=tk.W, pady=(0, 10))

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ('hotkey', 'name', 'type')
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            yscrollcommand=scrollbar.set
        )

        for col in columns:
            self.tree.heading(
                col,
                text=self.COLUMN_HEADERS[col],
                command=lambda c=col: self._sort_by(c)
            )

        self.tree.column('hotkey', width=150, minwidth=100)
        self.tree.column('name', width=200, minwidth=100)
        self.tree.column('type', width=120, minwidth=80)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        self.tree.bind('<Double-1>', self._on_double_click)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        add_btn = ttk.Button(
            button_frame,
            text="Add",
            command=self._on_add
        )
        add_btn.pack(side=tk.LEFT)

        edit_btn = ttk.Button(
            button_frame,
            text="Edit",
            command=self._on_edit
        )
        edit_btn.pack(side=tk.LEFT, padx=(5, 0))

        remove_btn = ttk.Button(
            button_frame,
            text="Remove",
            command=self._on_remove
        )
        remove_btn.pack(side=tk.LEFT, padx=(5, 0))

        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=self._on_close
        )
        close_btn.pack(side=tk.RIGHT)

    def _on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            self._on_edit()

    def _sort_by(self, column: str):
        if self._sort_column == column:
            self._sort_cycle = (self._sort_cycle + 1) % 3
        else:
            self._sort_column = column
            self._sort_cycle = 0

        self._refresh_list()

    def _get_sorted_keybinds(self):
        keybinds = self.store.get_all()

        if self._sort_column is None or self._sort_cycle == 2:
            keybinds.sort(key=lambda kb: kb.created_at)
            return keybinds

        col = self._sort_column
        if col == 'hotkey':
            key_func = lambda kb: kb.hotkey.lower()
        elif col == 'name':
            key_func = lambda kb: kb.name.lower()
        elif col == 'type':
            key_func = lambda kb: self.ACTION_TYPE_DISPLAY.get(kb.action_type, kb.action_type).lower()
        else:
            return keybinds

        reverse = (self._sort_cycle == 1)
        keybinds.sort(key=key_func, reverse=reverse)
        return keybinds

    def _update_column_headers(self):
        if self.tree is None:
            return

        for col in ('hotkey', 'name', 'type'):
            header_text = self.COLUMN_HEADERS[col]

            if self._sort_column == col and self._sort_cycle != 2:
                if self._sort_cycle == 0:
                    header_text += " \u25B2"
                elif self._sort_cycle == 1:
                    header_text += " \u25BC"

            self.tree.heading(
                col,
                text=header_text,
                command=lambda c=col: self._sort_by(c)
            )

    def _refresh_list(self):
        if self.tree is None:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for kb in self._get_sorted_keybinds():
            action_display = self.ACTION_TYPE_DISPLAY.get(kb.action_type, kb.action_type)
            self.tree.insert(
                '',
                tk.END,
                iid=kb.id,
                values=(kb.hotkey, kb.name, action_display)
            )

        self._update_column_headers()

    def _get_selected_keybind(self) -> Optional[Keybind]:
        if self.tree is None:
            return None

        selection = self.tree.selection()
        if not selection:
            return None

        keybind_id = selection[0]
        return self.store.get(keybind_id)

    def _on_add(self):
        from .keybind_editor import KeybindEditorDialog

        dialog = KeybindEditorDialog(
            self.root,
            self.store,
            self.hotkey_manager
        )
        result = dialog.show()

        if result:
            self._refresh_list()
            if self.on_keybinds_changed:
                self.on_keybinds_changed()

    def _on_edit(self):
        keybind = self._get_selected_keybind()
        if keybind is None:
            messagebox.showinfo("Edit", "Please select a keybind to edit.")
            return

        from .keybind_editor import KeybindEditorDialog

        dialog = KeybindEditorDialog(
            self.root,
            self.store,
            self.hotkey_manager,
            keybind=keybind
        )
        result = dialog.show()

        if result:
            self._refresh_list()
            if self.on_keybinds_changed:
                self.on_keybinds_changed()

    def _on_remove(self):
        keybind = self._get_selected_keybind()
        if keybind is None:
            messagebox.showinfo("Remove", "Please select a keybind to remove.")
            return

        confirm = messagebox.askyesno(
            "Remove Keybind",
            f"Are you sure you want to remove '{keybind.name}'?\n\n"
            f"Hotkey: {keybind.hotkey}"
        )

        if confirm:
            self.hotkey_manager.unregister(keybind.hotkey)

            self.store.remove(keybind.id)

            self._refresh_list()
            if self.on_keybinds_changed:
                self.on_keybinds_changed()

    def _on_close(self):
        if self.root:
            self.root.destroy()
            self.root = None
