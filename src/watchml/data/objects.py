from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter


class HKCharacteristicTypeIdentifier(Enum):
    DateOfBirth = "HKCharacteristicTypeIdentifierDateOfBirth"
    BiologicalSex = "HKCharacteristicTypeIdentifierBiologicalSex"
    BloodType = "HKCharacteristicTypeIdentifierBloodType"
    FitzpatrickSkinType = "HKCharacteristicTypeIdentifierFitzpatrickSkinType"
    CardioFitnessMedicationsUse = (
        "HKCharacteristicTypeIdentifierCardioFitnessMedicationsUse"
    )


@dataclass
class HealthData:
    locale: str


@dataclass
class Me:
    dateOfBirth: str
    biologicalSex: str
    bloodType: str
    fitzpatrickSkinType: str
    cardioFitnessMedicationsUse: str


@dataclass
class Record:
    type: str
    unit: str
    value: str
    sourceName: str
    sourceVersion: str
    device: str
    creationDate: str
    startDate: str
    endDate: str


@dataclass
class Workout:
    workoutActivityType: str
    duration: str
    durationUnit: str
    totalDistance: str
    totalDistanceUnit: str
    totalEnergyBurned: str
    totalEnergyBurnedUnit: str
    sourceName: str
    sourceVersion: str
    device: str
    creationDate: str
    startDate: str
    endDate: str


@dataclass
class WorkoutActivity:
    uuid: str
    startDate: str
    endDate: str
    duration: str
    durationUnit: str


@dataclass
class WorkoutEvent:
    type: str
    date: str
    duration: str
    durationUnit: str


@dataclass
class WorkoutStatistics:
    type: str
    startDate: str
    endDate: str
    average: str
    minimum: str
    maximum: str
    sum: str
    unit: str


# @dataclass
# class WorkoutRoute:
#     sourceName: str
#     sourceVersion: str
#     device: str
#     creationDate: str
#     startDate: str
#     endDate: str


class ECG:
    def __init__(self, values: List[float], meta_data: dict, name: str):
        self.values = values
        self.meta_data = meta_data
        self.name = name
        self.date = self.name.split("_")[1]

    def __repr__(self) -> str:
        desc = "\n".join([f"{k}: {v}" for k, v in self.meta_data.items()])
        return f"ECG(\n{desc}\n) -> {self.name}"

    def __getitem__(self, key):
        if key in self.meta_data:
            return self.meta_data[key]
        else:
            raise KeyError(f"Key {key} not found in meta_data")

    def keys(self):
        return self.meta_data.keys()

    def generate_plot(self, path: str):
        plt.switch_backend("Agg")
        fig, ax = plt.subplots(figsize=(20, 7))
        ax.plot(self.values)
        ax.set_title(f"ECG - {self.name}")
        ax.set_xlabel("Time")
        ax.set_ylabel("mV")
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        fig.savefig(path)

    def to_json(self):
        return {
            "name": self.name,
            "values": self.values,
            "metadata": self.meta_data,
            "date": self.date,
        }


@dataclass
class WorkoutRoute:
    route_df: pd.DataFrame
    uuid: str
    gpx_path: str
    workout_type = None

    def __repr__(self):
        return f"Track(uid={self.uuid}, gpx_path={self.gpx_path})"

    @property
    def start_time(self):
        return self.route_df["time"].min()

    @property
    def end_time(self):
        return self.route_df["time"].max()

    @property
    def lon(self):
        return self.route_df.lon

    @property
    def lat(self):
        return self.route_df.lat

    @property
    def time(self):
        return self.route_df.time

    def plot(self, figsize=(10, 10), return_fig=False):
        fig, ax = plt.subplots(figsize=figsize)
        ax.scatter(self.lon, self.lat, s=2)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        if return_fig:
            return fig

    def plot_elevation(self, figsize=(15, 4), return_fig=False):
        self.route_df["time"] = pd.to_datetime(self.route_df.time)
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(self.route_df.time, self.route_df.elevation)
        ax.tick_params(axis="x", rotation=45)
        timeFmt = DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(timeFmt)
        ax.set_xlabel("Time")
        ax.set_ylabel("Elevation (m)")
        ax.set_title(f"Elevation for track {self.start_time}")
        if return_fig:
            return fig
