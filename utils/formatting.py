import os


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def human_size(value):
    value = float(value or 0)
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024


def shorten_path(path, max_len=70):
    if len(path) <= max_len:
        return path
    keep = max_len - 3
    left = keep // 2
    right = keep - left
    return path[:left] + "..." + path[-right:]


def status_label(status):
    return {
        "CLEAN": "[CLEAN]",
        "REVIEW": "[REVIEW]",
        "KEEP": "[KEEP]",
    }.get(status, f"[{status}]")


def pause():
    input("\nPress Enter to continue...")


def print_header():
    print("+--------------------------------------------------------------+")
    print("|                    CAN I DELETE IT?                          |")
    print("|          Find what's eating your Windows storage             |")
    print("+--------------------------------------------------------------+")
    print()
