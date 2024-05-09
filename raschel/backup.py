from codecs import utf_8_decode
import datetime
import json
import logging as log
import os
from pathlib import Path
import re as re
import uuid
import zipfile as zip
from os import PathLike, path
from typing import Any, Optional

from raschel import file_util
from raschel.diff import diff_text1


class MetaInfo:
    def __init__(
        self, files: dict[str, list[dict[str, Any]]] | None = None, diff_backup: bool = False
    ):
        self.diff_backup = diff_backup
        self.files = files or {}
        self.id = uuid.uuid4()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetaInfo":
        if not isinstance(diff_backup := data.get("diff_backup", False), bool):
            raise ValueError
        if not isinstance(files := data.get("files", {}), dict):
            raise ValueError

        ret = cls(files, diff_backup)
        _id = data.get("id", uuid.uuid4())
        ret.id = _id
        return ret

    def to_dict(self) -> dict[str, Any]:
        return {
            "diff_backup": self.diff_backup,
            "files": self.files,
            "id": str(self.id),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)


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
    out_path = f"{target_dir}/backup_{time}.zip"
    meta_info = MetaInfo()
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
                            "filename": filename,
                            "archive_name": arcname,
                            "hash": file_util.get_file_hash(filename),
                            "timestamp": timestamp.isoformat(),
                        }
                        key = Path(dir).absolute().as_posix()
                        meta_info.files.setdefault(key, []).append(value)  # type: ignore
                    except Exception as e:
                        failed = True
                        failed_list.append((filename, arcname))
                        log.error(e)
        """
            also store that we are making a full backup
        """
        zipfile.writestr("meta.info", meta_info.to_json())
    if failed:
        log.error("Backup unsuccesful!")
        for f, t in failed_list:
            log.error(f"Could not write '{f}' to '{t}'")
    return out_path


def compare_backups(
    backup_path: PathLike[str], dir_path: PathLike[str]
) -> list[tuple[str, str]]:
    """
    Compares backups with original files in a directory.

    Arguments:
        `backup_path`-- The path to the backup file, which is expected to be a `.zip` file.
        `dir_path`-- The path to the directory containing the original files.

    Raises:
        ValueError: the backup file is not a `.zip` file.

    Returns:
        List of tuples, where each tuple contains the name of an original file and the differences found in its contents compared to the backed up version. If there are no changes, an empty string is returned.

    """
    backup_files: list[dict[str, Any]] = []

    if not zip.is_zipfile(backup_path):
        raise ValueError(f"Expected '{backup_path}' to be a '.zip' file.")

    with zip.ZipFile(backup_path) as archive:  # type: ignore
        data = archive.read(
            "meta.info",
        )
        data, _ = utf_8_decode(data)
        meta: MetaInfo = MetaInfo.from_dict(json.loads(data))
        """
        Read the backed up files from the meta file in the archive

        """
        for _, meta_files in meta.files.items():
            # for v in meta_files:
            backup_files.extend(meta_files)

        original_files: list[str] = []
        for file_dir, _, files in os.walk(dir_path):
            for file in files:
                original_files.append((Path(file_dir) / file).as_posix())

        for d in backup_files:
            if (file := d["filename"]) in original_files:
                if not d["hash"] == (file_util.get_file_hash(file)):
                    contents = archive.read(d["archive_name"])
        changed_paths: list[tuple[str, str]] = []
        for backup_file in backup_files:
            if (file := backup_file["original_path"]) in original_files:
                if not backup_file["hash"] == file_util.get_file_hash(file):
                    contents = archive.read(backup_file["archive_name"])
                    diff = diff_text1(file, contents)
                    changed_paths.append((file, str(diff)))

    return changed_paths

def do_diff_backup(backup_dir: str, original_dir: str) -> None:
    pass
