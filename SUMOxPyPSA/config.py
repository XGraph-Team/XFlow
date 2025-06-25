import os

# SUMO Configuration
# Modify these paths according to your system
SUMO_PATH = "/usr/share/sumo"  # Default for Linux
# Alternative paths for different systems:
# Windows: "C:\\Program Files (x86)\\Eclipse\\Sumo"
# macOS: "/opt/homebrew/Cellar/sumo/1.20.0/share/sumo"

# Web Server Configuration
HOST = "0.0.0.0"  # Allow external connections
PORT = 8080       # Web server port

# Simulation Configuration
SIMULATION_SPEED = 0.025  # Reduced for smoother movement
UPDATE_FREQUENCY = 2     # Update every 2 frames for smoother movement

# City paths are relative to the config file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NYC_PATH = os.path.join(BASE_DIR, "new_york")
MIAMI_PATH = os.path.join(BASE_DIR, "miami")
LA_PATH = os.path.join(BASE_DIR, "los_angeles")

# City configurations
CITY_CONFIGS = {
    "newyork": {
        "cfg_file": os.path.join(NYC_PATH, "osm.sumocfg"),
        "name": "New York, USA",
        "working_dir": NYC_PATH
    },
    "miami": {
        "cfg_file": os.path.join(MIAMI_PATH, "osm.sumocfg"),
        "name": "Miami, USA",
        "working_dir": MIAMI_PATH
    },
    "losangeles": {
        "cfg_file": os.path.join(LA_PATH, "osm.sumocfg"),
        "name": "Los Angeles, USA",
        "working_dir": LA_PATH
    }
}

# Default city
DEFAULT_CITY = "losangeles" 