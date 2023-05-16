# def test_delete_old_data():
#     wm = WatchManager(
#         data_path=Path("tests") / "sample_data",
#         cache_path=Path("tests") / "sample_data/cache",
#     )
#     wm.delete_old_data()
#     assert not (Path("tests") / "sample_data/cache/workout_statistics").exists()
#     assert not (Path("tests") / "sample_data/cache/routes").exists()
#     assert not (Path("tests") / "sample_data/cache/workout_metadata_entry").exists()
# def test_update_cache_info():
#     wm = WatchManager(
#         data_path=Path("tests") / "sample_data",
#         cache_path=Path("tests") / "sample_data/cache",
#     )
#     wm.update_cache_info()
#     assert (Path("tests") / "sample_data/cache/cache.json").exists()
