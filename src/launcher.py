import os
import platform
import shlex
import subprocess
import time
from pathlib import Path
from typing import List, Optional


class Launcher:

    def __init__(self):
        self.system = platform.system()

    def _parse_args(self, args_string: str) -> List[str]:
        if not args_string:
            return []

        try:
            if self.system == "Windows":
                return shlex.split(args_string, posix=False)
            return shlex.split(args_string)
        except ValueError:
            return args_string.split()

    def _resolve_path(self, program_path: str) -> str:
        path = os.path.expanduser(program_path)
        path = os.path.expandvars(path)
        return path

    def launch(
        self,
        program_path: str,
        args: str = "",
        working_dir: Optional[str] = None
    ) -> Optional[subprocess.Popen]:
        try:
            resolved_path = self._resolve_path(program_path)
            parsed_args = self._parse_args(args)

            command = [resolved_path] + parsed_args

            cwd = None
            if working_dir:
                cwd = self._resolve_path(working_dir)
            elif Path(resolved_path).exists():
                cwd = str(Path(resolved_path).parent)

            kwargs = {
                'cwd': cwd,
                'stdout': subprocess.DEVNULL,
                'stderr': subprocess.DEVNULL,
            }

            if self.system == "Windows":
                kwargs['creationflags'] = (
                    subprocess.CREATE_NO_WINDOW |
                    subprocess.DETACHED_PROCESS
                )
            else:
                kwargs['start_new_session'] = True

            process = subprocess.Popen(command, **kwargs)
            return process

        except Exception as e:
            print(f"Failed to launch {program_path}: {e}")
            return None

    def launch_and_wait(
        self,
        program_path: str,
        args: str = "",
        wait_seconds: float = 2.0,
        working_dir: Optional[str] = None
    ) -> bool:
        process = self.launch(program_path, args, working_dir)

        if process is None:
            return False

        if wait_seconds > 0:
            time.sleep(wait_seconds)

        if process.poll() is not None:
            return False

        return True

    def is_valid_executable(self, program_path: str) -> bool:
        try:
            resolved = self._resolve_path(program_path)
            path = Path(resolved)

            if not path.exists():
                return False

            if self.system == "Windows":
                return path.suffix.lower() in {
                    '.exe', '.bat', '.cmd', '.com', '.msi'
                }
            else:
                return os.access(resolved, os.X_OK)

        except Exception:
            return False

    def get_executable_filter(self) -> str:
        if self.system == "Windows":
            return "Executables (*.exe;*.bat;*.cmd)|*.exe;*.bat;*.cmd|All files (*.*)|*.*"
        elif self.system == "Darwin":
            return "Applications (*.app)|*.app|All files (*.*)|*.*"
        else:
            return "All files (*.*)|*.*"
