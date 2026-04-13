from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv

from platypusbot.interfaces.cli.chat_cli import run_cli
from platypusbot.interfaces.gui.chat_gui import run_gui
from platypusbot.interfaces.web.chat_web import run_web


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Launch PlatypusBot.")
    parser.add_argument(
        "interface",
        nargs="?",
        choices=("gui", "cli", "web"),
        default="gui",
        help="Choose which interface to start.",
    )
    args = parser.parse_args()

    if args.interface == "gui":
        if os.name != "nt" and not os.environ.get("DISPLAY"):
            print("No desktop display detected. Starting CLI instead.")
            run_cli()
            return
        run_gui()
        return

    if args.interface == "web":
        run_web()
        return

    run_cli()


if __name__ == "__main__":
    main()
