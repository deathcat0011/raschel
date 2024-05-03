from codecs import utf_8_decode
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


def run_backup(paths_to_backup: list[PathLike[str]], target_dir: PathLike[str]) -> str:

    if not isinstance(paths_to_backup, list):  # type: ignore
        log.warning(
            "Input was expected to be a list, put was single string, assuming you meant to only pass one string."
        )
        paths_to_backup = [paths_to_backup]

    os.makedirs(target_dir, exist_ok=True)
    failed = False
    failed_list: list[tuple[str, str]] = []
    timestamp = datetime.datetime.now()
    time = timestamp.isoformat("_", "seconds").replace("-", "_").replace(":", "_")
    written: dict[Any, Any] = dict()
    out_path = f"{target_dir}/backup_{time}.zip"
    with zip.ZipFile(
        out_path,
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
    return out_path


def compare_with_backup(backup_path: PathLike[str] | str, dir_path: PathLike[str]):
    backup_files: list[dict[str, Any]] = []
    original_files: list[str] = []
    if not str(backup_path).endswith(".zip"):
        backup_path += ".zip"  # type: ignore
    with zip.ZipFile(backup_path) as file:  # type: ignore
        data = file.read(
            "meta.info",
        )
        data, _ = utf_8_decode(data)
        meta: dict[Any, Any] = json.loads(data)
        # print(meta)
        for _, value in meta.items():
            for v in value:
                backup_files.extend([{"original_path": k, **v} for k, v in v.items()])
        # print(backup_files)

        for file_dir, _, files in os.walk(
            path.abspath(dir_path),
        ):
            for file in files:
                original_files.append(path.abspath(path.join(file_dir, file)))

    for d in backup_files:
        if (file := d["original_path"]) in original_files:
            if d["hash"] == (hash := file_util.get_file_hash(file)):
                print(f"'{file}' unchanged {hash}")
            else:
                print(f"'{file}' has changed")
