import datetime
import os
from os import PathLike
from typing import Dict


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
