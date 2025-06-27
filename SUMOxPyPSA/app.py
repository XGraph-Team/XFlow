from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import traci
import time
import threading
import os
import sys
import tempfile
from config import *
from sumo_config import SUMO_COMMON_CONFIG, CITY_CONFIGS as SUMO_CITY_CONFIGS

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['SECRET_KEY'] = 'A34F6g7JK0c5N'
socketio = SocketIO(app, async_mode='threading')

# Get SUMO binary path from config
SUMO_BINARY = os.path.join(SUMO_PATH, "bin/sumo")  # or "sumo-gui" for the GUI version

# Global variables
simulation_running = False
simulation_thread = None
stop_event = threading.Event()
CURRENT_CITY = DEFAULT_CITY

# Traffic light state tracking
traffic_light_states = {}  # Store current state for each traffic light
traffic_light_phases = {}  # Store phase information for each traffic light

def create_temp_sumocfg(city):
    """Create a temporary SUMO configuration file for the city"""
    city_dir = CITY_CONFIGS[city]["working_dir"]
    city_sumo_config = SUMO_CITY_CONFIGS[city.upper()]
    
    # Create temporary file in the city directory
    temp_path = os.path.join(city_dir, "temp.sumocfg")
    with open(temp_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">\n')
        
        # Input files
        f.write('    <input>\n')
        f.write(f'        <net-file value="{os.path.basename(city_sumo_config["net-file"])}"/>\n')
        f.write(f'        <route-files value="{os.path.basename(city_sumo_config["route-files"])}"/>\n')
        f.write(f'        <additional-files value="{os.path.basename(city_sumo_config["additional-files"])}"/>\n')
        f.write('    </input>\n')
        
        # Processing
        f.write('    <processing>\n')
        for key, value in SUMO_COMMON_CONFIG["processing"].items():
            f.write(f'        <{key} value="{value}"/>\n')
        f.write('    </processing>\n')
        
        # Time
        f.write('    <time>\n')
        for key, value in SUMO_COMMON_CONFIG["time"].items():
            f.write(f'        <{key} value="{value}"/>\n')
        f.write('    </time>\n')
        
        f.write('</configuration>\n')
        return temp_path

def sumo_simulation(city=DEFAULT_CITY):
    global simulation_running
    
    if city not in CITY_CONFIGS:
        print(f"City {city} not found in configurations.")
        return
    
    city_config = CITY_CONFIGS[city]
    working_dir = city_config["working_dir"]
    
    print(f"Starting simulation for {city_config['name']}")
    print(f"Working directory: {working_dir}")
    
    # Store current directory to restore later
    original_dir = os.getcwd()
    temp_cfg = None
    
    try:
        # Change to the city's working directory
        os.chdir(working_dir)
        print(f"Changed to directory: {os.getcwd()}")
        
        # Create temporary SUMO configuration
        temp_cfg = create_temp_sumocfg(city)
        print(f"Created temporary config at: {temp_cfg}")
        
        simulation_running = True
        stop_event.clear()
        
        # Start SUMO with the temporary config
        sumo_cmd = [SUMO_BINARY, "-c", os.path.basename(temp_cfg)]
        print(f"Running command: {' '.join(sumo_cmd)}")
        
        try:
            traci.start(sumo_cmd)
            print("Successfully connected to SUMO")
            
            # Switch to our randomized traffic light program (programID '1')
            for tl_id in traci.trafficlight.getIDList():
                try:
                    traci.trafficlight.setProgram(tl_id, "1")
                except:
                    pass  # Ignore errors if program doesn't exist
            
        except Exception as e:
            print(f"Failed to connect to SUMO: {str(e)}")
            raise
        
        # Counter for controlling update frequency
        step_counter = 0
        
        while traci.simulation.getMinExpectedNumber() > 0 and not stop_event.is_set():
            traci.simulationStep()
            step_counter += 1
            
            # Fix traffic light logic to ensure proper cycling
            fix_traffic_light_logic()
            
            # Send updates based on configured frequency
            if step_counter % UPDATE_FREQUENCY == 0:
                # Debug each traffic light
                traffic_lights = []
                for idx, tl_id in enumerate(traci.trafficlight.getIDList()):
                    try:
                        controlled_links = traci.trafficlight.getControlledLinks(tl_id)
                        gps_position = None
                        # Try fromEdge of controlled links
                        if controlled_links and controlled_links[0]:
                            first_link = controlled_links[0][0]
                            from_edge = first_link[0]
                            try:
                                edge_shape = traci.edge.getShape(from_edge)
                                if edge_shape:
                                    gps_position = traci.simulation.convertGeo(*edge_shape[0])
                            except:
                                pass
                        # If not found, try junction position
                        if gps_position is None:
                            try:
                                # First try to get the junction ID that this traffic light controls
                                junction_id = None
                                if controlled_links and controlled_links[0]:
                                    # Get junction from the first controlled link
                                    first_link = controlled_links[0][0]
                                    from_edge = first_link[0]
                                    to_edge = first_link[1]
                                    # Try to find the junction that connects these edges
                                    try:
                                        junction_id = traci.edge.getFromJunction(from_edge)
                                    except:
                                        try:
                                            junction_id = traci.edge.getToJunction(to_edge)
                                        except:
                                            pass
                                
                                # If we found a junction ID, get its position
                                if junction_id:
                                    junction_pos = traci.junction.getPosition(junction_id)
                                    gps_position = traci.simulation.convertGeo(*junction_pos)
                                else:
                                    # Fallback: try using tl_id as junction ID (original approach)
                                    junction_pos = traci.junction.getPosition(tl_id)
                                    gps_position = traci.simulation.convertGeo(*junction_pos)
                            except:
                                # If all else fails, skip this traffic light
                                continue
                        
                        if gps_position is not None:
                            state = traci.trafficlight.getRedYellowGreenState(tl_id)
                            traffic_lights.append({
                                'id': tl_id, 
                                'x': gps_position[0], 
                                'y': gps_position[1], 
                                'state': state
                            })
                    except:
                        # Skip this traffic light if any error occurs
                        continue
                
                # Get traffic light information
                vehicles = []
                for vehicle_id in traci.vehicle.getIDList():
                    position = traci.vehicle.getPosition(vehicle_id)
                    gps_position = traci.simulation.convertGeo(*position)
                    angle = traci.vehicle.getAngle(vehicle_id)
                    vehicles.append({'id': vehicle_id, 'x': gps_position[0], 'y': gps_position[1], 'angle': angle})
                
                # Send both vehicles and traffic lights
                socketio.emit('update', {
                    'vehicles': vehicles,
                    'traffic_lights': traffic_lights
                })
            
            # Use configured simulation speed
            time.sleep(SIMULATION_SPEED)
            
        traci.close()
    except Exception as e:
        print(f"Error in simulation: {e}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
    finally:
        # Clean up temporary file
        if temp_cfg and os.path.exists(temp_cfg):
            os.unlink(temp_cfg)
        # Restore original directory
        os.chdir(original_dir)
        simulation_running = False

@socketio.on('connect')
def handle_connect():
    """Handle client connection - don't start simulation automatically"""
    pass

@socketio.on('change_city')
def handle_change_city(data):
    global simulation_thread, CURRENT_CITY
    
    city = data.get('city', DEFAULT_CITY)
    if city not in CITY_CONFIGS:
        return
    
    CURRENT_CITY = city
    print(f"Changing city to {CITY_CONFIGS[CURRENT_CITY]['name']}")
    
    # Stop current simulation if running
    if simulation_running:
        stop_event.set()
        if simulation_thread:
            simulation_thread.join(timeout=2)
    
    # Start a new simulation with the selected city
    simulation_thread = threading.Thread(target=sumo_simulation, args=(CURRENT_CITY,))
    simulation_thread.start()

@socketio.on('restart')
def handle_restart(data):
    global simulation_thread, CURRENT_CITY
    
    city = data.get('city', CURRENT_CITY)
    if city not in CITY_CONFIGS:
        return
    
    CURRENT_CITY = city
    print(f"Restarting simulation for {CITY_CONFIGS[CURRENT_CITY]['name']}")
    
    # Stop current simulation if running
    if simulation_running:
        stop_event.set()
        if simulation_thread:
            simulation_thread.join(timeout=2)
    
    # Start a new simulation
    simulation_thread = threading.Thread(target=sumo_simulation, args=(CURRENT_CITY,))
    simulation_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

def fix_traffic_light_logic():
    """Fix traffic light logic to ensure proper green-yellow-red-green cycling"""
    global traffic_light_states, traffic_light_phases
    
    for tl_id in traci.trafficlight.getIDList():
        if tl_id not in traffic_light_states:
            traffic_light_states[tl_id] = {
                'current_state': None,
                'last_state': None,
                'state_duration': 0,
                'phase_index': 0
            }
            traffic_light_phases[tl_id] = []
        
        current_state = traci.trafficlight.getRedYellowGreenState(tl_id)
        tl_state = traffic_light_states[tl_id]
        
        # If state changed, update tracking
        if current_state != tl_state['current_state']:
            tl_state['last_state'] = tl_state['current_state']
            tl_state['current_state'] = current_state
            tl_state['state_duration'] = 0
        else:
            tl_state['state_duration'] += 1
        
        # Check for improper transitions and fix them
        if (tl_state['last_state'] and 
            'y' in tl_state['last_state'].lower() and 
            'g' in current_state.lower() and 
            'r' not in tl_state['last_state'].lower()):
            
            # This is a yellow-to-green transition without red - fix it
            print(f"Fixing improper transition for {tl_id}: {tl_state['last_state']} -> {current_state}")
            
            # Force a red state for 2 seconds before allowing green
            if tl_state['state_duration'] < 20:  # 2 seconds at 0.1s step length
                # Create a red state for all lanes
                red_state = 'r' * len(current_state)
                try:
                    traci.trafficlight.setRedYellowGreenState(tl_id, red_state)
                except:
                    pass  # Ignore errors if we can't set the state

if __name__ == "__main__":
    print(f"NYC path: {NYC_PATH}")
    socketio.run(app, debug=True, host=HOST, port=PORT) 