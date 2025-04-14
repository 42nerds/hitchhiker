import os
import pathlib
import shutil
import tempfile
import zipfile
import subprocess
from contextlib import contextmanager
from typing import BinaryIO, Iterator, Set


class GenericBackup:
    def __init__(self, path: str) -> None:
        self.path = path

    def add_dir(self, src: str, dst: str) -> None:
        raise NotImplementedError()

    def add_file(self, src: str, dst: str) -> None:
        raise NotImplementedError()

    def write(self, stream: BinaryIO, filename: str) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    def destroy(self) -> None:
        raise NotImplementedError()


# TODO: tests
class DirectoryBackup(GenericBackup):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        if os.path.exists(self.path):
            raise RuntimeError(f"Backup destination ({path}) already exists")
        pathlib.Path(self.path).mkdir(parents=True)

    def add_dir(self, src: str, dst: str) -> None:
        real_dst = os.path.join(self.path, dst)
        pathlib.Path(real_dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, real_dst)

    def add_file(self, src: str, dst: str) -> None:
        real_dst = os.path.join(self.path, dst)
        pathlib.Path(real_dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, real_dst)

    def write(self, stream: BinaryIO, filename: str) -> None:
        real_dst = os.path.join(self.path, filename)
        pathlib.Path(real_dst).parent.mkdir(parents=True, exist_ok=True)
        with open(os.path.join(self.path, filename), "wb") as f:
            shutil.copyfileobj(stream, f)

    def close(self) -> None:
        pass

    def destroy(self) -> None:
        shutil.rmtree(self.path)


# TODO: tests
class DirectoryRsyncBackup(GenericBackup):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        if os.path.isfile(self.path):
            raise RuntimeError(f"Backup destination ({path}) is a file")
        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
        rsync_exec = shutil.which("rsync")
        if rsync_exec is None:
            raise RuntimeError("rsync executable not found")
        self.rsync_exec = rsync_exec
        # keeps track of which paths rsync was used on, helpful for deleting things that are not meant to exist
        self.rsynced_paths: Set[str] = set()
        # keeps track of which files were created in the destination, also helpful for deleting things
        # that are not meant to exist
        self.files_created: Set[str] = set()

    def add_dir(self, src: str, dst: str) -> None:
        real_dst = os.path.join(self.path, dst)
        pathlib.Path(real_dst).mkdir(parents=True, exist_ok=True)
        self.rsynced_paths.add(real_dst)
        # just to be safe we check if real_dst so we don't delete root.. we call rsync with delete so better be careful
        if not real_dst or not real_dst.strip("/"):
            raise RuntimeError("root as destination with rsync and delete option..")
        subprocess.run(
            [self.rsync_exec, "-avh", "--delete-before", f"{src}/", f"{real_dst}/"],
            check=True,
        )

    def add_file(self, src: str, dst: str) -> None:
        real_dst = os.path.join(self.path, dst)
        pathlib.Path(real_dst).parent.mkdir(parents=True, exist_ok=True)
        self.files_created.add(real_dst)
        shutil.copyfile(src, real_dst)

    def write(self, stream: BinaryIO, filename: str) -> None:
        real_dst = os.path.join(self.path, filename)
        pathlib.Path(real_dst).parent.mkdir(parents=True, exist_ok=True)
        self.files_created.add(real_dst)
        with open(real_dst, "wb") as f:
            shutil.copyfileobj(stream, f)

    def close(self) -> None:
        def is_rsynced_path(path: str) -> bool:
            return any(
                os.path.commonpath([path, rp]) == rp for rp in self.rsynced_paths
            )

        def is_created_file(path: str) -> bool:
            return path in self.files_created

        for root, dirs, files in os.walk(self.path, topdown=True):
            # Skip walking into any rsynced path
            # note: slice assignment
            dirs[:] = [d for d in dirs if not is_rsynced_path(os.path.join(root, d))]

            # Remove untracked files
            for file in files:
                file_path = os.path.join(root, file)
                if not is_created_file(file_path):
                    os.remove(file_path)

        # Now clean up empty directories that are not rsynced
        for root, dirs, _ in os.walk(self.path, topdown=False):
            if is_rsynced_path(root) or root == self.path:
                continue
            try:
                os.rmdir(root)
            except OSError:
                pass  # directory not empty or permission error

    def destroy(self) -> None:
        shutil.rmtree(self.path)


class ZipBackup(GenericBackup):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        if not os.path.exists(self.path):
            # pylint: disable=consider-using-with
            self.file = zipfile.ZipFile(
                self.path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True
            )

    def add_dir(self, src: str, dst: str) -> None:
        prefix_len = len(src) + 1
        for dn, _dirnames, filenames in os.walk(src):
            for fn in filenames:
                path = os.path.normpath(os.path.join(dn, fn))
                if os.path.isfile(path):
                    self.file.write(path, os.path.join(dst, path[prefix_len:]))

    def add_file(self, src: str, dst: str) -> None:
        self.file.write(src, dst)

    def write(self, stream: BinaryIO, filename: str) -> None:
        with tempfile.NamedTemporaryFile("wb") as f:
            shutil.copyfileobj(stream, f)  # type: ignore[misc]
            self.file.write(f.name, filename)

    def close(self) -> None:
        self.file.close()

    def destroy(self) -> None:
        try:
            self.close()
        finally:
            os.unlink(self.path)


_backup_formats = {
    "zip": ZipBackup,
    "dir": DirectoryBackup,
    "dir_rsync": DirectoryRsyncBackup,
}


@contextmanager
def backup(path: str, fmt: str) -> Iterator[GenericBackup]:
    if fmt not in _backup_formats:
        raise RuntimeError("Invalid backup format")
    b = _backup_formats[fmt](path)
    try:
        yield b
        b.close()
    except Exception as e:
        b.close()
        raise e
