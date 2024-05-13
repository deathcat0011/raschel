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
    # subparsers = parser.add_subparsers()
    # diff_parser = subparsers.add_parser("diff", help="Subcommand to handle diff backups")
    # diff_parser = diff_parser.add_argument(
    #     "-f",
    #     "--from",
    #     # aliases=["_from"],
    #     action="store",
    #     type=str,
    #     required=True,
    #     help="Previous backup to base diff backup on"
    # )

    args = parser.parse_args()
    backup.do_backup(args.dir, args.target)


if __name__ == "__main__":
    main()
