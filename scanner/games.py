import os
from pathlib import Path


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


def _candidate_roots():
    roots = []

    pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    pfx86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))

    roots.extend([
        pfx86 / "Steam" / "steamapps" / "common",
        pf / "Steam" / "steamapps" / "common",
        pf / "Epic Games",
        Path(r"C:\XboxGames"),
        Path(r"C:\Games"),
    ])

    # Detect additional Steam libraries from libraryfolders.vdf
    steam_vdf_paths = [
        pfx86 / "Steam" / "steamapps" / "libraryfolders.vdf",
        pf / "Steam" / "steamapps" / "libraryfolders.vdf",
    ]

    for vdf in steam_vdf_paths:
        if not vdf.exists():
            continue
        try:
            text = vdf.read_text(encoding="utf-8", errors="ignore")
            for line in text.splitlines():
                if '"path"' in line.lower():
                    parts = line.split('"')
                    if len(parts) >= 4:
                        lib = Path(parts[3].replace("\\\\", "\\"))
                        roots.append(lib / "steamapps" / "common")
        except OSError:
            pass

    # Deduplicate
    out, seen = [], set()
    for p in roots:
        key = str(p).lower()
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def scan_games():
    items = []

    for root in _candidate_roots():
        if not root.exists() or not root.is_dir():
            continue

        try:
            children = list(root.iterdir())
        except OSError:
            continue

        for child in children:
            if not child.is_dir():
                continue

            try:
                size = _folder_size(child)
            except Exception:
                continue

            if size < 512 * 1024**2:
                continue

            items.append({
                "name": child.name,
                "path": str(child),
                "size": size,
                "status": "REVIEW",
                "reason": (
                    "This looks like an installed game folder. "
                    "Do not delete it manually if the game is still installed; "
                    "use Steam/Epic/Xbox/its launcher to uninstall it cleanly."
                ),
                "extra": "Manual deletion can leave launcher entries, saves, mods, or registry data behind.",
            })

    items.sort(key=lambda x: x["size"], reverse=True)
    return items
