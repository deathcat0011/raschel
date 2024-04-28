import logging
import re as re

from raschel import backup
from raschel import config

log = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    format="[%(levelname)s][%(asctime)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)


def main():
    conf = config.load_config()  # type: ignore

    path = "./test/**"
    # exclusion = ["*main*"]

    backup.run_backup(["E:/CodeRepo/py-toms-back/test"], "./backup_test")

    # print("Exclusions: ", end=None)
    # for e in exclusion:
    #     print(f"/t{fnmatch.translate(e)}")

    # for file in glob_files_iter(path, exclusion):
    #     if isdir(file):
    #         print(file)
    #     else:
    #         print(
    #             f"/t{basename(file):40} {file_util.get_last_changed(file)} {get_file_hash(file)}"
    #          )


if __name__ == "__main__":
    main()
