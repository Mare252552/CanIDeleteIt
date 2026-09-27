from pathlib import Path


SYSTEM_NAMES = {
    "pagefile.sys",
    "swapfile.sys",
    "hiberfil.sys",
    "bootmgr",
    "ntldr",
}

SYSTEM_PATH_PARTS = (
    r"\windows\system32",
    r"\windows\winsxs",
    r"\windows\boot",
    r"\windows\servicing",
    r"\program files",
    r"\program files (x86)",
    r"\programdata\microsoft",
)

CLEAN_PATH_PARTS = (
    r"\appdata\local\temp\\",
    r"\windows\temp\\",
    r"\deriveddatacache\\",
    r"\intermediate\\",
    r"\.vs\\",
    r"\node_modules\.cache\\",
    r"\pip\cache\\",
    r"\npm-cache\\",
)

REVIEW_EXTENSIONS = {
    ".zip": "Archive",
    ".rar": "Archive",
    ".7z": "Archive",
    ".iso": "Disk image",
    ".img": "Disk image",
    ".mp4": "Video",
    ".mkv": "Video",
    ".mov": "Video",
    ".avi": "Video",
    ".exe": "Executable / installer",
    ".msi": "Windows installer",
    ".apk": "Android application",
    ".aab": "Android App Bundle",
    ".psd": "Photoshop project",
    ".blend": "Blender project",
    ".uproject": "Unreal Engine project",
    ".godot": "Godot project",
    ".vhd": "Virtual disk",
    ".vhdx": "Virtual disk",
}
