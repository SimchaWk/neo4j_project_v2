from typing import Optional, Dict, List
from datetime import datetime
from neo4j import Transaction

from app.db.models import Device, Interaction
from app.db.neo4j_database import driver
from app.utils.param_creator_util import create_device_params, create_interaction_params


def check_device_interaction_at_time(device_id: str, timestamp: datetime) -> bool:
    with driver.session() as session:
        try:
            query = '''
            MATCH (d:Device {id: $device_id})-[r:INTERACTED]-()
            WHERE r.timestamp = datetime($timestamp)
            RETURN count(r) > 0 as has_interaction
            '''

            params = {
                'device_id': device_id,
                'timestamp': timestamp.isoformat()
            }

            result = session.run(query, params).data()
            return result[0]['has_interaction'] if result else False

        except Exception as e:
            print(f"Error checking device interaction at time: {e}")
            return False


def run_tracker_transaction(tx: Transaction, devices: List[Device], interaction: Interaction) -> List[Dict]:
    try:
        device_query = '''
        MERGE (d:Device {id: $id})
        ON CREATE SET d += $properties
        ON MATCH SET d += $properties
        '''

        device_params = [create_device_params(device) for device in devices]
        [tx.run(device_query, params) for params in device_params]

        interaction_query = '''
        MATCH (from:Device {id: $from_id})
        MATCH (to:Device {id: $to_id})
        CREATE (from)-[r:INTERACTED {
            method: $method,
            bluetooth_version: $bluetooth_version,
            signal_strength_dbm: $signal_strength_dbm,
            distance_meters: $distance_meters,
            duration_seconds: $duration_seconds,
            timestamp: datetime($timestamp)
        }]->(to)
        RETURN {
            from_device: from.name,
            to_device: to.name,
            method: r.method,
            bluetooth_version: r.bluetooth_version,
            signal_strength: r.signal_strength_dbm,
            distance: r.distance_meters,
            duration: r.duration_seconds,
            timestamp: toString(r.timestamp)
        } as interaction_data
        '''

        interaction_params = create_interaction_params(interaction)
        result = tx.run(interaction_query, interaction_params)
        return result.data()

    except Exception as e:
        print(f"Error in transaction operations: {e}")
        return []


def create_tracker_data(devices: List[Device], interaction: Interaction) -> Optional[Dict]:
    with driver.session() as session:
        try:
            result = session.execute_write(
                lambda tx: run_tracker_transaction(tx, devices, interaction)
            )
            return result[0] if result else None

        except Exception as e:
            print(f"Error in tracker transaction: {e}")
            return None


# 2
def find_bluetooth_paths() -> Optional[List[Dict]]:
    with driver.session() as session:
        try:
            query = '''
            MATCH (source:Device), (target:Device)
            WHERE source <> target
            MATCH path = shortestPath((source)-[r:INTERACTED*]-(target))
            WHERE ALL(rel in r WHERE rel.method = 'Bluetooth')
            RETURN {
                source_device: {
                    id: source.id,
                    name: source.name
                },
                target_device: {
                    id: target.id,
                    name: target.name
                },
                path_length: length(path),
                connection_exists: true
            } as bluetooth_path
            ORDER BY bluetooth_path.path_length
            '''

            result = session.run(query).data()
            if not result:
                return []

            return [record['bluetooth_path'] for record in result]

        except Exception as e:
            print(f"Error finding bluetooth paths: {e}")
            return None


# 3
def find_strong_connections(min_strength: int = -60) -> Optional[List[Dict]]:
    with driver.session() as session:
        try:
            query = '''
            MATCH (d1:Device)-[r:INTERACTED]->(d2:Device)
            WHERE r.signal_strength_dbm > $min_strength
            RETURN {
                from_device: d1.name,
                to_device: d2.name,
                method: r.method,
                signal_strength: r.signal_strength_dbm,
                distance: r.distance_meters,
                timestamp: toString(r.timestamp)
            } as connection
            ORDER BY r.signal_strength_dbm DESC
            '''

            params = {'min_strength': min_strength}
            result = session.run(query, params).data()
            return [record['connection'] for record in result]

        except Exception as e:
            print(f"Error getting strong connections: {e}")
            return None


# 4
def find_device_connections_count(device_id: str) -> Optional[Dict]:
    with driver.session() as session:
        try:
            query = '''
            MATCH (d:Device {id: $device_id})
            OPTIONAL MATCH (d)-[r:INTERACTED]-()
            WITH d, count(r) as total_connections
            OPTIONAL MATCH (d)-[r2:INTERACTED]-(other:Device)
            WITH d, total_connections, collect(DISTINCT other) as unique_devices
            RETURN {
                device: {
                    id: d.id,
                    name: d.name
                },
                total_connections: total_connections,
                unique_devices_count: size(unique_devices)
            } as connection_stats
            '''

            params = {'device_id': device_id}
            result = session.run(query, params).data()

            if not result or not result[0]['connection_stats']['device']['name']:
                return None

            return result[0]['connection_stats']

        except Exception as e:
            print(f"Error counting device connections: {e}")
            return None


# 5
def check_direct_connection(device1_id: str, device2_id: str) -> Optional[Dict]:
    with driver.session() as session:
        try:
            query = '''
            MATCH (source:Device {id: $device1_id}), (target:Device {id: $device2_id})
            OPTIONAL MATCH (source)-[forward:INTERACTED]->(target)
            OPTIONAL MATCH (target)-[backward:INTERACTED]->(source)
            RETURN {
                devices: {
                    source: {id: source.id, name: source.name},
                    target: {id: target.id, name: target.name}
                },
                connections: {
                    forward: CASE 
                        WHEN forward IS NOT NULL 
                        THEN {exists: true, method: forward.method, timestamp: toString(forward.timestamp)}
                        ELSE {exists: false}
                    END,
                    backward: CASE 
                        WHEN backward IS NOT NULL 
                        THEN {exists: true, method: backward.method, timestamp: toString(backward.timestamp)}
                        ELSE {exists: false}
                    END
                }
            } as connection_info
            '''

            params = {
                'device1_id': device1_id,
                'device2_id': device2_id
            }

            result = session.run(query, params).data()
            return result[0]['connection_info'] if result else None

        except Exception as e:
            print(f"Error checking direct connection: {e}")
            return None


# 6
def find_device_latest_interaction(device_id: str) -> Optional[Dict]:
    with driver.session() as session:
        try:
            query = '''
            MATCH (device:Device {id: $device_id})-[interaction:INTERACTED]-(other:Device)
            RETURN {
                device: {
                    id: device.id,
                    name: device.name
                },
                interaction: {
                    direction: CASE 
                        WHEN startNode(interaction).id = $device_id THEN 'outgoing' 
                        ELSE 'incoming' 
                    END,
                    other_device: {
                        id: other.id,
                        name: other.name
                    },
                    method: interaction.method,
                    signal_strength: interaction.signal_strength_dbm,
                    distance: interaction.distance_meters,
                    bluetooth_version: interaction.bluetooth_version,
                    duration: interaction.duration_seconds,
                    timestamp: toString(interaction.timestamp)
                }
            } as latest_interaction
            ORDER BY interaction.timestamp DESC
            LIMIT 1
            '''

            params = {'device_id': device_id}
            result = session.run(query, params).data()

            if not result:
                return None

            return result[0]['latest_interaction']

        except Exception as e:
            print(f"Error getting device latest interaction: {e}")
            return None
