import fnmatch  # to translate our exclusion lists and filters to glob strings
import hashlib
import logging
import re as re
from glob import glob, iglob
from os.path import basename, isdir
from typing import Dict, Iterator, List


import config
import file_util

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


def run_backup(config: config.Config):
    pass

def main():
    conf = config.load_config()  # type: ignore
    
    path = "./**"
    exclusion = ["*main*"]

    print("Exclusions: ", end=None)
    for e in exclusion:
        print(f"\t{fnmatch.translate(e)}")

    for file in glob_files_iter(path, exclusion):
        if isdir(file):
            print(file)
        else:
            print(
                f"\t{basename(file):40} {file_util.get_last_changed(file)} {get_file_hash(file)}"
            )


if __name__ == "__main__":
    main()
