import os
import sys
from pathlib import Path

from scanner.large_files import scan_large_files
from scanner.junk_files import scan_junk
from scanner.games import scan_games
from scanner.programs import scan_programs
from analyzer.classifier import classify_path
from utils.disk import drive_summary
from utils.formatting import (
    clear,
    human_size,
    pause,
    print_header,
    status_label,
    shorten_path,
)
from utils.recycle_bin import move_to_recycle_bin


def get_default_drive():
    drive = os.environ.get("SystemDrive", "C:")
    return drive + "\\"


def ask_path(prompt, default):
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default


def ask_number(prompt, default, minimum=None):
    raw = input(f"{prompt} [{default}]: ").strip()
    if not raw:
        return default
    try:
        value = float(raw)
        if minimum is not None and value < minimum:
            return default
        return value
    except ValueError:
        return default


def show_items(items, title, allow_actions=True):
    clear()
    print_header()
    print(title)
    print("=" * 96)

    if not items:
        print("\nNothing found.")
        pause()
        return

    max_show = min(len(items), 50)

    for i, item in enumerate(items[:max_show], start=1):
        path = item.get("path") or item.get("install_location") or item.get("name", "")
        size = item.get("size", 0)

        if "status" in item:
            status = item["status"]
            reason = item.get("reason", "")
        else:
            status, reason = classify_path(Path(path)) if path else ("REVIEW", "Review manually.")

        item["_status"] = status
        item["_reason"] = reason

        print(
            f"{i:>2}. {human_size(size):>10}  "
            f"{status_label(status):<10}  "
            f"{shorten_path(str(path), 68)}"
        )

    if len(items) > max_show:
        print(f"\nShowing top {max_show} of {len(items)} results.")

    if not allow_actions:
        pause()
        return

    print("\nEnter a number for details, or B to go back.")
    while True:
        choice = input("> ").strip().lower()
        if choice in {"b", "back", "q"}:
            return
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < max_show:
                item_details(items[idx])
                return show_items(items, title, allow_actions=True)
        print("Invalid choice.")


def item_details(item):
    clear()
    print_header()

    path = item.get("path") or item.get("install_location")
    display_name = item.get("name") or (Path(path).name if path else "Unknown")
    size = item.get("size", 0)
    status = item.get("_status") or item.get("status")
    reason = item.get("_reason") or item.get("reason")

    if not status:
        status, reason = classify_path(Path(path))

    print(display_name)
    print("=" * 72)
    print(f"Path:   {path}")
    print(f"Size:   {human_size(size)}")
    print(f"Status: {status_label(status)}")
    print()
    print("Why?")
    print(reason or "No explanation available.")

    extra = item.get("extra")
    if extra:
        print()
        print(extra)

    print()
    print("[O] Open location")
    if status != "KEEP" and path:
        print("[D] Move to Recycle Bin")
    else:
        print("[D] Delete disabled for KEEP items")
    print("[B] Back")

    while True:
        choice = input("> ").strip().lower()

        if choice == "b":
            return

        if choice == "o" and path:
            try:
                target = Path(path)
                folder = target if target.is_dir() else target.parent
                os.startfile(str(folder))
            except Exception as exc:
                print(f"Could not open location: {exc}")
                pause()
                return

        if choice == "d":
            if status == "KEEP":
                print("Blocked: this item is marked KEEP.")
                pause()
                return

            print()
            print("This moves the selected item to the Recycle Bin.")
            print("It does NOT permanently erase it.")
            confirm = input(f'Type DELETE to move "{display_name}" to Recycle Bin: ').strip()

            if confirm != "DELETE":
                print("Cancelled.")
                pause()
                return

            ok, message = move_to_recycle_bin(path)
            print(message)
            pause()
            return


def large_files_menu():
    root = ask_path("Scan path", get_default_drive())
    min_gb = ask_number("Minimum file size in GB", 1.0, 0.01)

    clear()
    print_header()
    print(f"Scanning {root} for files >= {min_gb:g} GB...")
    print("Press Ctrl+C to cancel.\n")

    try:
        items = scan_large_files(root, int(min_gb * 1024**3))
    except KeyboardInterrupt:
        print("\nScan cancelled.")
        pause()
        return

    show_items(items, f"LARGEST FILES - {root}")


def junk_menu():
    clear()
    print_header()
    print("Scanning known cache/temp/build locations...")
    try:
        items = scan_junk()
    except KeyboardInterrupt:
        print("\nScan cancelled.")
        pause()
        return
    show_items(items, "UNNECESSARY / REGENERATABLE DATA")


def games_menu():
    clear()
    print_header()
    print("Looking for common game libraries...")
    try:
        items = scan_games()
    except KeyboardInterrupt:
        print("\nScan cancelled.")
        pause()
        return
    show_items(items, "LARGE GAMES")


def programs_menu():
    clear()
    print_header()
    print("Reading installed apps from Windows...")
    items = scan_programs()
    show_items(items, "LARGE INSTALLED PROGRAMS")


def full_scan():
    root = ask_path("Scan path", get_default_drive())
    min_gb = ask_number("Minimum large-file size in GB", 1.0, 0.01)

    clear()
    print_header()
    print("FULL STORAGE SCAN")
    print("This can take a while. Press Ctrl+C to cancel.\n")

    try:
        large = scan_large_files(root, int(min_gb * 1024**3))
        junk = scan_junk()
        games = scan_games()
        programs = scan_programs()
    except KeyboardInterrupt:
        print("\nScan cancelled.")
        pause()
        return

    while True:
        clear()
        print_header()
        print("FULL SCAN COMPLETE")
        print("=" * 72)
        print(f"[1] Largest files      {len(large)} found")
        print(f"[2] Junk/cache         {len(junk)} found")
        print(f"[3] Games              {len(games)} found")
        print(f"[4] Programs           {len(programs)} found")
        print("[B] Back")

        c = input("> ").strip().lower()
        if c == "1":
            show_items(large, "LARGEST FILES")
        elif c == "2":
            show_items(junk, "UNNECESSARY / REGENERATABLE DATA")
        elif c == "3":
            show_items(games, "LARGE GAMES")
        elif c == "4":
            show_items(programs, "LARGE INSTALLED PROGRAMS")
        elif c == "b":
            return


def main():
    while True:
        clear()
        print_header()

        total, used, free = drive_summary(get_default_drive())
        if total:
            percent = used / total * 100
            print(
                f"{get_default_drive()}  "
                f"{human_size(used)} used / {human_size(total)} total  "
                f"({percent:.1f}% full) | {human_size(free)} free"
            )

        print()
        print("What do you want to find?")
        print()
        print("[1] Largest files")
        print("    Find huge files anywhere on a drive/folder")
        print()
        print("[2] Unnecessary files")
        print("    Known cache, temp and generated build data")
        print()
        print("[3] Large games")
        print("    Scan common Steam/Epic/game library locations")
        print()
        print("[4] Large programs")
        print("    Show large installed Windows applications")
        print()
        print("[5] Full storage scan")
        print()
        print("[Q] Exit")
        print()

        choice = input("> ").strip().lower()

        if choice == "1":
            large_files_menu()
        elif choice == "2":
            junk_menu()
        elif choice == "3":
            games_menu()
        elif choice == "4":
            programs_menu()
        elif choice == "5":
            full_scan()
        elif choice in {"q", "quit", "exit"}:
            return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye.")
