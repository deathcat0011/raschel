import io
import json
from os import path
import os
from pathlib import Path
import random
import shutil
import tempfile
import pytest
import zipfile
import itertools


from .context import raschel  # type: ignore
from raschel import backup
from diff_match_patch import diff_match_patch  # type: ignore


TEST_DIR = f"{tempfile.mkdtemp(prefix='raschel_')}/"
TEST_DIR_IN = f"{TEST_DIR}/in"
TEST_DIR_OUT = f"{TEST_DIR}/out"


def generate_text(length: int, use_extra_symbols: bool = False) -> str:
    alpha = [chr(ord("a") + i) for i in range(26)]
    alpha.extend([chr(ord("A") + i) for i in range(26)])
    alpha.extend([chr(ord("0") + i) for i in range(10)])
    if use_extra_symbols:
        alpha.extend(["\n", " ", "\t"])
    return "".join([random.choice(alpha) for _ in range(length)])


@pytest.fixture(scope="session", autouse=True)
def create_temp_dir():
    os.makedirs(TEST_DIR, exist_ok=True)
    root_dir = TEST_DIR_IN
    for i in range(random.randint(1, 5)):
        dir = f"{root_dir}/dir{i}/"
        os.makedirs(dir)
        for _ in range(random.randint(1, 10)):
            filename = f"{dir}/{generate_text(random.randint(5, 10))}"
            with open(file=filename, mode="w") as file:
                file.write(generate_text(random.randint(100, 10000)))


@pytest.fixture(scope="session", autouse=True)
def cleanup(request: pytest.FixtureRequest):
    def remove_test_dir():
        if path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        request.addfinalizer(remove_test_dir)


def test_full_backup() -> None:
    """"""

    """Fixture"""
    original_files = []
    for dir, _, dirs in os.walk(Path(TEST_DIR_IN).as_posix()):
        if dirs and len(dirs) > 0:
            original_files.extend([(Path(dir) / file).as_posix() for file in dirs])  # type: ignore

    """Test"""

    out = backup.do_backup([TEST_DIR_IN], TEST_DIR_OUT)  # type: ignore
    backup_files = []
    with zipfile.ZipFile(out, "r") as archive:  # type: ignore
        meta = backup.MetaInfo.from_dict(json.load(archive.open("meta.info")))

        for root, dirs in meta.dirs.items():
            backup_files.extend([(Path(root) / dir["filename"]).as_posix() for dir in dirs])  # type: ignore
    assert len(original_files) == len(backup_files)  # type: ignore
    for file in backup_files:  # type: ignore
        assert file in original_files


def test_diff_one_file() -> None:
    """"""

    """Fixture"""
    backup_path = backup.do_backup([TEST_DIR_IN], TEST_DIR_OUT)  # type: ignore
    assert backup_path is not None
    all_files: list[str] = []

    for file_dir, _, files in os.walk(path.abspath(TEST_DIR_IN)):
        for selected in files:
            all_files.append(path.abspath(path.join(file_dir, selected)))
    selected = random.choice(all_files)
    text = generate_text(10)
    with open(selected, "a") as file:
        file.write(text)

    """Test"""

    with zipfile.ZipFile(file=backup_path) as archive:

        diff = backup.get_archive_file_diffs(
            archive=archive,  # type: ignore
        )

    """Check"""
    dmp = diff_match_patch()
    diff = dmp.patch_fromText(diff[0][1])  # type: ignore
    diff_text, stat = dmp.patch_apply(diff, text)  # type: ignore
    assert diff_text == text  # type: ignore


def test_diff_multiple() -> None:
    """"""

    """Fixture"""
    backup_path = backup.do_backup([TEST_DIR_IN], TEST_DIR_OUT)  # type: ignore
    assert backup_path is not None

    all_files: list[str] = []

    for file_dir, _, files_to_change in os.walk(path.abspath(TEST_DIR_IN)):
        for selected in files_to_change:
            all_files.append((Path(file_dir) /  selected).absolute().as_posix())
    files_to_change = random.sample(all_files, 3)

    changes: dict[str, str] = {}
    dmp = diff_match_patch()

    for selected in files_to_change:
        text = generate_text(10)

        with open(selected, "a+") as file:
            file.seek(0)
            content = file.read()
            file.seek(io.SEEK_END)
            file.write(text)
            content_after = content + text

            diff_text = dmp.diff_main(content, content_after)  # type: ignore
            diff_text = dmp.patch_make(diff_text)  # type: ignore
            diff_text = dmp.patch_toText(diff_text)  # type: ignore
            changes[Path(selected).as_posix()] = diff_text

    """Test"""


    with zipfile.ZipFile(backup_path) as archive:
        diffs = backup.get_archive_file_diffs(
            archive=archive,  # type: ignore
        )
        """Check"""

        #check wether all changed files have been detected
        assert len(files_to_change) == len(diffs)
        assert all((a in files_to_change for a,_ in diffs))
        for file, diff in diffs:
            
            assert changes[file] == diff
