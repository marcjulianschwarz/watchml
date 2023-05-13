import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime as dt
from typing import List, Tuple
from uuid import uuid4
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd

WorkoutElement = ET.Element


class ECG:
    def __init__(self, values: List[float], meta_data: dict):
        self.values = values
        self.meta_data = meta_data

    def plot(self):
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.plot(self.values)
        ax.set_xlabel("Time")
        ax.set_ylabel("Voltage (mV)")
        plt.show()
        return fig


class Track:
    def __init__(
        self, track_df: pd.DataFrame, uuid: str, gpx_path: str, workout_type=None
    ):
        self.track_df = track_df
        self.uuid = uuid
        self.gpx_path = gpx_path
        self.workout_type = workout_type

    def __repr__(self):
        return f"Track(uid={self.uuid}, gpx_path={self.gpx_path})"

    @property
    def start_time(self):
        return self.track_df["time"].min()

    @property
    def end_time(self):
        return self.track_df["time"].max()

    @property
    def lon(self):
        return self.track_df.lon

    @property
    def lat(self):
        return self.track_df.lat

    @property
    def time(self):
        return self.track_df.time

    def plot(self, figsize=(10, 10), return_fig=False):
        fig, ax = plt.subplots(figsize=figsize)
        ax.scatter(self.lon, self.lat, s=2)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        if return_fig:
            return fig

    def plot_elevation(self, figsize=(15, 4), return_fig=False):
        self.track_df["time"] = pd.to_datetime(self.track_df.time)
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(self.track_df.time, self.track_df.elevation)
        ax.tick_params(axis="x", rotation=45)
        timeFmt = DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(timeFmt)
        ax.set_xlabel("Time")
        ax.set_ylabel("Elevation (m)")
        ax.set_title(f"Elevation for track {self.start_time}")
        if return_fig:
            return fig


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

    def tracks(self) -> List[Track]:
        tracks = []
        for row in self.tracks_meta().itertuples():
            track_df = self.track(row.workout_uuid)
            track = Track(track_df=track_df, uuid=row.workout_uuid, gpx_path=row.path)
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


class WatchLoader:
    def __init__(self, data_path: str, export_name: str):
        self.export_name = export_name
        self.data_path = os.path.join(data_path, f"apple_health_export_{export_name}")
        self.cache_path = os.path.join("cache", self.export_name)

    def load_export_root(self) -> ET.Element:
        tree = ET.parse(f"{self.data_path}/Export.xml")
        root = tree.getroot()
        return root

    def _scaffold_paths(self, paths: List[str]):
        """Generates folder for every path in paths when it doesn't exist yet.

        Parameters
        ----------
        paths : List[str]
            List of paths/folders to generate.
        """

        for path in paths:
            if not os.path.exists(path):
                os.mkdir(path)

    def _scaffolding(self):

        paths = [
            self.cache_path,
            os.path.join(self.cache_path, "workout_statistics"),
            os.path.join(self.cache_path, "tracks"),
            os.path.join(self.cache_path, "workout_metadata_entry"),
            os.path.join(self.cache_path, "records"),
        ]

        if not os.path.exists("cache"):
            os.mkdir("cache")
            self._scaffold_paths(paths)
        else:
            self._scaffold_paths(paths)

    def create_record_files(self, root: ET.Element):
        """Loads the records from the root element and saves them to individual csv files based on the record type.
        The files are stored under cache/{export_name}/records/{record_type}.csv

        Parameters
        ----------
        root : ET.Element
            The root element of the Export.xml file from Apple Health.
        export_name : str, optional
            Name of the subdirectory in which to save the files, by default "marc"
        """

        records = root.findall("Record")
        record_attribs = [record.attrib for record in records]
        record_df = pd.DataFrame(record_attribs)

        unique_record_types = record_df["type"].unique()
        for record_type in unique_record_types:
            record_sub_df = record_df.loc[record_df["type"] == record_type]
            self._to_cache(record_sub_df, f"records/{record_type}")

    def _create_record_file(self, root: ET.Element):

        records = root.findall("Record")
        record_attribs = [record.attrib for record in records]
        record_df = pd.DataFrame(record_attribs)
        record_df.to_csv(os.path.join(self.cache_path, "records.csv"), index=False)

    def _to_cache(self, df: pd.DataFrame, name):
        df.to_csv(os.path.join(self.cache_path, f"{name}.csv"), index=False)

    def _create_workout_event_file(self, workout: WorkoutElement, workout_id: str):
        event_attributes = []
        events = workout.findall("WorkoutEvent")
        for event in events:
            event.attrib["workout_uuid"] = workout_id
        event_attribs = [event.attrib for event in events]
        event_attributes.extend(event_attribs)

        events_df = pd.DataFrame(event_attributes)
        self._to_cache(events_df, "workout_events")

    def _create_track_files(self, track_root: WorkoutElement, workout_id: str):
        ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
        tracks = track_root.findall("gpx:trk", ns)

        track_data = {
            "lon": [],
            "lat": [],
            "time": [],
            "elevation": [],
            "speed": [],
            "course": [],
            "hAcc": [],
            "vAcc": [],
        }

        for track in tracks:
            track_segments = track.findall("gpx:trkseg", ns)
            for track_segment in track_segments:
                track_points = track_segment.findall("gpx:trkpt", ns)
                for track_point in track_points:

                    elevation = track_point.find("gpx:ele", ns).text
                    time = track_point.find("gpx:time", ns).text

                    extension = track_point.find("gpx:extensions", ns)

                    lon = track_point.get("lon")
                    lat = track_point.get("lat")
                    speed = extension.find("gpx:speed", ns).text
                    course = extension.find("gpx:course", ns).text
                    hAcc = extension.find("gpx:hAcc", ns).text
                    vAcc = extension.find("gpx:vAcc", ns).text

                    track_data["lon"].append(float(lon))
                    track_data["lat"].append(float(lat))
                    track_data["elevation"].append(float(elevation))
                    track_data["time"].append(time)
                    track_data["speed"].append(float(speed))
                    track_data["course"].append(float(course))
                    track_data["hAcc"].append(float(hAcc))
                    track_data["vAcc"].append(float(vAcc))

        track_df = pd.DataFrame(track_data)
        self._to_cache(track_df, f"tracks/{workout_id}")

    def _create_statistics_file(self, workout: WorkoutElement, workout_id: str):
        statistics = workout.findall("WorkoutStatistics")
        statistic_attribs = [statistic.attrib for statistic in statistics]
        statistic_df = pd.DataFrame(statistic_attribs)
        self._to_cache(statistic_df, f"workout_statistics/{workout_id}")

    def _create_meta_data_entry_file(self, workout: WorkoutElement, workout_id: str):
        metadata_entries = workout.findall("MetadataEntry")
        metadata_entry_attribs = [
            {metadata_entry.attrib["key"]: metadata_entry.attrib["value"]}
            for metadata_entry in metadata_entries
        ]
        metadata_entry_df = pd.DataFrame(metadata_entry_attribs)
        self._to_cache(metadata_entry_df, f"workout_metadata_entry/{workout_id}")

    def create_workout_files(
        self,
        root: ET.Element = None,
    ):
        """
        Parameters
        ----------
        root : ET.Element
            The root element of the Export.xml file from Apple Health.
        export_name : str, optional
            Name of the subdirectory in which to save the files, by default "marc"
        """

        if root is None:
            root = self.load_export_root()

        workouts = root.findall("Workout")

        workout_attributes = []
        track_attributes = []

        for workout in workouts:
            # Generate unique id for each workout to be able to join workouts with events, tracks, etc.
            workout_id = uuid4()
            workout.attrib["uuid"] = workout_id
            workout_attributes.append(workout.attrib)

            self._create_workout_event_file(workout, workout_id)

            tracks = workout.findall("WorkoutRoute")

            for track in tracks:
                track.attrib["workout_uuid"] = workout_id
                file_ref = track.find("FileReference")
                if file_ref is not None:
                    track_path = file_ref.attrib["path"]
                    track.attrib["path"] = track_path
                    track_path = os.path.join(self.data_path, track_path[1:])
                    track_tree = ET.parse(track_path)
                    route_root = track_tree.getroot()

                    self._create_track_files(route_root, workout_id)

            track_attribs = [route.attrib for route in tracks]
            track_attributes.extend(track_attribs)

            self._create_statistics_file(workout, workout_id)
            self._create_meta_data_entry_file(workout, workout_id)

        workouts_df = pd.DataFrame(workout_attributes)
        routes_meta_df = pd.DataFrame(track_attributes)

        self._to_cache(workouts_df, "workouts")
        self._to_cache(routes_meta_df, "tracks_meta")

    def _delete_files(self, path: str):
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))

    def _load_metadata(self, root: ET.Element):
        locale = root.attrib["locale"]
        metadata_node = root.find("Me").attrib
        export_date = root.find("ExportDate").attrib["value"]

        metadata_df = pd.DataFrame(metadata_node, index=[0])
        metadata_df["locale"] = locale
        metadata_df["export_date"] = export_date
        self._to_cache(metadata_df, "metadata")

    def reload_data(
        self,
        root: ET.Element = None,
    ):

        self._scaffolding()

        if root is None:
            print("Reading Export.xml file.")
            root = self.load_export_root()

        print("Updating cache info.")
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)
        with open(os.path.join(self.cache_path, "cache.json"), "w") as f:
            content = {
                "last_updated": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            f.write(json.dumps(content))

        print("Deleting Workout Statistics.")
        self._delete_files(os.path.join(self.cache_path, "workout_statistics"))
        print("Deleting Tracks.")
        self._delete_files(os.path.join(self.cache_path, "tracks"))
        print("Deleting Workout Metadata Entries.")
        self._delete_files(os.path.join(self.cache_path, "workout_metadata_entry"))

        print("Loading Metadata.")
        self._load_metadata(root)

        print("Loading Activity Summaries.")
        activity_summary_nodes = root.findall("ActivitySummary")
        activity_summary_attributes = [
            activity_summary_node.attrib
            for activity_summary_node in activity_summary_nodes
        ]
        activity_summary_df = pd.DataFrame(activity_summary_attributes)
        self._to_cache(activity_summary_df, "activity_summary")

        print("Loading Workouts.")
        self.create_workout_files(root)
        print("Loading Health Records.")
        self.create_record_files(root)
