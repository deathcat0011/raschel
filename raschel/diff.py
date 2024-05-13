from os import PathLike
from typing import Iterator
from diff_match_patch import diff_match_patch  # type: ignore


def _do_diff(f1: str, f2: str) -> Iterator[str] | None:
    dmp = diff_match_patch()
    patches = dmp.patch_make(f2, f1)  # type: ignore
    return dmp.patch_toText(patches)  # type: ignore


def diff_text_file(
    file_path1: PathLike[str], file_path2: PathLike[str]
) -> Iterator[str] | None:
    with open(file_path1, "r") as file1:
        with open(file_path2, "r") as file2:
            file1_gen = file1.read()  # _read_in_chunks(file1, 4096)
            file2_gen = file2.read()  # _read_in_chunks(file2, 4096)
            return _do_diff(file1_gen, file2_gen)
            # return _do_diff(file2_gen, file1_gen)


def diff_text1(
    file_path1: PathLike[str], bytes: bytearray | bytes
) -> Iterator[str] | None:
    """
    compare with the second file loaded in memory
    """
    with open(file_path1, "r") as file1:
        file1_gen = file1.read()  # _read_in_chunks(file1, 4096)
        return _do_diff(file1_gen, bytes.decode())


def apply_patch(
    file_path: PathLike[str],
    patch_path: PathLike[str],
):
    with open(file_path, "r+") as file:
        with open(patch_path, "r") as patch:
            dmp = diff_match_patch()
            text = file.read()
            patch_text = patch.read()
            patches = dmp.patch_fromText(patch_text)  # type: ignore
            patch_text, _ = dmp.patch_apply(patches, text)  # type: ignore
            file.seek(0)
            file.write(patch_text)  # type: ignore
