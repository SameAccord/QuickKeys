import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional, List

import customtkinter as ctk

from ..storage import Keybind, KeybindStore
from ..hotkeys import HotkeyManager
from . import theme


class _KeybindCard(ctk.CTkFrame):

    def __init__(self, master, keybind: Keybind, action_label: str,
                 on_select: Callable, on_double_click: Callable, **kwargs):
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            corner_radius=theme.CORNER_RADIUS,
            height=56,
            **kwargs,
        )
        self.keybind = keybind
        self._on_select = on_select
        self._on_double_click = on_double_click
        self._selected = False

        self.pack_propagate(False)

        self.badge = ctk.CTkLabel(
            self,
            text=keybind.hotkey,
            font=theme.FONT_BADGE,
            text_color=theme.TEXT_PRIMARY,
            fg_color=theme.ACCENT,
            corner_radius=6,
            width=0,
            padx=10,
            pady=2,
        )
        self.badge.pack(side="left", padx=(theme.PAD_SM, theme.PAD_SM))

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, pady=6)

        self.name_label = ctk.CTkLabel(
            text_frame,
            text=keybind.name,
            font=theme.FONT_BODY,
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
        )
        self.name_label.pack(anchor="w")

        self.type_label = ctk.CTkLabel(
            text_frame,
            text=action_label,
            font=theme.FONT_TINY,
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        self.type_label.pack(anchor="w")

        for widget in (self, self.badge, text_frame, self.name_label, self.type_label):
            widget.bind("<Button-1>", self._handle_click)
            widget.bind("<Double-Button-1>", self._handle_dblclick)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def set_selected(self, selected: bool):
        self._selected = selected
        color = theme.SURFACE_SELECT if selected else theme.SURFACE
        self.configure(fg_color=color)

    def _on_enter(self, event):
        if not self._selected:
            self.configure(fg_color=theme.SURFACE_HOVER)

    def _on_leave(self, event):
        if not self._selected:
            self.configure(fg_color=theme.SURFACE)

    def _handle_click(self, event):
        self._on_select(self)

    def _handle_dblclick(self, event):
        self._on_select(self)
        self._on_double_click(self)


class ConfigWindow:

    ACTION_TYPE_DISPLAY = {
        'paste': 'Paste',
        'launch': 'Launch',
        'launch_paste': 'Launch + Paste',
    }

    def __init__(
        self,
        parent,
        store: KeybindStore,
        hotkey_manager: HotkeyManager,
        on_keybinds_changed: Optional[Callable] = None,
    ):
        self.parent = parent
        self.store = store
        self.hotkey_manager = hotkey_manager
        self.on_keybinds_changed = on_keybinds_changed
        self.root: Optional[ctk.CTkToplevel] = None

        self._sort_column: Optional[str] = None
        self._sort_cycle: int = 0

        self._cards: List[_KeybindCard] = []
        self._selected_card: Optional[_KeybindCard] = None

    def show(self):
        if self.root is not None:
            try:
                self.root.lift()
                self.root.focus_force()
                return
            except tk.TclError:
                self.root = None

        self.root = ctk.CTkToplevel(self.parent)
        self.root.title("QuickKeys - Configure Keybinds")
        self.root.geometry("600x460")
        self.root.minsize(500, 360)
        self.root.configure(fg_color=theme.BG_DARK)

        theme.set_window_icon(self.root)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 600) // 2
        y = (self.root.winfo_screenheight() - 460) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._refresh_list()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=theme.BG_DARK)
        main_frame.pack(fill="both", expand=True, padx=theme.PAD, pady=theme.PAD)

        header_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, theme.PAD_SM))

        ctk.CTkLabel(
            header_row,
            text="Keybinds",
            font=theme.FONT_TITLE,
            text_color=theme.TEXT_PRIMARY,
        ).pack(side="left")

        sort_frame = ctk.CTkFrame(header_row, fg_color="transparent")
        sort_frame.pack(side="right")

        ctk.CTkLabel(
            sort_frame,
            text="Sort:",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_SECONDARY,
        ).pack(side="left", padx=(0, 4))

        self.sort_menu = ctk.CTkOptionMenu(
            sort_frame,
            values=["Created", "Hotkey", "Name", "Type"],
            command=self._on_sort_changed,
            width=110,
            height=28,
            font=theme.FONT_SMALL,
            fg_color=theme.SURFACE,
            button_color=theme.ACCENT,
            button_hover_color=theme.ACCENT_HOVER,
            dropdown_fg_color=theme.SURFACE,
            dropdown_hover_color=theme.SURFACE_HOVER,
            dropdown_text_color=theme.TEXT_PRIMARY,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.BUTTON_RADIUS,
        )
        self.sort_menu.set("Created")
        self.sort_menu.pack(side="left")

        self.list_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=theme.BG_DARK,
            corner_radius=theme.CORNER_RADIUS,
            scrollbar_button_color=theme.SURFACE,
            scrollbar_button_hover_color=theme.SURFACE_HOVER,
        )
        self.list_frame.pack(fill="both", expand=True)

        self.empty_label = ctk.CTkLabel(
            self.list_frame,
            text="No keybinds configured.\nClick Add to create one.",
            font=theme.FONT_BODY,
            text_color=theme.TEXT_MUTED,
        )

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(theme.PAD, 0))

        add_btn = ctk.CTkButton(
            btn_frame, text="Add",
            command=self._on_add,
            **theme.accent_button_kwargs(),
            width=80,
        )
        add_btn.pack(side="left")

        edit_btn = ctk.CTkButton(
            btn_frame, text="Edit",
            command=self._on_edit,
            **theme.secondary_button_kwargs(),
            width=80,
        )
        edit_btn.pack(side="left", padx=(theme.PAD_SM, 0))

        remove_btn = ctk.CTkButton(
            btn_frame, text="Remove",
            command=self._on_remove,
            **theme.danger_button_kwargs(),
            width=80,
        )
        remove_btn.pack(side="left", padx=(theme.PAD_SM, 0))

        close_btn = ctk.CTkButton(
            btn_frame, text="Close",
            command=self._on_close,
            **theme.secondary_button_kwargs(),
            width=80,
        )
        close_btn.pack(side="right")

    def _refresh_list(self):
        for card in self._cards:
            card.destroy()
        self._cards.clear()
        self._selected_card = None

        keybinds = self._get_sorted_keybinds()

        if not keybinds:
            self.empty_label.pack(pady=40)
        else:
            self.empty_label.pack_forget()
            for kb in keybinds:
                action_display = self.ACTION_TYPE_DISPLAY.get(kb.action_type, kb.action_type)
                card = _KeybindCard(
                    self.list_frame,
                    keybind=kb,
                    action_label=action_display,
                    on_select=self._on_card_select,
                    on_double_click=self._on_card_dblclick,
                )
                card.pack(fill="x", pady=(0, theme.PAD_SM))
                self._cards.append(card)

    def _on_card_select(self, card: _KeybindCard):
        if self._selected_card and self._selected_card is not card:
            self._selected_card.set_selected(False)
        card.set_selected(True)
        self._selected_card = card

    def _on_card_dblclick(self, card: _KeybindCard):
        self._on_edit()

    _SORT_MAP = {
        "Created": None,
        "Hotkey": "hotkey",
        "Name": "name",
        "Type": "type",
    }

    def _on_sort_changed(self, value: str):
        col = self._SORT_MAP.get(value)
        if col == self._sort_column:
            self._sort_cycle = (self._sort_cycle + 1) % 2
        else:
            self._sort_column = col
            self._sort_cycle = 0
        self._refresh_list()

    def _get_sorted_keybinds(self):
        keybinds = self.store.get_all()

        if self._sort_column is None:
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

    def _get_selected_keybind(self) -> Optional[Keybind]:
        if self._selected_card is None:
            return None
        return self._selected_card.keybind

    def _on_add(self):
        from .keybind_editor import KeybindEditorDialog

        dialog = KeybindEditorDialog(
            self.root,
            self.store,
            self.hotkey_manager,
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
            keybind=keybind,
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
            f"Hotkey: {keybind.hotkey}",
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
