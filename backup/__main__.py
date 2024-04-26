import datetime
import fnmatch  # to translate our exclusion lists and filters to glob strings
import logging
import os
import re as re
import zipfile as zip
from os import PathLike, path
from typing import Iterator, Optional

import backup.config as config

log = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    format="[%(levelname)s][%(asctime)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)


def to_zip_path(p: str) -> Optional[str]:
    """
    We want to keep the path information of a file tied to its location in the original file system, so we have to remove the drive letters. returns None if the path was invalid
    """
    if path.isabs(p):
        (drive, p) = path.splitdrive(p)
        drive: setattr = drive.replace(':','').lower()
        if not drive:
            return None
        # now join the lower case drive letter with the rest of the path
        return path.normpath(f"{drive}/{p}")
    return p


def run_backup(paths_to_backup: PathLike[str], target_dir: PathLike[str]):

    os.makedirs(target_dir, exist_ok=True)
    failed = False
    failed_list = []
    time = datetime.datetime.now().isoformat('_','seconds').replace("-","_").replace(':','_')
    with zip.ZipFile(
        f"{target_dir}/backup_{time}.zip",
        "a",
        compression=zip.ZIP_DEFLATED,
        compresslevel=9,
    ) as zipfile:
        # now recursively go through the paths
        for dir in paths_to_backup:
            for file_dir, _, files in os.walk(path.abspath(dir), ):
                if (archive_dir := to_zip_path(file_dir)) is None:
                    log.error(f"Invalid path '{dir}'")
                    continue
                for file in files:
                    log.info(f"{file}")
                    filename = path.join(file_dir, file)
                    arcname =path.join(archive_dir, file)
                    try:
                        zipfile.write(
                            filename,
                            arcname,
                            compress_type=zip.ZIP_DEFLATED,
                            compresslevel=9,
                        )
                    except Exception as e:
                        failed = True
                        failed_list.append((filename, arcname))
                        log.error(e)
    if failed:
        log.error("Backup unsuccesful!")
        for (f,t) in failed_list:
            log.error(f"Could not write '{f}' to '{t}'")

def main():
    conf = config.load_config()  # type: ignore

    path = "./test/**"
    # exclusion = ["*main*"]

    run_backup(["./conda/"], "./backup_test")

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
