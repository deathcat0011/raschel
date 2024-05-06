from codecs import utf_8_decode
import datetime
import json
import logging as log
import os
from pathlib import Path
import re as re
import zipfile as zip
from os import PathLike, path
from typing import Any, Optional

from raschel import file_util
from raschel.diff import diff_text1


def to_zip_path(p: str | Path) -> Optional[Path]:
    """
    We want to keep the path information of a file tied to its location in the original file system, so we have to remove the drive letters. returns None if the path was invalid
    """
    if path.isabs(p):
        (drive, p) = path.splitdrive(p)
        drive = drive.replace(":", "").lower()
        if not drive:
            return None
        # now join the lower case drive letter with the rest of the path
        return Path(path.normpath(f"{drive}/{p}"))
    return Path(p)


def run_backup(
    paths_to_backup: list[PathLike[str]], target_dir: PathLike[str]
) -> str | None:
    """
    Returns:
        The name of the archive zip file or `None` if the backup was unsuccesfull
    """
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
    meta_file_info: dict[Any, Any] = dict()
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
                archive_dir = archive_dir.as_posix()
                for file in files:
                    log.info(f"{file}")

                    filename = (Path(file_dir) / file).as_posix()
                    arcname = (Path(archive_dir) / file).as_posix()
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
                        key = Path(dir).as_posix()
                        if key in meta_file_info.keys():
                            meta_file_info[key].append(value)  # type: ignore
                        else:
                            meta_file_info[key] = [value]
                    except Exception as e:
                        failed = True
                        failed_list.append((filename, arcname))
                        log.error(e)
        """
            also store that we are making a full backup
        """
        meta_info = {"diff_backup": False, "files": meta_file_info}
        zipfile.writestr("meta.info", json.dumps(meta_info, indent=4))
    if failed:
        log.error("Backup unsuccesful!")
        for f, t in failed_list:
            log.error(f"Could not write '{f}' to '{t}'")
    return out_path


def compare_backups(
    backup_path: PathLike[str] | str, dir_path: PathLike[str]
) -> list[tuple[str, str]]:
    backup_files: list[dict[str, Any]] = []
    original_files: list[str] = []

    changed_paths: list[tuple[str, str]] = []

    if not zip.is_zipfile(backup_path):
        log.error(f"Expected '{backup_path}' to be a '.zip' file.")
        raise ValueError(f"Expected '{backup_path}' to be a '.zip' file.")

    with zip.ZipFile(backup_path) as zipfile:  # type: ignore
        data = zipfile.read(
            "meta.info",
        )
        data, _ = utf_8_decode(data)
        meta: dict[Any, Any] = json.loads(data)
        """
        Read the backed up files from the meta file in the archive
        """
        for _, value in meta["files"].items():
            for v in value:
                backup_files.extend([{"original_path": k, **v} for k, v in v.items()])

        for file_dir, _, files in os.walk(
            path.abspath(dir_path),
        ):
            for file in files:
                original_files.append((Path(file_dir) / file).as_posix())

        for d in backup_files:
            if (file := d["original_path"]) in original_files:
                if not d["hash"] == (file_util.get_file_hash(file)):
                    contents = zipfile.read(d["archive_name"])
                    diff = diff_text1(file, contents)
                    changed_paths.append((file, str(diff)))

    return changed_paths
