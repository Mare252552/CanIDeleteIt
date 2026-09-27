from pathlib import Path

from .rules import (
    CLEAN_PATH_PARTS,
    REVIEW_EXTENSIONS,
    SYSTEM_NAMES,
    SYSTEM_PATH_PARTS,
)


CLEAN_REASONS = {
    "cache": "Known cache/generated location. The related app can normally recreate it.",
}


def classify_path(path: Path):
    text = str(path).lower().replace("/", "\\")
    name = path.name.lower()

    if name in SYSTEM_NAMES:
        if name == "hiberfil.sys":
            return (
                "KEEP",
                "Windows hibernation file. Do not delete it manually. "
                "If you intentionally want to remove it, Windows can do that by disabling hibernation."
            )
        return (
            "KEEP",
            "Windows manages this system file. Do not delete it manually."
        )

    if any(part in text for part in SYSTEM_PATH_PARTS):
        return (
            "KEEP",
            "This is inside a Windows or installed-program system location. "
            "Deleting files here manually can break Windows or an application."
        )

    if any(part in text for part in CLEAN_PATH_PARTS):
        return (
            "CLEAN",
            "This matches a known temporary/cache/generated-data location. "
            "It can normally be regenerated, though the next launch/build may be slower."
        )

    suffix = path.suffix.lower()
    if suffix in REVIEW_EXTENSIONS:
        file_type = REVIEW_EXTENSIONS[suffix]
        return (
            "REVIEW",
            f"{file_type} file. Windows probably does not require it, "
            "but it may contain something important to you."
        )

    # Personal folders are never auto-classified as safe
    personal_parts = (
        r"\desktop\\",
        r"\documents\\",
        r"\pictures\\",
        r"\videos\\",
        r"\downloads\\",
    )

    if any(part in text for part in personal_parts):
        return (
            "REVIEW",
            "This appears to be a personal file. Review it yourself before deleting."
        )

    return (
        "REVIEW",
        "Large file not recognized as safely removable. Review it manually before deleting."
    )
