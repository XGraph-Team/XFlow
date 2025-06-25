# SUMOxPyPSA

A web-based traffic simulation system that combines SUMO (Simulation of Urban MObility) with PyPSA (Python for Power System Analysis) for real-time traffic visualization and analysis.

## Overview

SUMOxPyPSA is a Flask-based web application that provides real-time traffic simulation for multiple cities using SUMO. The system allows users to visualize traffic flow, traffic lights, and vehicle movements in an interactive web interface.

## Features

- **Multi-City Support**: Simulate traffic in New York, Miami, and Los Angeles
- **Real-Time Visualization**: Web-based interface showing live traffic simulation
- **Interactive Controls**: Start, stop, and restart simulations
- **Traffic Light Monitoring**: Real-time traffic light state visualization
- **Vehicle Tracking**: Track individual vehicles and their movements
- **WebSocket Communication**: Real-time updates via Socket.IO
- **Configurable Simulation**: Adjustable simulation speed and update frequency

## Prerequisites

- Python 3.7+
- SUMO (Simulation of Urban MObility)
- Flask and Flask-SocketIO
- Required Python packages (see requirements.txt)

## Installation

1. **Install SUMO**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install sumo sumo-tools sumo-doc
   
   # macOS
   brew install sumo
   
   # Windows
   # Download from https://sumo.dlr.de/docs/Downloads.php
   ```

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SUMOxPyPSA
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r tools/requirements.txt
   pip install flask flask-socketio traci
   ```

4. **Configure SUMO path**:
   Edit `config.py` and update the `SUMO_PATH` variable to match your SUMO installation:
   ```python
   # Linux (default)
   SUMO_PATH = "/usr/share/sumo"
   
   # Windows
   SUMO_PATH = "C:\\Program Files (x86)\\Eclipse\\Sumo"
   
   # macOS
   SUMO_PATH = "/opt/homebrew/Cellar/sumo/1.20.0/share/sumo"
   ```

## Usage

1. **Start the web server**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   Open your web browser and navigate to `http://localhost:8080`

3. **Select a city**:
   Use the city selector to choose between New York, Miami, or Los Angeles

4. **Control the simulation**:
   - Click "Start" to begin the simulation
   - Click "Restart" to reset and restart the simulation

## Project Structure

```
SUMOxPyPSA/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── sumo_config.py         # SUMO-specific configurations
├── build.py               # Network building script
├── map_to_power.py        # Map conversion utilities
├── compress_net.py        # Network compression utilities
├── test_db_connection.py  # Database connection testing
├── tools/
│   └── requirements.txt   # Python dependencies
├── templates/
│   └── index.html         # Web interface template
├── static/                # Static web assets
├── new_york/              # New York city data
├── miami/                 # Miami city data
├── los_angeles/           # Los Angeles city data
├── pypsa_network/         # PyPSA network data
└── LICENSE                # MIT License
```

## Configuration

### Simulation Settings

Edit `config.py` to customize simulation parameters:

- `SIMULATION_SPEED`: Controls how fast the simulation runs
- `UPDATE_FREQUENCY`: How often to send updates to the web interface
- `HOST` and `PORT`: Web server configuration

### City Configurations

Each city has its own configuration in `config.py`:

```python
CITY_CONFIGS = {
    "newyork": {
        "cfg_file": "path/to/newyork/osm.sumocfg",
        "name": "New York, USA",
        "working_dir": "path/to/newyork"
    },
    # ... other cities
}
```

## Building Networks

To build SUMO networks for cities:

```bash
python build.py [city_name]
```

Where `city_name` can be:
- `newyork`
- `miami` 
- `losangeles`

## API Endpoints

- `GET /`: Main web interface
- `WebSocket /socket.io`: Real-time communication
  - `change_city`: Switch between cities
  - `restart`: Restart simulation
  - `update`: Real-time simulation data

## Real-Time Data

The application sends real-time data via WebSocket including:

- **Vehicles**: Position, angle, and ID of all vehicles
- **Traffic Lights**: Position, state, and ID of all traffic lights

## Troubleshooting

1. **SUMO not found**: Ensure SUMO is properly installed and the path in `config.py` is correct
2. **Port already in use**: Change the `PORT` in `config.py`
3. **City data missing**: Ensure city directories contain proper SUMO configuration files

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- SUMO Development Team for the traffic simulation framework
- PyPSA Development Team for the power system analysis tools
- Flask and Socket.IO communities for the web framework

## Support

For issues and questions, please open an issue on the project repository.
