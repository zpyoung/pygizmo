import errno
import os
import shutil
import stat
from pathlib import Path


def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def remove_glob(glob: str):
    for path in Path(".").rglob(glob):
        shutil.rmtree(path, ignore_errors=False, onerror=handleRemoveReadonly)
        print(f"Remove {path.absolute()}")


def main():
    remove_glob(".pytest_cache")
    remove_glob(".ipynb_checkpoints")
    remove_glob(".mypy_cache")
    remove_glob(".DS_Store")
    remove_glob("__pycache__")
    remove_glob(".pyc")
    remove_glob(".pyo*")


if __name__ == "__main__":
    main()
