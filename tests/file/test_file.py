from watchml.file.file import FileSystemManager
import os
import pandas as pd


def test_scaffold_paths(tmp_path):
    paths = [tmp_path / "a", tmp_path / "b", tmp_path / "c"]
    FileSystemManager.scaffold_paths(paths)
    for path in paths:
        assert os.path.exists(path)


def test_to_processed(tmp_path):
    path = tmp_path / "test.csv"
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    FileSystemManager.to_processed(tmp_path, df, "test")
    assert os.path.exists(path)


def test_delete_files_in(tmp_path):
    path = tmp_path / "test.csv"
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    FileSystemManager.to_processed(tmp_path, df, "test")
    FileSystemManager.delete_files_in(tmp_path)
    assert not os.path.exists(path)
