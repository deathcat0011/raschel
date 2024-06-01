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
    )
    parser.add_argument(
        "-t",
        "--target",
        action="store",
        type=str,
        default="./",
        help="Directory where the backup should be stored",
    )

    parser.add_argument(
        "-e",
        "--exclude",
        action="extend",
        nargs="+",
        type=str,
        help="Exclude listed paths from the backup"
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store",
        type=str,
        help="List files inside the backup zip file",
        metavar="BACKUP_FILE"
    )

    args = parser.parse_args()

    if args.list:
        meta = backup.MetaInfo.from_path(args.list)
        backup_files = sorted(backup.get_backup_files(meta))
        for file in backup_files:
            print(file)
        return

    if not args.dir:
        parser.error("the following arguments are required: -d/--dir")
    
    backup.do_backup(args.dir, args.target, args.exclude)


if __name__ == "__main__":
    main()
