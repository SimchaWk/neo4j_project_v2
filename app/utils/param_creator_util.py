from typing import Dict

from app.db.models import Device, Interaction


def create_device_params(device: Device) -> Dict:
    return {
        'id': device.id,
        'properties': {
            'name': device.name,
            'brand': device.brand,
            'model': device.model,
            'os': device.os,
            'latitude': device.latitude,
            'longitude': device.longitude,
            'altitude_meters': device.altitude_meters,
            'accuracy_meters': device.accuracy_meters
        }
    }


def create_interaction_params(interaction: Interaction) -> Dict:
    return {
        'from_id': interaction.from_device,
        'to_id': interaction.to_device,
        'method': interaction.method,
        'bluetooth_version': interaction.bluetooth_version,
        'signal_strength_dbm': interaction.signal_strength_dbm,
        'distance_meters': interaction.distance_meters,
        'duration_seconds': interaction.duration_seconds,
        'timestamp': interaction.timestamp.isoformat()
    }
