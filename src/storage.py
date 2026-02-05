import json
import time
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional

from .encryption import EncryptionManager


@dataclass
class Keybind:

    id: str
    hotkey: str
    name: str
    action_type: str

    username: str = ""
    password: str = ""
    custom_text: str = ""

    program_path: str = ""
    program_args: str = ""
    wait_seconds: float = 2.0

    created_at: float = 0.0

    @classmethod
    def create_new(
        cls,
        hotkey: str,
        name: str,
        action_type: str,
        username: str = "",
        password: str = "",
        custom_text: str = "",
        program_path: str = "",
        program_args: str = "",
        wait_seconds: float = 2.0
    ) -> "Keybind":
        return cls(
            id=str(uuid.uuid4()),
            hotkey=hotkey,
            name=name,
            action_type=action_type,
            username=username,
            password=password,
            custom_text=custom_text,
            program_path=program_path,
            program_args=program_args,
            wait_seconds=wait_seconds,
            created_at=time.time()
        )


class KeybindStore:

    STORE_VERSION = 1

    def __init__(self, encryption: EncryptionManager, data_dir: Path):
        self.encryption = encryption
        self.data_path = data_dir / "keybinds.enc"
        self.keybinds: Dict[str, Keybind] = {}

    def load(self) -> bool:
        if not self.data_path.exists():
            return False

        encrypted_data = self.data_path.read_bytes()
        json_str = self.encryption.decrypt(encrypted_data)
        data = json.loads(json_str)

        self.keybinds = {
            kb['id']: Keybind(**kb) for kb in data.get('keybinds', [])
        }
        return True

    def save(self) -> None:
        data = {
            'version': self.STORE_VERSION,
            'keybinds': [asdict(kb) for kb in self.keybinds.values()]
        }
        json_str = json.dumps(data, indent=2)
        encrypted_data = self.encryption.encrypt(json_str)

        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_path.write_bytes(encrypted_data)

    def add(self, keybind: Keybind) -> None:
        self.keybinds[keybind.id] = keybind
        self.save()

    def update(self, keybind: Keybind) -> None:
        if keybind.id not in self.keybinds:
            raise KeyError(f"Keybind with id {keybind.id} not found")
        self.keybinds[keybind.id] = keybind
        self.save()

    def remove(self, keybind_id: str) -> None:
        if keybind_id in self.keybinds:
            del self.keybinds[keybind_id]
            self.save()

    def get(self, keybind_id: str) -> Optional[Keybind]:
        return self.keybinds.get(keybind_id)

    def get_all(self) -> List[Keybind]:
        return list(self.keybinds.values())

    def get_by_hotkey(self, hotkey: str) -> Optional[Keybind]:
        for kb in self.keybinds.values():
            if kb.hotkey.lower() == hotkey.lower():
                return kb
        return None

    def hotkey_exists(self, hotkey: str, exclude_id: Optional[str] = None) -> bool:
        for kb in self.keybinds.values():
            if kb.hotkey.lower() == hotkey.lower():
                if exclude_id is None or kb.id != exclude_id:
                    return True
        return False

    def exists(self) -> bool:
        return self.data_path.exists()
