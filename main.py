#!/usr/bin/env python3
"""Entry program for make.fun's news-image-20261118 competition.

The repository holds one finished image, entry.png, which sums up the
world news of Wednesday 18 November 2026. The grader runs this program
twice in a sandbox with no network: the repository is mounted read-only
and a writable output directory is provided. All the program does is
copy entry.png into that output directory, byte for byte, so both runs
produce exactly the same file.

The output directory comes from the MAKEFUN_OUTPUT_DIR environment
variable when it is set (the kit's local run convention) and falls back
to /output, the grader's mount point.
"""

import hashlib
import os
import shutil
import sys

IMAGE_NAME = "entry.png"


def source_path() -> str:
    """The image ships beside this file in the repository snapshot."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), IMAGE_NAME)


def output_dir() -> str:
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def sha256_of(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    src = source_path()
    dest_dir = output_dir()
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, IMAGE_NAME)
    shutil.copyfile(src, dest)
    # The grader runs this program twice and requires the same bytes
    # both times, so verify the copy landed byte for byte before
    # reporting success: a short write must fail loudly, not silently
    # enter a truncated image.
    if sha256_of(dest) != sha256_of(src):
        print(f"error: {dest} does not match {src}", file=sys.stderr)
        return 1
    print(f"wrote {dest} ({os.path.getsize(dest)} bytes, "
          f"sha256 {sha256_of(dest)[:16]}…)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
