import customtkinter as ctk

BG_DARK        = "#0f0f1a"
SURFACE        = "#1a1a2e"
SURFACE_HOVER  = "#252540"
SURFACE_SELECT = "#4a2c6e"

INPUT_BG       = "#252540"
BORDER         = "#1a1a3d"

TEXT_PRIMARY   = "#e8e8f0"
TEXT_SECONDARY = "#9999b3"
TEXT_MUTED     = "#6a6a8a"

ACCENT         = "#e91e8c"
ACCENT_HOVER   = "#ff6eb4"
ACCENT_PRESS   = "#4a2c6e"

DANGER         = "#C72437"
DANGER_HOVER   = "#A11D2C"

FONT_FAMILY    = "Segoe UI"
FONT_TITLE     = (FONT_FAMILY, 18, "bold")
FONT_HEADING   = (FONT_FAMILY, 14, "bold")
FONT_BODY      = (FONT_FAMILY, 13)
FONT_SMALL     = (FONT_FAMILY, 11)
FONT_TINY      = (FONT_FAMILY, 10)
FONT_BADGE     = (FONT_FAMILY, 11, "bold")

CORNER_RADIUS  = 10
BUTTON_RADIUS  = 8
ENTRY_HEIGHT   = 36
BUTTON_HEIGHT  = 34
PAD            = 16
PAD_SM         = 8


def configure_appearance():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def accent_button_kwargs() -> dict:
    return dict(
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        text_color=TEXT_PRIMARY,
        corner_radius=BUTTON_RADIUS,
        height=BUTTON_HEIGHT,
        font=FONT_BODY,
    )


def secondary_button_kwargs() -> dict:
    return dict(
        fg_color=SURFACE,
        hover_color=SURFACE_HOVER,
        text_color=TEXT_PRIMARY,
        border_color=BORDER,
        border_width=1,
        corner_radius=BUTTON_RADIUS,
        height=BUTTON_HEIGHT,
        font=FONT_BODY,
    )


def danger_button_kwargs() -> dict:
    return dict(
        fg_color=DANGER,
        hover_color=DANGER_HOVER,
        text_color=TEXT_PRIMARY,
        corner_radius=BUTTON_RADIUS,
        height=BUTTON_HEIGHT,
        font=FONT_BODY,
    )


def entry_kwargs() -> dict:
    return dict(
        fg_color=INPUT_BG,
        border_color=BORDER,
        text_color=TEXT_PRIMARY,
        corner_radius=BUTTON_RADIUS,
        height=ENTRY_HEIGHT,
        font=FONT_BODY,
    )


def set_window_icon(window) -> None:
    from ..config import get_icon_path, get_png_icon_path

    def _apply():
        ico_path = get_icon_path()
        if ico_path:
            try:
                window.iconbitmap(str(ico_path))
                return
            except Exception:
                pass

        png_path = get_png_icon_path()
        if png_path:
            try:
                from PIL import Image, ImageTk
                img = Image.open(png_path)
                photo = ImageTk.PhotoImage(img)
                window.iconphoto(True, photo)
                window._icon_photo = photo
            except Exception:
                pass

    window.after(150, _apply)
