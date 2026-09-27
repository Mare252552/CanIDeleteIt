import os
from pathlib import Path

from analyzer.classifier import CLEAN_REASONS


def _folder_size(path):
    total = 0
    for current, dirs, files in os.walk(path, topdown=True, followlinks=False):
        for name in files:
            p = Path(current) / name
            try:
                if not p.is_symlink():
                    total += p.stat().st_size
            except (OSError, PermissionError, FileNotFoundError):
                pass
    return total


def _known_locations():
    user = Path.home()
    local = Path(os.environ.get("LOCALAPPDATA", user / "AppData/Local"))
    roaming = Path(os.environ.get("APPDATA", user / "AppData/Roaming"))
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))

    candidates = [
        (Path(os.environ.get("TEMP", local / "Temp")), "Temporary files"),
        (local / "Temp", "Temporary files"),
        (windir / "Temp", "Windows temporary files"),
        (local / "pip" / "Cache", "pip package cache"),
        (local / "npm-cache", "npm cache"),
        (roaming / "npm-cache", "npm cache"),
        (local / "UnrealEngine" / "Common" / "DerivedDataCache", "Unreal Engine Derived Data Cache"),
    ]

    # Common project-level generated folders under Desktop/Documents
    search_roots = [user / "Desktop", user / "Documents"]
    generated_names = {
        "DerivedDataCache": "Unreal Engine Derived Data Cache",
        "Intermediate": "Generated build data",
        ".vs": "Visual Studio project cache",
    }

    for base in search_roots:
        if not base.exists():
            continue
        try:
            for current, dirs, _files in os.walk(base, topdown=True, followlinks=False):
                depth = len(Path(current).relative_to(base).parts)
                if depth > 4:
                    dirs[:] = []
                    continue
                for d in list(dirs):
                    if d in generated_names:
                        candidates.append((Path(current) / d, generated_names[d]))
                        dirs.remove(d)
        except Exception:
            pass

    # Remove duplicates
    seen = set()
    out = []
    for path, label in candidates:
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append((path, label))

    return out


def scan_junk():
    items = []

    for path, label in _known_locations():
        if not path.exists():
            continue

        try:
            size = _folder_size(path)
        except Exception:
            continue

        if size < 50 * 1024**2:
            continue

        items.append({
            "path": str(path),
            "size": size,
            "status": "CLEAN",
            "reason": (
                f"{label}. This location is used for temporary, cache, "
                "or generated data and can normally be recreated. "
                "Close related apps before cleaning it."
            ),
            "extra": "Tip: deleting caches can make the next launch/build slower while files are rebuilt.",
        })

    items.sort(key=lambda x: x["size"], reverse=True)
    return items
