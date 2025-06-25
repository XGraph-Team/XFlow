"""
Unified SUMO configuration settings for all cities
"""

import os

# Base directory is where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Common configuration settings for all cities
SUMO_COMMON_CONFIG = {
    'processing': {
        'time-to-teleport': '300',
        'ignore-junction-blocker': '60',
        'collision.action': 'none',
        'collision.stoptime': '0',
        'collision.check-junctions': 'false',
        'ignore-accidents': 'true',
        'lateral-resolution': '0.8',
        'route-steps': '200',
        'no-step-log': 'true',
        'no-internal-links': 'false',
        'ignore-route-errors': 'true'
    },
    'routing': {
        'device.rerouting.adaptation-interval': '1',
        'device.rerouting.adaptation-weight': '0.0',
        'device.rerouting.adaptation-steps': '180',
        'device.rerouting.with-taz': 'false',
        'device.rerouting.init-with-loaded-weights': 'true',
        'device.rerouting.threads': '0',
        'device.rerouting.synchronize': 'true',
        'device.rerouting.output': 'rerouting.xml'
    },
    'time': {
        'step-length': '0.5',
        'start': '0',
        'end': '3600'
    },
    'report': {
        'verbose': 'true',
        'no-step-log': 'true'
    },
    'gui_only': {
        'start': 'true',
        'quit-on-end': 'true'
    }
}

# City-specific configurations
CITY_CONFIGS = {
    "MANCHESTER": {
        "net-file": "osm.net.xml.gz",
        "route-files": "osm.passenger.trips.xml",
        "additional-files": "osm.poly.xml.gz"
    },
    "NEWYORK": {
        "net-file": "osm.net.xml.gz",
        "route-files": "osm.passenger.trips.xml",
        "additional-files": "osm.poly.xml.gz"
    },
    "MIAMI": {
        "net-file": "osm.net.xml.gz",
        "route-files": "osm.passenger.trips.xml",
        "additional-files": "osm.poly.xml.gz"
    },
    "LOSANGELES": {
        "net-file": "osm.net.xml.gz",
        "route-files": "osm.passenger.trips.xml",
        "additional-files": "osm.poly.xml.gz"
    }
} 