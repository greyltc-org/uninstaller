#!/usr/bin/env python3

import unittest
import tempfile
import os
from pathlib import Path

from installer.__main__ import _main as installer_main
from uninstaller.__main__ import _main as uninstaller_main

try:
    import tests.util as tstutil
except ImportError:
    import util as tstutil


class UninstallerTestCase(unittest.TestCase):
    """uninstaller testing"""

    def test_uninstall(self):
        with tempfile.TemporaryDirectory() as tmpdirname:

            # write the wheel file
            whl_filepath = tstutil.fancy_wheel(Path(tmpdirname))

            # install it
            installer_main(
                [str(whl_filepath), "-d", str(tmpdirname)],
                "python -m installer",
            )

            # uninstall the package "fancy" that we just installed
            uninstaller_main(["--verbose", "--root", tmpdirname, "fancy"])

            # check that the uninstaller removed everything it should
            root, dirs, files = next(os.walk(tmpdirname))
            self.assertEqual(dirs, [], msg="found unexpected directories(s)")
            self.assertEqual(files, [whl_filepath.name], msg="found unexpected file(s)")


if __name__ == "__main__":
    unittest.main()
