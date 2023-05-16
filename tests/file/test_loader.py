from watchml.file.loader import WatchLoader
from watchml.utils import skip_slow_tests
import pytest
from pathlib import Path


@pytest.mark.skipif(skip_slow_tests, reason="Slow")
def test_load_export_root():
    wl = WatchLoader(data_path=Path("tests") / "sample_data")
    root = wl._load_export_root()
    assert root.tag == "HealthData"
