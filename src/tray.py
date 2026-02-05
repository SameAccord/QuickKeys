import threading
from pathlib import Path
from typing import Callable, Optional

from PIL import Image
import pystray

from .config import get_icon_path, get_png_icon_path


class SystemTray:

    def __init__(
        self,
        on_configure: Callable,
        on_quit: Callable,
        on_lock: Optional[Callable] = None
    ):
        self.on_configure = on_configure
        self.on_quit = on_quit
        self.on_lock = on_lock
        self.icon: Optional[pystray.Icon] = None
        self._stop_event = threading.Event()

    def _create_default_icon(self) -> Image.Image:
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))

        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)

        draw.ellipse([4, 4, 60, 60], fill=(52, 152, 219))

        draw.ellipse([16, 16, 48, 48], outline='white', width=4)
        draw.line([36, 40, 52, 56], fill='white', width=4)

        return image

    def _load_icon(self) -> Image.Image:
        png_path = get_png_icon_path()
        if png_path and png_path.exists():
            try:
                img = Image.open(png_path)
                img = img.convert('RGBA')
                img = img.resize((64, 64), Image.LANCZOS)
                return img
            except Exception:
                pass

        icon_path = get_icon_path()
        if icon_path and icon_path.exists():
            try:
                img = Image.open(icon_path)
                img = img.convert('RGBA')
                return img
            except Exception:
                pass

        return self._create_default_icon()

    def _create_menu(self) -> pystray.Menu:
        items = [
            pystray.MenuItem("Configure Keybinds", self._on_configure),
        ]

        if self.on_lock:
            items.append(pystray.MenuItem("Lock", self._on_lock))

        items.extend([
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit)
        ])

        return pystray.Menu(*items)

    def _on_configure(self, icon, item):
        self.on_configure()

    def _on_lock(self, icon, item):
        if self.on_lock:
            self.on_lock()

    def _on_quit(self, icon, item):
        self.stop()
        self.on_quit()

    def run(self):
        image = self._load_icon()
        menu = self._create_menu()

        self.icon = pystray.Icon(
            name="QuickKeys",
            icon=image,
            title="QuickKeys",
            menu=menu
        )

        self.icon.run()

    def run_detached(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def stop(self):
        self._stop_event.set()
        if self.icon:
            self.icon.stop()
            self.icon = None

    def update_title(self, title: str):
        if self.icon:
            self.icon.title = title

    def notify(self, title: str, message: str):
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception:
                pass
