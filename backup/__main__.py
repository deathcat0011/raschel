import fnmatch  # to translate our exclusion lists and filters to glob strings
import logging
import os
import re as re
import zipfile as zip
from os import PathLike, path
from typing import Iterator

import backup.config as config

log = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    format="[%(levelname)s][%(asctime)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)


def run_backup(paths_to_backup: PathLike[str], target_path: PathLike[str]):

    # paths_to_backup: [PathLike[str]] = None
    # target_dir: PathLike[str] = None
    # calculate diffs to last backup?
    # skip for now

    # collect files into archive
    target_parent_dir = path.abspath(path.dirname(target_path))
    if not path.exists(target_path):
        try:
            os.makedirs(target_path)
        except OSError as e:
            log.error(f"Could not create target dir: {e}")
            raise e
    # if path.exists(target_path):
    #     log.error(f"Backup file already exists in {target_path}")
    #     raise FileExistsError(f"Backup file already exists in {target_path}")

    # now recursively go through the paths
    for dir in paths_to_backup:
        print(dir)
        # !Bug dir could be absolute path (with drive letters, this would make join return only dir instead of target_path + dir, trying to overwrite the path we want to backup)
        if path.isabs(dir):
            (drive, part) = path.splitdrive(dir)
            drive = (drive[:-1]).lower()
            archive_dir = path.normpath(path.join(drive, part[1:]))
        else:
            archive_dir = dir
        dir = path.abspath(path.join(target_path, dir))
        dir += ".zip"
        with zip.ZipFile(
            dir,
            "a",
            compression=zip.ZIP_DEFLATED,
            compresslevel=9,
        ) as zipfile:
            for _, _, files in os.walk(dir):
                log.info("{}")
                zipfile.write(
                    files,
                    path.dirname(archive_path),
                    # compress_type=zip.ZIP_DEFLATED,
                    # compresslevel=9,
                )


def main():
    conf = config.load_config()  # type: ignore

    # path = "./**"
    # exclusion = ["*main*"]

    # run_backup(["D:/Coderepo/py-toms-back/backup"], "./backup_test")

    # print("Exclusions: ", end=None)
    # for e in exclusion:
    #     print(f"\t{fnmatch.translate(e)}")

    # for file in glob_files_iter(path, exclusion):
    #     if isdir(file):
    #         print(file)
    #     else:
    #         print(
    #             f"\t{basename(file):40} {file_util.get_last_changed(file)} {get_file_hash(file)}"
    #          )


if __name__ == "__main__":
    main()
