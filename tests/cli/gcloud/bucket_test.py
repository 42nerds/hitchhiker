import os
from pathlib import PosixPath
from unittest.mock import MagicMock, call

import pytest
from click.testing import CliRunner

bucket = pytest.importorskip("hitchhiker.cli.gcloud.bucket").bucket_group

from google.cloud import storage  # noqa: E402


def test_sync_folder_noabs():
    storage.Client = MagicMock()

    result = CliRunner().invoke(bucket, ["sync-folder", "test bucket", "/badpath", "test directory/helloworld/"])
    assert result.exit_code == 1
    assert "Expected absolute path for bucket_path\n" in result.output


def test_sync_folder_allnew(tmp_path):
    os.mkdir(tmp_path / "dir")
    os.mkdir(tmp_path / "dir" / "dir 2")
    os.mkdir(tmp_path / "dir" / "dir 2" / "empty")
    files = [
        "file1.txt",
        "file2.txt",
        "dir/dir_file.txt",
        "dir/dir_file2.txt",
        "dir/dir 2/dir2_file1.txt",
        "dir/dir 2/dir2_file2.txt",
        "dir/dir 2/dir2_file3.txt",
    ]

    for file in [tmp_path / file for file in files]:
        open(file, "w").close()

    storage.Client = MagicMock()

    result = CliRunner().invoke(bucket, ["sync-folder", "test bucket", str(tmp_path), "/test directory/helloworld/"])
    assert result.exit_code == 0
    assert f"uploading {tmp_path / 'file1.txt'} to test directory/helloworld/file1.txt\n" in result.output

    storage.Client.assert_called_once()
    storage.Client().list_blobs.assert_called_once_with("test bucket")
    storage.Client().bucket.assert_called_once_with("test bucket")

    storage.Client().bucket().blob.assert_has_calls([call(f"test directory/helloworld/{file}") for file in files], any_order=True)
    assert len(storage.Client().bucket().blob.mock_calls) == len(files) * 2

    storage.Client().bucket().blob().upload_from_filename.assert_has_calls([call(PosixPath(tmp_path / file), if_generation_match=0) for file in files], any_order=True)
    assert len(storage.Client().bucket().blob().upload_from_filename.mock_calls) == len(files)


def test_sync_folder_presynced(tmp_path):
    os.mkdir(tmp_path / "dir")
    os.mkdir(tmp_path / "dir" / "dir 2")
    os.mkdir(tmp_path / "dir" / "dir 2" / "empty")
    files = [
        "file1.txt",
        "file2.txt",
        "dir/dir_file.txt",
        "dir/dir_file2.txt",
        "dir/dir 2/dir2_file1.txt",
        "dir/dir 2/dir2_file2.txt",
        "dir/dir 2/dir2_file3.txt",
    ]

    for file in [tmp_path / file for file in files]:
        open(file, "w").close()

    storage.Client = MagicMock()

    storage.Client().list_blobs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    storage.Client().list_blobs.return_value[0].name = "test directoryx/helloworld/file1.txt"
    storage.Client().list_blobs.return_value[1].name = "test directory/helloworld/x/file1.txt"
    storage.Client().list_blobs.return_value[2].name = "test directory/helloworld/file2.txt"
    storage.Client().list_blobs.return_value[3].name = "test directory/helloworld/dir/dir 2/dir2_file3.txt"
    files.remove("file2.txt")
    files.remove("dir/dir 2/dir2_file3.txt")

    result = CliRunner().invoke(bucket, ["sync-folder", "another test bucket", str(tmp_path), "/test directory/helloworld/"])
    assert result.exit_code == 0
    assert f"uploading {tmp_path / 'file1.txt'} to test directory/helloworld/file1.txt\n" in result.output

    storage.Client().list_blobs.assert_called_with("another test bucket")
    storage.Client().bucket.assert_called_once_with("another test bucket")

    storage.Client().bucket().blob.assert_has_calls([call(f"test directory/helloworld/{file}") for file in files], any_order=True)
    assert len(storage.Client().bucket().blob.mock_calls) == len(files) * 2

    storage.Client().bucket().blob().upload_from_filename.assert_has_calls([call(PosixPath(tmp_path / file), if_generation_match=0) for file in files], any_order=True)
    assert len(storage.Client().bucket().blob().upload_from_filename.mock_calls) == len(files)
