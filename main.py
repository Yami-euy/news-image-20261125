#!/usr/bin/env python3
"""THE WEDNESDAY GLOBE — entry program (standard library only).

Copies the pre-rendered entry.png held in this repository to the output
location. No third-party imports, no network, deterministic: the bytes
written are exactly the bytes committed.
"""
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
FILENAME = "entry.png"


def resolve_target(argv):
    """Return the output file path.

    Accepts the destination as a full file path or as a directory, from
    argv[2], then MAKEFUN_OUTPUT_DIR, then the default /output/entry.png.
    """
    dest = None
    if len(argv) > 1 and argv[1]:
        dest = argv[1]
    elif os.environ.get("MAKEFUN_OUTPUT_DIR"):
        dest = os.environ["MAKEFUN_OUTPUT_DIR"]
    if dest:
        path = Path(dest)
        if path.suffix.lower() == ".png" or path.name == FILENAME:
            return path
        return path / FILENAME
    return Path("/output") / FILENAME


def main(argv):
    target = resolve_target(argv)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, target)
    os.chmod(target, 0o644)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
