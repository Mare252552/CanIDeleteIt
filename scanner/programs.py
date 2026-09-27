import os
import winreg


UNINSTALL_KEYS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]


def _read_value(key, name, default=None):
    try:
        value, _ = winreg.QueryValueEx(key, name)
        return value
    except OSError:
        return default


def scan_programs():
    found = {}

    for hive, subkey in UNINSTALL_KEYS:
        try:
            root = winreg.OpenKey(hive, subkey)
        except OSError:
            continue

        try:
            count = winreg.QueryInfoKey(root)[0]
            for i in range(count):
                try:
                    child_name = winreg.EnumKey(root, i)
                    child = winreg.OpenKey(root, child_name)
                except OSError:
                    continue

                try:
                    name = _read_value(child, "DisplayName")
                    if not name:
                        continue

                    estimated_kb = _read_value(child, "EstimatedSize", 0)
                    location = _read_value(child, "InstallLocation", "") or ""
                    uninstall = _read_value(child, "UninstallString", "") or ""

                    size = int(estimated_kb) * 1024 if isinstance(estimated_kb, int) else 0

                    if size < 100 * 1024**2:
                        continue

                    key = (name.lower(), location.lower())
                    found[key] = {
                        "name": name,
                        "install_location": location or "(not reported by installer)",
                        "path": location or "",
                        "size": size,
                        "status": "REVIEW",
                        "reason": (
                            "This is an installed Windows application. "
                            "Use Settings > Apps or the program's uninstaller instead of deleting its folder."
                        ),
                        "extra": f"Uninstall command: {uninstall}" if uninstall else "",
                    }
                finally:
                    try:
                        child.Close()
                    except Exception:
                        pass
        finally:
            root.Close()

    items = list(found.values())
    items.sort(key=lambda x: x["size"], reverse=True)
    return items
