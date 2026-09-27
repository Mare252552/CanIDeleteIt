# CanIDeleteIt

A Windows command-line storage analyzer that finds large files, cache/build data, games and installed programs — then explains whether each item is likely safe to remove.

> **Important:** `CLEAN` means the path matches a known cache/temp/generated-data rule. Personal files are never marked automatically safe. `KEEP` items cannot be deleted from the app.

## Features

- Find the largest files on a drive or folder
- Find known temp/cache/generated build folders
- Find games in common Steam/Epic/Xbox locations
- Read large installed applications from the Windows registry
- Explain `CLEAN`, `REVIEW`, and `KEEP`
- Move non-KEEP items to the Windows Recycle Bin
- Full-storage scan menu

## Quick start

1. Download the repository as ZIP and extract it.
2. Install Python 3.10+ and make sure **Add Python to PATH** is enabled.
3. Open the extracted folder.
4. Run:

```cmd
setup
```

5. Then run:

```cmd
canidelete
```

You can also double-click `setup.bat` once and `canidelete.bat` whenever you want to launch it.

## Status meanings

- `CLEAN` — known cache/temp/generated data that can normally be recreated.
- `REVIEW` — may be deletable, but could contain something you need.
- `KEEP` — Windows/system/program location; deletion from the app is blocked.

## Safety

CanIDeleteIt intentionally uses conservative rules. It does **not** claim that every large file is safe to delete. Items marked `REVIEW` require your judgment.

Deletion uses the Windows **Recycle Bin** through `Send2Trash`; it does not permanently erase files.

## Current limitations

- Game discovery is based on common library locations.
- Installed-program sizes depend on what the installer reports to Windows.
- Scanning an entire drive can take time.
- Some protected folders may be skipped because Windows denies access.

## License

MIT
