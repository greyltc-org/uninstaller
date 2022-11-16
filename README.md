# uninstaller
counterpart to https://github.com/pypa/installer

# ⚠General Warning⚠
This project uses a bunch of lightly tested logic to decide how to call [`os.unlink()`](https://docs.python.org/3/library/os.html#os.unlink) and [`os.rmdir()`](https://docs.python.org/3/library/os.html#os.rmdir) which make changes to your file system that probably can't be undone. I personally think it's safe (if you're okay with the empty folder warning below) and effective, but it comes with no warranty it won't destroy some data you wish it didn't. That said, I wouldn't run it with root permissions at this point.

# ⚠Empty Folder Warning
This project reads [The RECORD file](https://packaging.python.org/en/latest/specifications/recording-installed-packages/#the-record-file) to figure out how to remove a package. The RECORD file does not contain info on which folders were created during installation (only files), so we can't, with 100% certianty, know which folders should be removed when we try to uninstall a package. After removing all the files listed in RECORD, this project will remove all **empty** folders that were in the chain upwards of where each file in RECORD was. That means it's possible that an empty folder not created at install time will be removed by this tool.

# Usage
Tested with python 3.10 on Linux. It's written to be platform agnostic.
```
EMPTY
```
`--ignore-sizes` and `--ignore-checksums` are particularly dangerous arguments to use because they bypass validation of files you're about to delete. These switches when paired with a maliciously crafted RECORD file can delete anything your user has the permissions to delete (although they don't completely protect you from a maliciously crafted RECORD file. If you avoid using these, you're pretty safe from a crafted RECORD file because an evil genius would need to know the checksum, size and location of the file(s) they want this tool to delete).