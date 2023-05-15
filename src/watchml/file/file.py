import os
from pathlib import Path
from typing import List

import pandas as pd


class FileSystemManager:
    @staticmethod
    def scaffold_paths(paths: List[Path | str]):
        """Generates folder for every path in paths when it doesn't exist yet.

        Parameters
        ----------
        paths : List[Path | str]
            List of paths/folders to generate.
        """

        for path in paths:
            if not os.path.exists(path):
                os.mkdir(path)

    @staticmethod
    def to_processed(path: Path | str, df: pd.DataFrame, name: str):
        df.to_csv(path / f"{name}.csv", index=False)

    @staticmethod
    def delete_files_in(path: Path | str):
        path = Path(path)
        for file in os.listdir(path):
            print(f"Deleting {file}")
            os.remove(path / file)
