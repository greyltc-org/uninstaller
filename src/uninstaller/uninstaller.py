import base64
import csv
import hashlib
import os
import sysconfig
from glob import iglob
from pathlib import Path
from typing import Dict, Optional, Union


class Uninstaller(object):
    """a package uninstaller"""

    search_dir: str
    pkg_dirs: list[str]

    def __init__(
        self,
        root: Optional[str] = None,
        base: Optional[str] = None,
        scheme: Optional[Union[str, Dict[str, str]]] = None,
        whl_scheme: str = "purelib",
    ):
        vars = {}
        if base is None:
            installed_base = sysconfig.get_config_var("base")
            assert installed_base
        else:
            vars["base"] = vars["platbase"] = installed_base = base

        if isinstance(scheme, dict):
            scheme_dict = scheme
        else:
            if scheme is None:
                install_scheme = sysconfig.get_default_scheme()
            else:
                install_scheme = scheme

            scheme_dict = sysconfig.get_paths(scheme=install_scheme, vars=vars)

        self.search_dir = scheme_dict[whl_scheme]

        if root is not None:
            sdp = Path(self.search_dir)
            if sdp.is_absolute():
                join_parts = sdp.parts[1:]
            else:
                join_parts = sdp.parts
            self.search_dir = str(Path(root).joinpath(*join_parts))

        try:
            root, self.pkg_dirs, files = next(os.walk(self.search_dir))
        except Exception:
            self.pkg_dirs = []

    def uninstall(
        self,
        package: str,
        ignore_csum: bool = False,
        ignore_size: bool = False,
        verbose: bool = False,
    ):
        """uninstall a package"""
        match_dir = None
        for dir in self.pkg_dirs:
            if dir.startswith(f"{package}-") and dir.endswith(".dist-info"):
                if match_dir is None:
                    match_dir = dir
                else:
                    raise RuntimeError(f"Too many matches for {package}")

        assert match_dir

        to_removes: list[str] = []
        full_match_dir = os.path.join(self.search_dir, match_dir)
        record_file = os.path.join(full_match_dir, "RECORD")
        with open(record_file, newline="") as csvrecords:
            records = csv.reader(csvrecords, strict=True)
            for path, hash, size in records:

                installed_file = os.path.join(self.search_dir, path)
                is_recordfile = installed_file == record_file
                if (not ignore_size) and (not is_recordfile) and (size != ""):
                    fstat = os.stat(installed_file)
                    msg = f"The file has {fstat.st_size} bytes but RECORD thinks it should have {size}"
                    assert fstat.st_size == int(size), msg
                if (not ignore_csum) and (not is_recordfile) and (hash != ""):
                    with open(installed_file, "rb") as fh:
                        # TODO: only in 3.11
                        # digest = hashlib.file_digest(fh, hash_kind)
                        hash_kind, hash_value = hash.split("=", 1)
                        hasher = getattr(hashlib, hash_kind)()
                        while True:
                            buf = fh.read(4096)
                            if not buf:
                                break
                            hasher.update(buf)
                        digest = base64.urlsafe_b64encode(hasher.digest())
                        digest = digest.removesuffix(b"=")
                        msg = f"The file's hash is {digest.decode()} but RECORD thinks it should be {hash_value}"
                        assert digest.decode() == hash_value, 
                if ignore_size and ignore_csum:
                    assert os.path.isfile(installed_file)
                to_removes.append(installed_file)

        # remove the RECORD files and their .pycs, keeping track of folders
        holding_dirs = {}  # dirs we might delete later
        pyc_to_culls = []  # byte compiled files we might delete later
        for to_remove in to_removes:
            premove = Path(to_remove)

            # make a record of the folders the files were in
            holding_dir = premove.parent.resolve()
            holding_dirs[holding_dir] = None

            # locate the .pyc file that matches the .py file
            if premove.suffix == ".py":
                pyc_dir = holding_dir / "__pycache__"
                if pyc_dir.exists():
                    holding_dirs[pyc_dir] = None
                    for bc_match in iglob(str(pyc_dir / premove.stem) + "*.pyc"):
                        pyc_to_culls.append(bc_match)

            # make the file from the RECORD line go away
            os.unlink(to_remove)

            if verbose:
                print(f"removed RECORD file:     {to_remove}")

        # now remove the byte compiled files
        for pyc_to_cull in pyc_to_culls:
            # if the pyc was in RECORD, it's already been removed
            if Path(pyc_to_cull).exists():
                os.unlink(pyc_to_cull)
                if verbose:
                    print(f"removed extra .pyc file: {pyc_to_cull}")

        # now remove any empty directories
        for holding_dir in list(holding_dirs):
            # move linearly up the folder tree, deleting empty folders
            holding_dir_parts = list(holding_dir.parts)
            while len(holding_dir_parts) > 1:  # don't even recurse to root
                path = Path(*holding_dir_parts)
                root, dirs, files = next(os.walk(path))

                # only empty folders get removed
                if (not files) and (not dirs):
                    os.rmdir(root)
                    if verbose:
                        print(f"removed empty directory: {root}")

                holding_dir_parts.pop()

            # NOTE: the RECORD file does not record the folders created
            # during installation (only files), so we can't, with 100% certianty,
            # know which folders should be removed here. right now, all empty
            # folders up the chain are removed, seems like the only way to be sure
            # everything the installer made gets disappeared
