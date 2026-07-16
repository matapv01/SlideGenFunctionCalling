"""Backward-compatible launcher for the official SlideGen SDFT entrypoint."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    from rl.sdft_official.train_slidegen import main as official_main

    official_main()


if __name__ == "__main__":
    main()
