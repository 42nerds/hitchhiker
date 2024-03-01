import os
import shutil
import tempfile
import zipfile
from contextlib import contextmanager
from typing import BinaryIO, Iterator


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
        if not os.path.isdir(self.path):
            os.mkdir(self.path)

    def add_dir(self, src: str, dst: str) -> None:
        shutil.copytree(src, os.path.join(self.path, dst))

    def add_file(self, src: str, dst: str) -> None:
        shutil.copyfile(src, os.path.join(self.path, dst))

    def write(self, stream: BinaryIO, filename: str) -> None:
        with open(os.path.join(self.path, filename), "wb") as f:
            shutil.copyfileobj(stream, f)

    def close(self) -> None:
        pass

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
}


@contextmanager
def backup(path: str, fmt: str) -> Iterator[GenericBackup]:
    if fmt not in _backup_formats:
        # pylint: disable=broad-exception-raised
        raise Exception("Invalid backup format")
    b = _backup_formats[fmt](path)
    try:
        yield b
    except Exception as e:
        b.destroy()
        raise e
