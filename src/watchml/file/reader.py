import os
import xml.etree.ElementTree as ET
from typing import List, Tuple

import pandas as pd

from watchml.data import ECG, WorkoutRoute

WorkoutElement = ET.Element

class WatchReader:
    def __init__(self, data_path: str, export_name: str):
        self.export_name = export_name
        self.data_path = os.path.join(data_path, f"apple_health_export_{export_name}")
        self.cache_path = os.path.join("cache", self.export_name)

    def _ecg_data(self, ecg_name: str) -> Tuple[List[float], dict]:
        with open(f"{self.data_path}/electrocardiograms/{ecg_name}", "r") as f:
            ecg = f.read()

            data = ecg.split("\n")
            m_data = data[:12]
            meta_data = {}
            for m in m_data:
                if (
                    m != "" and "," in m
                ):  # makes sure that the row isnt empty and that it is a key,value pair
                    x = m.split(",")
                    if len(x) == 3:  # if commas were used instead of points for floats
                        meta_data[x[0]] = x[1] + "." + x[2]
                    else:
                        meta_data[x[0]] = x[1]

            data = data[13:]

            values = []
            for d in data:
                if d != "":
                    values.append(float(d.replace(",", ".")))

            return values, meta_data

    def ecgs(self):
        for file in os.listdir(os.path.join(self.data_path, "electrocardiograms")):
            values, meta_data = self._ecg_data(file)
            yield ECG(values, meta_data)

    def activity_summary(self):
        return pd.read_csv(os.path.join(self.cache_path, "activity_summary.csv"))

    def workouts(self):
        return pd.read_csv(os.path.join(self.cache_path, "workouts.csv"))

    def workout_events(self):
        return pd.read_csv(os.path.join(self.cache_path, "workout_events.csv"))

    def tracks_meta(self):
        return pd.read_csv(os.path.join(self.cache_path, "tracks_meta.csv"))

    def track(self, workout_id: str):
        return pd.read_csv(os.path.join(self.cache_path, "tracks", f"{workout_id}.csv"))

    def tracks(self) -> List[WorkoutRoute]:
        tracks = []
        for row in self.tracks_meta().itertuples():
            track_df = self.track(row.workout_uuid)
            track = WorkoutRoute(track_df=track_df, uuid=row.workout_uuid, gpx_path=row.path)
            tracks.append(track)
        return tracks

    def workout_metadata_entry(self, workout_id: str):
        return pd.read_csv(
            os.path.join(self.cache_path, "workout_metadata_entry", f"{workout_id}.csv")
        )

    def workout_statistics(self, workout_id: str):
        return pd.read_csv(
            os.path.join(self.cache_path, "workout_statistics", f"{workout_id}.csv")
        )

    @property
    def metadata(self):
        return pd.read_csv(os.path.join(self.cache_path, "metadata.csv"))

    def records(self):
        for file in os.listdir(os.path.join(self.cache_path, "records")):
            yield pd.read_csv(os.path.join(self.cache_path, "records", file))

    def record(self, record_type: str):
        return pd.read_csv(
            os.path.join(self.cache_path, "records", f"{record_type}.csv")
        )

    @property
    def record_types(self):
        return [
            file.split(".")[0]
            for file in os.listdir(os.path.join(self.cache_path, "records"))
        ]
