from __future__ import annotations

import sys
from pathlib import Path, PurePath, PurePosixPath

import click
from google.cloud import storage  # type: ignore[import, import-untyped]


@click.group("bucket")
def bucket_group() -> None:
    """Google Cloud Bucket related commands"""


def _paths_filter_relative_to(
    paths: list[PurePath], folder: PurePath
) -> list[PurePath]:
    """
    takes a list of Paths and returns the ones relative to the folder

    Example:
        paths = [Path("/home/user/Downloads"), Path("/home/user2/test")]
        folder = Path("/home/user")
        returns: [Path("/home/user/Downloads")]
    """
    return [path for path in paths if path.is_relative_to(folder)]


def _path_relative_to_folder(path: PurePath, folder: PurePath) -> PurePath:
    """
    takes a path and removes the parts relative to folder

    Example:
        path = Path("/home/user/Downloads")
        folder = Path("/home/user")
        returns: Path("Downloads")
    """
    return path.parent.relative_to(folder) / path.name


def _paths_relative_to_folder(
    paths: list[PurePath], folder: PurePath
) -> list[PurePath]:
    return [_path_relative_to_folder(path, folder) for path in paths]


@bucket_group.command()
@click.argument("bucket_name")
@click.argument("folder_path")
@click.argument("bucket_path")
def sync_folder(bucket_name: str, folder_path: str, bucket_path: str) -> None:
    folder_path_p = Path(folder_path)
    if not PurePosixPath(bucket_path).is_absolute():
        click.echo("Expected absolute path for bucket_path")
        sys.exit(1)
    bucket_path_p = PurePosixPath(bucket_path).relative_to(PurePosixPath("/"))

    storage_client = storage.Client()

    bucket_files = _paths_filter_relative_to(
        [PurePosixPath(blob.name) for blob in storage_client.list_blobs(bucket_name)],
        bucket_path_p,
    )
    bucket_files = _paths_relative_to_folder(bucket_files, bucket_path_p)

    bucket = storage_client.bucket(bucket_name)

    for file in [path for path in folder_path_p.glob("**/*") if path.is_file()]:
        file_rel = _path_relative_to_folder(file, folder_path_p)
        if file_rel not in bucket_files:
            bucket_dest = str(bucket_path_p / file_rel)
            click.echo(f"uploading {file} to {bucket_dest}")
            blob = bucket.blob(bucket_dest)
            blob.upload_from_filename(file, if_generation_match=0)
