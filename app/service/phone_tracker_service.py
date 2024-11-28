from datetime import datetime
from typing import Dict, Optional, Tuple

from app.db.models import Device, Interaction
from app.repository.tracker_repository import (
    create_tracker_data,
    check_device_interaction_at_time,
    find_bluetooth_paths,
    check_direct_connection,
    find_strong_connections,
    find_device_connections_count,
    find_device_latest_interaction
)


def is_same_device(device1_id: str, device2_id: str) -> bool:
    return device1_id == device2_id


def check_devices_available(from_device: str, to_device: str, timestamp: datetime) -> Tuple[bool, str]:
    if is_same_device(from_device, to_device):
        return False, "Self interaction is not allowed"

    if check_device_interaction_at_time(from_device, timestamp):
        return False, f"Device {from_device} already has an interaction at {timestamp}"

    if check_device_interaction_at_time(to_device, timestamp):
        return False, f"Device {to_device} already has an interaction at {timestamp}"

    return True, ""


def process_phone_tracker_data(data: Dict) -> Optional[Dict]:
    try:
        interaction_data = data['interaction']
        timestamp = datetime.fromisoformat(interaction_data['timestamp'])

        devices_available, error_message = check_devices_available(
            interaction_data['from_device'],
            interaction_data['to_device'],
            timestamp
        )

        if not devices_available:
            return {
                'status': 'error',
                'message': error_message
            }

        devices = [
            Device(
                id=device_data['id'],
                name=device_data['name'],
                brand=device_data['brand'],
                model=device_data['model'],
                os=device_data['os'],
                latitude=device_data['location']['latitude'],
                longitude=device_data['location']['longitude'],
                altitude_meters=device_data['location']['altitude_meters'],
                accuracy_meters=device_data['location']['accuracy_meters']
            )
            for device_data in data['devices']
        ]

        interaction = Interaction(
            from_device=interaction_data['from_device'],
            to_device=interaction_data['to_device'],
            method=interaction_data['method'],
            bluetooth_version=interaction_data['bluetooth_version'],
            signal_strength_dbm=interaction_data['signal_strength_dbm'],
            distance_meters=interaction_data['distance_meters'],
            duration_seconds=interaction_data['duration_seconds'],
            timestamp=timestamp
        )

        result = create_tracker_data(devices, interaction)
        return result

    except KeyError as e:
        print(f"Missing required field in data: {e}")
        return None
    except ValueError as e:
        print(f"Invalid data format: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing tracker data: {e}")
        return None


# 2
def get_bluetooth_paths() -> Optional[Dict]:
    try:
        paths = find_bluetooth_paths()
        if paths is None:
            return {
                'status': 'error',
                'message': 'Failed to fetch Bluetooth paths'
            }

        if not paths:
            return {
                'status': 'success',
                'message': 'No Bluetooth paths found',
                'data': []
            }

        return {
            'status': 'success',
            'data': paths
        }
    except Exception as e:
        print(f"Error in get_bluetooth_paths: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


# 3
def get_strong_signal_connections(min_strength: int = -60) -> Optional[Dict]:
    try:
        connections = find_strong_connections(min_strength)
        if connections is None:
            return {
                'status': 'error',
                'message': 'Failed to fetch strong connections'
            }
        return {
            'status': 'success',
            'data': connections
        }
    except Exception as e:
        print(f"Error in get_strong_signal_connections: {e}")
        return None


# 4
def get_device_connections_count(device_id: str) -> Dict:
    try:
        stats = find_device_connections_count(device_id)
        if stats is None:
            return {
                'status': 'error',
                'message': f'Device {device_id} not found'
            }

        return {
            'status': 'success',
            'data': stats
        }
    except Exception as e:
        print(f"Error in get_device_connections_count: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


# 5
def check_devices_connection(device1_id: str, device2_id: str) -> Optional[Dict]:
    try:
        connection_info = check_direct_connection(device1_id, device2_id)
        if connection_info is None:
            return {
                'status': 'error',
                'message': 'Failed to check connection between devices'
            }
        return {
            'status': 'success',
            'data': connection_info
        }
    except Exception as e:
        print(f"Error in check_devices_connection: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


# 6
def get_device_latest_interaction(device_id: str) -> Dict:
    try:
        latest = find_device_latest_interaction(device_id)
        if latest is None:
            return {
                'status': 'error',
                'message': f'No interactions found for device {device_id}'
            }

        return {
            'status': 'success',
            'data': latest
        }
    except Exception as e:
        print(f"Error in get_device_latest_interaction: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }
