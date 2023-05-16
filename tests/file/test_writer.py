from pathlib import Path

from watchml.file import WatchWriter

ww = WatchWriter(
    data_path=Path("tests") / "sample_data",
    cache_path=Path("tests") / "sample_data/cache",
)


def test_scaffold_folder_structure():
    ww.scaffold_folder_structure()
    assert (Path("tests") / "sample_data/cache/workout_statistics").exists()
    assert (Path("tests") / "sample_data/cache/routes").exists()
    assert (Path("tests") / "sample_data/cache/workout_metadata_entries").exists()
    assert (Path("tests") / "sample_data/cache/records").exists()


# def test_write_record_files():
#     ww.scaffold_folder_structure()
#     ww.write_record_files(record_df=None)
