def move_to_recycle_bin(path):
    try:
        from send2trash import send2trash
    except ImportError:
        return (
            False,
            "Send2Trash is not installed. Run setup.bat first."
        )

    try:
        send2trash(path)
        return True, "Moved to Recycle Bin."
    except Exception as exc:
        return False, f"Could not move item to Recycle Bin: {exc}"
