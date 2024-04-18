from typing import Dict, List


class Config:
    pass


def load_config() -> Config | None:
    raise NotImplementedError


def get_diffs(
    backed_up_file_list: List[str], up_file_lis: List[str]
) -> Dict[str, bool]:
    raise NotImplementedError


def glob_files(root_dir: str) -> List[str]:
    raise NotImplementedError


def main():
    pass


if __name__ == "__main__":
    main()
