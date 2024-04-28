import logging
import re as re
from argparse import ArgumentParser

from raschel import backup
from raschel import config

log = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    format="[%(levelname)s][%(asctime)s] %(name)s: %(message)s",
    level=logging.DEBUG,
)


def main():

    parser = ArgumentParser(description="Simple zip-based backup client")
    parser.add_argument(
        "-d",
        "--dir",
        action="extend",
        nargs="+",
        type=str,
        help="Directories to be included in the backup",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--target",
        action="store",
        type=str,
        default="./",
        help="Directory where the backup should be stored",
    )
    # args = parser.parse_args()

    # backup.run_backup(args.dir, args.target)
    backup.compare_with_backup("./backup_2024_04_28_13_15_41.zip", "./test")


if __name__ == "__main__":
    main()
