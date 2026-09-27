import shutil


def drive_summary(path):
    try:
        usage = shutil.disk_usage(path)
        return usage.total, usage.used, usage.free
    except OSError:
        return 0, 0, 0
