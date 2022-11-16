"""Uninstaller CLI"""

import sys
import uninstaller
import argparse
from typing import Optional, Sequence


def _get_main_parser() -> argparse.ArgumentParser:
    """Construct the main parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        nargs="+",
        metavar="package",
        dest="packages",
        type=str,
        help="name of the package to uninstall",
    )
    parser.add_argument(
        "--root",
        "-r",
        metavar="path",
        type=str,
        help="override package search root",
    )
    parser.add_argument(
        "--base",
        "-b",
        metavar="path",
        type=str,
        help="overrirde base path (aka prefix)",
    )
    parser.add_argument(
        "--scheme",
        "-s",
        metavar="scheme",
        type=str,
        help="override the default installation scheme",
    )
    parser.add_argument(
        "--not-pure-python",
        "-n",
        action="store_true",
        dest="unpure",
        help="use this if the package to be uninstalled is not pure python",
    )
    parser.add_argument(
        "--ignore-checksums",
        "-i",
        action="store_true",
        dest="nocsum",
        help="use this to skip checksum verification",
    )
    parser.add_argument(
        "--ignore-sizes",
        "-z",
        action="store_true",
        dest="nosize",
        help="use this to skip file size verification",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="print every file that's removed to stdout",
    )

    return parser


def _main(cli_args: Sequence[str], program: Optional[str] = None) -> None:
    """Process arguments and perform the uninstall."""
    parser = _get_main_parser()
    if program:
        parser.prog = program
    args = parser.parse_args(cli_args)

    if args.unpure:
        pkg_scheme = "platlib"
    else:
        pkg_scheme = "purelib"

    u = uninstaller.Uninstaller(
        root=args.root,
        base=args.base,
        scheme=args.scheme,
        whl_scheme=pkg_scheme,
    )

    for package in args.packages:
        u.uninstall(
            package,
            ignore_csum=args.nocsum,
            ignore_size=args.nosize,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    _main(sys.argv[1:], "python -m uninstaller")
