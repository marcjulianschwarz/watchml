import os
from pathlib import Path
from typing import List

import pandas as pd


class FileSystemManager:
    """Class to manage file system operations."""

    @staticmethod
    def scaffold_paths(paths: List[Path | str]):
        """Creates a folder structure.

        :param paths: A list of paths to create.
        :type paths: List[Path | str]
        """

        for path in paths:
            if not os.path.exists(path):
                os.mkdir(path)

    @staticmethod
    def to_processed(path: Path | str, df: pd.DataFrame, name: str):
        """Saves a dataframe to the processed folder.

        :param path: Path to the processed folder.
        :type path: Path | str
        :param df: The dataframe to save.
        :type df: pd.DataFrame
        :param name: The name of the file.
        :type name: str
        """
        df.to_csv(path / f"{name}.csv", index=False)

    @staticmethod
    def delete_files_in(path: Path | str):
        """Deletes all files in a folder.

        :param path: Path to the folder.
        :type path: Path | str
        """
        path = Path(path)
        if not path.exists():
            return
        for file in os.listdir(path):
            print(f"Deleting {file}")
            os.remove(path / file)
