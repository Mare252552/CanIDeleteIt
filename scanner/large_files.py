import heapq
import os
from pathlib import Path

from analyzer.classifier import classify_path


SKIP_DIR_NAMES = {
    "$recycle.bin",
    "system volume information",
}

MAX_RESULTS = 500


def scan_large_files(root, min_size_bytes):
    root = os.path.abspath(root)
    heap = []

    def onerror(_err):
        pass

    for current, dirs, names in os.walk(root, topdown=True, onerror=onerror, followlinks=False):
        dirs[:] = [
            d for d in dirs
            if d.lower() not in SKIP_DIR_NAMES
        ]

        for name in names:
            path = Path(current) / name

            try:
                if path.is_symlink():
                    continue
                size = path.stat().st_size
            except (PermissionError, FileNotFoundError, OSError):
                continue

            if size < min_size_bytes:
                continue

            status, reason = classify_path(path)

            item = {
                "path": str(path),
                "size": size,
                "status": status,
                "reason": reason,
            }

            if len(heap) < MAX_RESULTS:
                heapq.heappush(heap, (size, str(path), item))
            elif size > heap[0][0]:
                heapq.heapreplace(heap, (size, str(path), item))

    items = [entry[2] for entry in heap]
    items.sort(key=lambda x: x["size"], reverse=True)
    return items
