from os import PathLike
from typing import Iterator
from diff_match_patch import diff_match_patch

def diff_text_file(
    file_path1: PathLike[str], file_path2: PathLike[str]
) -> Iterator[str] | None:
    with open(file_path1, "r") as file1:
        with open(file_path2, "r") as file2:
            file1_gen = file1.read()  # _read_in_chunks(file1, 4096)
            file2_gen = file2.read()  # _read_in_chunks(file2, 4096)
            dmp = diff_match_patch()
            patches = dmp.patch_make(file1_gen, file2_gen)
            return dmp.patch_toText(patches)
            # return difflib.unified_diff(file1_gen, file2_gen, file_path1, file_path2) # type: ignore


def apply_patch(
    file_path: PathLike[str],
    patch_path: PathLike[str],
):
    with open(file_path, "r+") as file:
        with open(patch_path, "r") as patch:
            dmp = diff_match_patch()
            text = file.read()
            patch_text = patch.read()
            patches = dmp.patch_fromText(patch_text)
            patch_text, _ = dmp.patch_apply(patches, text)
            file.seek(0)
            file.write(patch_text)

