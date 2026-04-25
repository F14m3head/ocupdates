# Depulicates current gtfs_static.sqlite file to achrive (filename: gtfs_static_MMDD.sqlite)
# Call function: archive_gtfs()
# Checks all other archive files. If more than 3, deletes the oldest one.

from __future__ import annotations
import os
import shutil
import glob
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
ARCHUVE_DIR = os.path.join(ROOT_DIR, "./data/archive")
GTFS_FILE = os.path.join(ROOT_DIR, "./data/gtfs_static.sqlite")

def archive_gtfs() -> None:
    os.makedirs(ARCHUVE_DIR, exist_ok=True)

    # Create archive filename with current date
    date_str = datetime.datetime.now().strftime("%m%d")
    archive_filename = f"gtfs_static_{date_str}.sqlite"
    archive_path = os.path.join(ARCHUVE_DIR, archive_filename)

    # Copy current GTFS file to archive
    if os.path.exists(GTFS_FILE):
        try:
            shutil.copy2(GTFS_FILE, archive_path)
            print(f"Archived GTFS file to {archive_path}")
        except PermissionError:
            raise PermissionError("Permission error archiving GTFS file")
        except Exception as e:
            raise RuntimeError(f"Error archiving GTFS file: {e}")
    else:
        print("GTFS file does not exist. Nothing to archive.")
        return

    # Check for existing archives and delete oldest if more than 3
    archive_files = glob.glob(os.path.join(ARCHUVE_DIR, "gtfs_static_*.sqlite"))
    if len(archive_files) > 3:
        oldest_file = min(archive_files, key=os.path.getctime)
        try:
            os.remove(oldest_file)
            print(f"Deleted oldest archive: {oldest_file}")
        except PermissionError:
            raise PermissionError("Permission error deleting oldest archive")
        except Exception as e:
            raise RuntimeError(f"Error deleting oldest archive: {e}")