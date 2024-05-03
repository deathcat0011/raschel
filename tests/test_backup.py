from os import path
import os
import random
import shutil
import tempfile
import pytest

from .context import raschel  # type: ignore
from raschel import backup


TEST_DIR = f"{tempfile.mkdtemp(prefix='raschel_')}/"
TEST_DIR_IN = f"{TEST_DIR}/in"
TEST_DIR_OUT = f"{TEST_DIR}/out"


def generate_text(length: int) -> str:
    alpha = [chr(ord("a") + i) for i in range(26)]
    alpha.extend([chr(ord("A") + i) for i in range(26)])
    alpha.extend([chr(ord("0") + i) for i in range(10)])
    # alpha.extend(["\n", " ", "\t"])
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


def test_backup() -> None:
    out_path = backup.run_backup([TEST_DIR_IN], TEST_DIR_OUT)  # type: ignore
    
