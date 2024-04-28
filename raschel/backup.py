import datetime
import json
import logging as log
import os
import re as re
import zipfile as zip
from os import PathLike, path
from typing import Any, Optional

from raschel import file_util


def to_zip_path(p: str) -> Optional[str]:
    """
    We want to keep the path information of a file tied to its location in the original file system, so we have to remove the drive letters. returns None if the path was invalid
    """
    if path.isabs(p):
        (drive, p) = path.splitdrive(p)
        drive = drive.replace(":", "").lower()
        if not drive:
            return None
        # now join the lower case drive letter with the rest of the path
        return path.normpath(f"{drive}/{p}")
    return p


def run_backup(paths_to_backup: list[PathLike[str]], target_dir: PathLike[str]):

    os.makedirs(target_dir, exist_ok=True)
    failed = False
    failed_list: list[tuple[str, str]] = []
    timestamp = datetime.datetime.now()
    time = timestamp.isoformat("_", "seconds").replace("-", "_").replace(":", "_")
    written: dict[Any, Any] = dict()
    with zip.ZipFile(
        f"{target_dir}/backup_{time}.zip",
        "a",
        compression=zip.ZIP_DEFLATED,
        compresslevel=9,
    ) as zipfile:
        # now recursively go through the paths
        for dir in paths_to_backup:
            for file_dir, _, files in os.walk(
                path.abspath(dir),
            ):
                if (archive_dir := to_zip_path(file_dir)) is None:
                    log.error(f"Invalid path '{dir}'")
                    continue
                for file in files:
                    log.info(f"{file}")
                    filename = path.join(file_dir, file)
                    arcname = path.join(archive_dir, file)
                    try:
                        zipfile.write(
                            filename,
                            arcname,
                            compress_type=zip.ZIP_DEFLATED,
                            compresslevel=9,
                        )
                        value = {
                            filename: {
                                "archive_name": arcname,
                                "hash": file_util.get_file_hash(filename),
                                "timestamp": timestamp.isoformat(),
                            }
                        }
                        key = path.normpath(dir)
                        if key in written.keys():
                            written[key].append(value)  # type: ignore
                        else:
                            written[key] = [value]
                    except Exception as e:
                        failed = True
                        failed_list.append((filename, arcname))
                        log.error(e)
        zipfile.writestr("meta.info", json.dumps(written, indent=4))
    if failed:
        log.error("Backup unsuccesful!")
        for f, t in failed_list:
            log.error(f"Could not write '{f}' to '{t}'")
