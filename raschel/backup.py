from codecs import utf_8_decode
import datetime
import json
import logging as log
import os
from pathlib import Path
import pathlib
import re as re
import uuid
import zipfile
from os import PathLike, path
from typing import Any, Optional

from raschel import file_util
from raschel.diff import diff_text1


class MetaInfo:
    def __init__(
        self,
        files: dict[str, list[dict[str, Any]]] | None = None,
        diff_backup: bool = False,
    ):
        self.diff_backup = diff_backup
        self.dirs = files or {}
        self.id = uuid.uuid4()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetaInfo":
        if not isinstance(diff_backup := data.get("diff_backup", False), bool):
            raise ValueError
        if not isinstance(files := data.get("dirs", {}), dict):
            raise ValueError

        ret = cls(files, diff_backup)  # type: ignore
        _id = data.get("id", uuid.uuid4())
        ret.id = _id
        return ret

    def to_dict(self) -> dict[str, Any]:
        return {
            "diff_backup": self.diff_backup,
            "dirs": self.dirs,
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


def do_backup(
    paths_to_backup: list[PathLike[str]], target_dir: PathLike[str]
) -> str | None:
    """
    Raises:
        ValueError if one of the file paths could not be converted into a zip friendly path
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
    failed_list: list[str] = []
    timestamp = datetime.datetime.now()
    time = timestamp.isoformat("_", "seconds").replace("-", "_").replace(":", "_")
    meta_info = MetaInfo()
    out_path = (
        (Path(target_dir) / f"{str(meta_info.id)}_{time}.zip").resolve().as_posix()
    )

    with zipfile.ZipFile(
        out_path,
        "a",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        # now recursively go through the paths
        for dir in paths_to_backup:
            for file_dir, _, files in os.walk(
                path.abspath(dir),
            ):
                dir = Path(dir).resolve().as_posix()
                for file in files:
                    log.info(f"{file}")
                    filename = (Path(file_dir) / file).as_posix()
                    try:
                        root_dir = Path(dir).absolute().as_posix()
                        root_dir_base = Path(Path(dir).absolute().name)
                        file_archive_path = Path(filename).relative_to(root_dir)
                        if not file_archive_path:
                            log.error(
                                f"Could not convert '{filename}' to a zip friendly path"
                            )
                            raise ValueError
                        archive.write(
                            filename=filename,
                            arcname=root_dir_base / file_archive_path,
                            compress_type=zipfile.ZIP_DEFLATED,
                            compresslevel=9,
                        )
                        value = {
                            "filename": file_archive_path.as_posix(),
                            "hash": file_util.get_file_hash(filename),
                            "timestamp": datetime.datetime.now().isoformat(),
                            "last_modified": datetime.datetime.fromtimestamp(
                                path.getmtime(filename)
                            ).isoformat(),
                        }
                        meta_info.dirs.setdefault(root_dir, []).append(value)  # type: ignore
                    except Exception as e:
                        failed = True
                        failed_list.append(filename)
                        log.error(e)
        """
            also store that we are making a full backup
        """
        archive.writestr("meta.info", meta_info.to_json())
    if failed:
        log.error("Backup unsuccesful!")
        for f in failed_list:
            log.error(f"Could not write '{f}' to zip file in'{to_zip_path(f)}'")
        if path.exists(out_path):
            os.remove(path=out_path)
    log.info(f"Backup succesfully written to '{out_path}'")
    return out_path


def get_archive_file_diffs(
    archive: zipfile.ZipFile,
):  # TODO! Respect zip folderstructure, this will be changed soon!
    """Compare files with the ones referenced in backup."""
    backup_files: list[dict[str, Any]] = []

    data = archive.read(
        "meta.info",
    )
    data, _ = utf_8_decode(data)
    meta: MetaInfo = MetaInfo.from_dict(json.loads(data))
    """
    Read the backed up files from the meta file in the archive
    """
    changed_paths: list[tuple[str, str]] = []
    for backup_dir, dirs in meta.dirs.items():
        archive_root = Path(backup_dir).name
        for file_obj in dirs:
            original_file_path = (Path(backup_dir) / file_obj["filename"]).as_posix()

            if not path.exists(original_file_path):
                log.warning(f"{original_file_path} has been moved or deleted.")
                continue  # TODO handle file removed

            original_timestamp = path.getmtime(original_file_path)
            backup_timestamp = datetime.datetime.fromisoformat(
                file_obj["last_modified"]
            ).timestamp()

            if (
                original_timestamp > backup_timestamp and file_util.get_file_hash(original_file_path) != file_obj["hash"]
            ):  # original is newer, FIXME! at the moment on windows this is always true in tests, cannot verify, so we also check the hash
                log.debug(f"{original_file_path} has changed.")
                file_archive_path = (
                    Path(archive_root) / file_obj["filename"]
                ).as_posix()
                contents = archive.read(file_archive_path)
                diff = diff_text1(original_file_path, contents)



                changed_paths.append((original_file_path, str(diff)))

    original_files: list[str] = []
    for dir_path, meta_files in meta.dirs.items():
        # for v in meta_files:
        backup_files.extend(meta_files)

        for file_dir, _, files in os.walk(dir_path):
            for file in files:
                original_files.append((Path(file_dir) / file).as_posix())

    for backup_file in backup_files:
        if (file := backup_file["filename"]) in original_files:
            if not backup_file["hash"] == (file_util.get_file_hash(file)):
                file_archive_path = to_zip_path(backup_file["filename"])
                if not file_archive_path:
                    log.error(
                        f"Could not convert '{backup_file['filename']}' to a zip friendly path"
                    )
                    raise ValueError
                contents = archive.read(file_archive_path.as_posix())
                diff = diff_text1(file, contents)
                changed_paths.append((file, str(diff)))

    return changed_paths


def do_diff_backup(
    backup_archive: str, dir_path: PathLike[str], target_dir: PathLike[str]
) -> str:
    """
    Do a differential backup based on a given full backup

    """
    if not zipfile.is_zipfile(backup_archive):
        raise ValueError(f"Expected '{backup_archive}' to be a '.zip' file.")

    # collect original archive dirs from previous backup
    with zipfile.ZipFile(backup_archive) as archive:  # type: ignore

        diffs: list[tuple[str, str]] = get_archive_file_diffs(archive)

        data = archive.read(
            "meta.info",
        )
        data, _ = utf_8_decode(data)
        old_meta: MetaInfo = MetaInfo.from_dict(json.loads(data))
        timestamp = datetime.datetime.now()
        time = timestamp.isoformat("_", "seconds").replace("-", "_").replace(":", "_")
        out_path = (Path(target_dir) / f"{old_meta.id}_{time}.zip").as_posix()

        files: dict[str, list[dict[str, str]]] = {
            Path(dir_path).as_posix(): [
                {
                    "filename": changed_file,
                    "hash": file_util.get_file_hash(changed_file),
                    "timestamp": timestamp.isoformat(),
                    "last_modified": datetime.datetime.fromtimestamp(
                        path.getmtime(changed_file)
                    ).isoformat(),
                }
                for changed_file, _ in diffs
            ]
        }

        new_meta = MetaInfo(files=files, diff_backup=True)

        with zipfile.ZipFile(
            out_path,
            "a",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as diff_archive:
            diff_archive.writestr("meta.info", new_meta.to_json())
            for changed_file, changed_data in diffs:
                file_archive_path = to_zip_path(changed_file)
                if not file_archive_path:
                    log.error(
                        f"Could not convert '{changed_file}' to a zip friendly path"
                    )
                    raise ValueError
                diff_archive.write(file_archive_path.as_posix(), changed_data)
    return out_path
