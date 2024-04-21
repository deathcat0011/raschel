import fnmatch  # to translate our exclusion lists and filters to glob strings
import hashlib
import logging
import os
import re as re
import zipfile as zip
from glob import glob, iglob
from os import PathLike, path
from typing import Dict, Iterator, List

import config

log = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    format="[%(levelname)s][%(asctime)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)


def get_diffs(
    backed_up_file_list: List[str], up_file_lis: List[str]
) -> Dict[str, bool]:
    raise NotImplementedError


def glob_files(glob_str: str) -> List[str]:
    return glob(glob_str, recursive=True)


def glob_files_iter(glob_str: str, exclusion_list: list[str]) -> Iterator[str]:
    patterns = [re.compile(fnmatch.translate(x)) for x in exclusion_list]
    for x in iglob(glob_str, recursive=True):
        if not any(map(lambda p: p.match(x) is not None, patterns)):
            yield x


def matches(pattern: str, name: str) -> bool:
    reg = re.compile(fnmatch.translate(pattern))
    return reg.match(name) is not None


def get_file_hash(filename: str):
    BUFFER_SIZE = 4096
    hash = hashlib.sha256()
    with open(filename, "rb") as file:
        while True:
            chunk = file.read(BUFFER_SIZE)
            if not chunk:
                break
            hash.update(chunk)
        return hash.hexdigest()


def diff_file(file1, file2) -> bytearray:
    pass


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

    path = "./**"
    exclusion = ["*main*"]

    run_backup(["D:/Coderepo/py-toms-back/backup"], "./backup_test")

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
