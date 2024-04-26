import datetime
import fnmatch
import glob
import hashlib
import os
from io import TextIOWrapper
from os import PathLike
import re
from typing import Any, Dict, Generator, Iterator, List


class FileAttribs:

    def get_last_modified(self) -> float:
        # TODO implement
        return 0


def get_last_changed(path: PathLike[str] | str) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(os.path.getmtime(path))


def file_has_changed(
    path: PathLike[str], lib: Dict[PathLike[str], FileAttribs]
) -> bool:
    # check based on modified time stamp
    return (
        datetime.datetime.fromtimestamp(FileAttribs().get_last_modified())
        - datetime.datetime.fromtimestamp(os.path.getmtime(path))
    ).seconds > 0


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


def _read_lazy_chunks(
    file_object: TextIOWrapper, chunk_size: int = 1024
) -> Generator[str, Any, None]:  # noqa: F821
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def _read_lazy_lines(
    file_object: TextIOWrapper, chunk_size: int = 1024
) -> Generator[str, Any, None]:
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.readline()
        if not data:
            break
        yield data


def glob_files(glob_str: str) -> List[str]:
    return glob(glob_str, recursive=True)


def glob_files_iter(glob_str: str, exclusion_list: list[str]) -> Iterator[str]:
    patterns = [re.compile(fnmatch.translate(x)) for x in exclusion_list]
    for x in glob.iglob(glob_str, recursive=True):
        if not any(map(lambda p: p.match(x) is not None, patterns)):
            yield x
