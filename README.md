<p align="left">
<a href="https://pypi.org/project/uninstaller/"><img alt="PyPI" src="https://img.shields.io/pypi/v/uninstaller"></a>
</p>
# uninstaller
A library for uninstalling python packages. Inverse counterpart of https://github.com/pypa/installer 

# ⚠General Warning⚠
This project uses a bunch of lightly tested logic to decide how to call [`os.unlink()`](https://docs.python.org/3/library/os.html#os.unlink) and [`os.rmdir()`](https://docs.python.org/3/library/os.html#os.rmdir) which make changes to your file system that probably can't be undone. I personally think it's safe (if you're okay with the empty folder warning below) and effective, but it comes with no warranty it won't destroy some data you wish it didn't. That said, I wouldn't run it with root permissions at this point.

# ⚠Empty Folder Warning
This project reads [The RECORD file](https://packaging.python.org/en/latest/specifications/recording-installed-packages/#the-record-file) to figure out how to remove a package. The RECORD file does not contain info on which folders were created during installation (only files), so we can't, with 100% certianty, know which folders should be removed when we try to uninstall a package. After removing all the files listed in RECORD, this project will remove all **empty** folders that were in the chain upwards of where each file in RECORD was. That means it's possible that an empty folder not created at install time will be removed by this tool.

# Scope
The design intent here is that this project just undoes what https://github.com/pypa/installer (or a similar tool) does. This uninstaller can't uninstall all packages. A package to be uninstalled must at least have a RECORD file in its .dist-info directory for this to have a chance to work. The uninstall done by this tool can only be as complete and correct as that RECORD file allows for.

# Usage
```
$ python -m uninstaller --help
usage: python -m uninstaller [-h] [--root path] [--base path] [--scheme scheme] [--not-pure-python] [--ignore-checksums] [--ignore-sizes] [--verbose] package [package ...]

uninstall python packages

positional arguments:
  package               name of the package to uninstall

options:
  -h, --help            show this help message and exit
  --root path, -r path  override package search root
  --base path, -b path  override base path (aka prefix)
  --scheme scheme, -s scheme
                        override the default installation scheme
  --not-pure-python, -n
                        you might need to use this if 'Root-is-Purelib' metadata parameter of the package you want to uninstall is false
  --ignore-checksums, -i
                        use this to skip checksum verification ☠️DANGEROUS☠️
  --ignore-sizes, -z    use this to skip file size verification ☠️DANGEROUS☠️
  --verbose, -v         print every file that's removed to stdout
```
`--ignore-sizes` and `--ignore-checksums` are particularly dangerous arguments to use because they bypass validation of files you're about to delete. These switches when paired with a maliciously crafted RECORD file can delete anything your user has the permissions to delete (although they don't completely protect you from a maliciously crafted RECORD file. If you avoid using these, you're pretty safe from a crafted RECORD file because an evil genius would need to know the checksum, size and location of the file(s) they want this tool to delete).
