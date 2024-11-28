# Phone Tracker System

## Overview

The Phone Tracker System is a Flask-based application that tracks and analyzes interactions between devices. It receives
periodic updates about device interactions and their locations, storing this information in a Neo4j graph database for
analysis and querying.

## Features

- Track device interactions with various methods (WiFi, Bluetooth, NFC)
- Store device information including location data
- Analyze connection patterns between devices
- Query interaction history and statistics
- Monitor signal strengths and connection durations

## Tech Stack

- **Backend**: Python, Flask
- **Database**: Neo4j
- **Data Format**: JSON

## API Endpoints

### POST /api/phone_tracker

Receives device interaction data and stores it in the database.

### GET /api/device/{device_id}/stats

Returns statistics for a specific device.

### GET /api/connections/strong

Returns all connections with strong signal strength (above -60 dbm).

### GET /api/connections/bluetooth/paths

Returns all Bluetooth paths between devices.

### GET /api/connections/direct/{device1_id}/{device2_id}

Checks for direct connections between two specific devices.

### GET /api/device/{device_id}/history

Returns the interaction history for a specific device.

## Setup Requirements

- Python 3.8+
- Neo4j Database
- Flask
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure Neo4j connection in config file
4. Run the application:
   ```bash
   python app/main.py
   ```
