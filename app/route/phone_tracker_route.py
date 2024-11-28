from flask import Blueprint, request, jsonify

from app.utils.datetime_handler_util import format_response_datetime
from app.service.phone_tracker_service import (
    process_phone_tracker_data,
    get_strong_signal_connections,
    check_devices_connection,
    get_bluetooth_paths,
    get_device_connections_count,
    get_device_latest_interaction
)

phone_tracker_bp = Blueprint('phone_tracker', __name__)


# 1
@phone_tracker_bp.route('/phone_tracker', methods=['POST'])
def track_interaction():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = process_phone_tracker_data(data)
        print(result)

        if result:
            formatted_result = format_response_datetime(result)
            return jsonify({
                'status': 'success',
                'message': 'Interaction tracked successfully',
                'data': formatted_result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to process interaction'
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# 2
@phone_tracker_bp.route('/connections/bluetooth/paths', methods=['GET'])
def get_bluetooth_paths_route():
    try:
        result = get_bluetooth_paths()
        if not result:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch Bluetooth paths'
            }), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# 3
@phone_tracker_bp.route('/connections/strong', methods=['GET'])
def get_strong_signal_connections_route():
    try:
        min_strength = request.args.get('min_strength', default=-60, type=int)
        result = get_strong_signal_connections(min_strength)

        if not result:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch strong connections'
            }), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# 4
@phone_tracker_bp.route('/device/<device_id>/connections/count', methods=['GET'])
def get_device_connections_count_route(device_id: str):
    try:
        result = get_device_connections_count(device_id)

        if result['status'] == 'error':
            return jsonify(result), 404

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# 5
@phone_tracker_bp.route('/connections/direct/<device1_id>/<device2_id>', methods=['GET'])
def check_direct_connection_route(device1_id: str, device2_id: str):
    try:
        result = check_devices_connection(device1_id, device2_id)
        if not result:
            return jsonify({
                'status': 'error',
                'message': 'Failed to check direct connection'
            }), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# 6
@phone_tracker_bp.route('/device/<device_id>/latest', methods=['GET'])
def get_device_latest_interaction_route(device_id: str):
    try:
        result = get_device_latest_interaction(device_id)

        if result['status'] == 'error':
            return jsonify(result), 404

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
