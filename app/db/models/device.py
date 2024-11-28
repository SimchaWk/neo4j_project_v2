from dataclasses import dataclass


@dataclass
class Device:
    id: str
    name: str
    brand: str
    model: str
    os: str
    latitude: float
    longitude: float
    altitude_meters: int
    accuracy_meters: int
