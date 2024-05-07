import json
from os import path
import os
from pathlib import Path
import random
import shutil
import tempfile
import pytest
import zipfile as zip

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
            original_files.extend([(Path(dir) / file).as_posix() for file in dirs])

    """Test"""

    out = backup.run_backup([TEST_DIR_IN], TEST_DIR_OUT)  # type: ignore
    backup_files = []
    with zip.ZipFile(out, "r") as zipfile:
        meta = backup.MetaInfo.from_dict(json.load(zipfile.open("meta.info")))

        for dirs in meta.files.values():
            backup_files.extend([dir["filename"]for dir in dirs])
    assert len(original_files) == len(backup_files)
    for file in backup_files:
        assert file in original_files


def test_diff_backup() -> None:
    """"""

    """Fixture"""
    backup_path = backup.run_backup([TEST_DIR_IN], TEST_DIR_OUT)  # type: ignore
    all_files: list[str] = []

    for file_dir, _, files in os.walk(path.abspath(TEST_DIR_IN)):
        for selected in files:
            all_files.append(path.abspath(path.join(file_dir, selected)))
    selected = random.choice(all_files)
    text = generate_text(10)
    with open(selected, "a") as file:
        file.write(text)

    """Test"""

    diff = backup.compare_backups(
        backup_path,  # type: ignore
        TEST_DIR_IN,  # type: ignore
    )

    """Check"""
    dmp = diff_match_patch()
    diff = dmp.patch_fromText(diff[0][1])
    diff_text, stat = dmp.patch_apply(diff, text)
    assert len(diff_text) == 0 and stat[0]  # type: ignore
    pass
