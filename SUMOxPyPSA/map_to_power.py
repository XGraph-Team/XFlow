import os
import subprocess
import pandas as pd
import sys

def find_python_executable():
    """Find the appropriate Python executable to use."""
    # Try different possible Python executables
    python_candidates = [
        '/bin/python',
        '/usr/bin/python',
        '/usr/bin/python3',
        'python3',
        'python'
    ]
    
    for python_exe in python_candidates:
        try:
            # Test if the executable exists and works
            result = subprocess.run([python_exe, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"Using Python executable: {python_exe}")
                return python_exe
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    # If none found, use sys.executable as fallback
    print(f"Using fallback Python executable: {sys.executable}")
    return sys.executable

def convert_osm_to_pypsa(osm_file, output_dir, gridkit_script='tools/gridkit.py'):
    """
    Converts an OpenStreetMap file to a PyPSA network format using GridKit.

    Args:
        osm_file (str): Path to the input OSM file (e.g., 'new_york/osm_nyc_bbox.osm.xml.gz').
        output_dir (str): Directory to save the PyPSA-compatible CSV files.
        gridkit_script (str): Path to the GridKit main python script.
    """
    if not os.path.exists(osm_file):
        print(f"Error: OSM file not found at {osm_file}")
        return

    if not os.path.exists(gridkit_script):
        print(f"Error: GridKit script not found at {gridkit_script}")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Find the appropriate Python executable
    python_exe = find_python_executable()

    # --- 1. Run GridKit to extract the power grid ---
    print("Running GridKit to extract power grid from OSM data...")
    # GridKit produces output files in its own directory
    gridkit_dir = os.path.dirname(gridkit_script)
    cmd = [python_exe, gridkit_script, osm_file]
    
    # We must run gridkit from within its directory
    run_dir = os.path.dirname(gridkit_script)
    
    try:
        # Note: We pass the absolute path to the osm_file now
        abs_osm_file = os.path.abspath(osm_file)
        
        # Add the 'util' directory to the python path for the subprocess
        env = os.environ.copy()
        util_path = os.path.join(run_dir, 'util')
        env['PYTHONPATH'] = f"{util_path}:{env.get('PYTHONPATH', '')}"
        
        # Set PostgreSQL environment variables to avoid interactive prompts
        env['PGUSER'] = 'gridkit'  # Use the gridkit user we created
        env['PGHOST'] = 'localhost'
        env['PGPORT'] = '5432'
        env['PGDATABASE'] = 'gridkit'
        env['PGPASSWORD'] = 'gridkit123'  # Password for gridkit user
        
        print(f"Running command: {python_exe} {os.path.basename(gridkit_script)} {abs_osm_file} --no-interactive")
        print(f"Working directory: {run_dir}")
        print(f"Environment variables: PGUSER={env['PGUSER']}, PGHOST={env['PGHOST']}, PGDATABASE={env['PGDATABASE']}")
        
        result = subprocess.run([python_exe, os.path.basename(gridkit_script), abs_osm_file, '--no-interactive'], 
                              cwd=run_dir, env=env, capture_output=True, text=True)
        
        print(f"GridKit exit code: {result.returncode}")
        if result.stdout:
            print(f"GridKit stdout: {result.stdout}")
        if result.stderr:
            print(f"GridKit stderr: {result.stderr}")
            
        if result.returncode != 0:
            print(f"Error running GridKit: Command returned non-zero exit status {result.returncode}")
            return
            
        print("GridKit processing complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error running GridKit: {e}")
        print(f"GridKit stdout: {e.stdout}")
        print(f"GridKit stderr: {e.stderr}")
        return
    except FileNotFoundError as e:
        print(f"Error: Python executable not found: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    # --- 2. Process GridKit's output ---
    print("Converting GridKit output to PyPSA format...")
    vertices_file = os.path.join(run_dir, 'gridkit-highvoltage-vertices.csv')
    edges_file = os.path.join(run_dir, 'gridkit-highvoltage-edges.csv')

    if not os.path.exists(vertices_file) or not os.path.exists(edges_file):
        print("Error: GridKit did not produce the expected output files.")
        return

    # Read GridKit output
    vertices_df = pd.read_csv(vertices_file)
    edges_df = pd.read_csv(edges_file)

    # --- 3. Create PyPSA buses.csv ---
    # Map GridKit vertices to PyPSA buses
    buses = pd.DataFrame()
    buses['id'] = 'Bus ' + vertices_df['id'].astype(str)
    buses['x'] = vertices_df['lon']
    buses['y'] = vertices_df['lat']
    buses['v_nom'] = vertices_df['voltage'].fillna(220) # Default voltage if not specified
    buses['control'] = 'PV' # Assume all are PV buses for simplicity
    
    # Save buses.csv
    buses_path = os.path.join(output_dir, 'buses.csv')
    buses.to_csv(buses_path, index=False)
    print(f"Created buses.csv at {buses_path}")

    # --- 4. Create PyPSA lines.csv ---
    # Map GridKit edges to PyPSA lines
    lines = pd.DataFrame()
    lines['id'] = 'Line ' + edges_df.index.astype(str)
    lines['bus0'] = 'Bus ' + edges_df['v0'].astype(str)
    lines['bus1'] = 'Bus ' + edges_df['v1'].astype(str)
    lines['x'] = 0.0001 # Placeholder for reactance
    lines['r'] = 0.0001 # Placeholder for resistance
    lines['s_nom'] = 1000  # Placeholder for nominal power (MVA)

    # Save lines.csv
    lines_path = os.path.join(output_dir, 'lines.csv')
    lines.to_csv(lines_path, index=False)
    print(f"Created lines.csv at {lines_path}")

    print("\nPyPSA network files created successfully!")


if __name__ == '__main__':
    # --- Configuration ---
    # Note: This assumes you have the uncompressed OSM file.
    
    osm_input_gz = 'new_york/osm_nyc_bbox.osm.xml.gz'
    osm_input_uncompressed = 'new_york/osm_nyc_bbox.osm.xml'
    
    pypsa_output_dir = 'pypsa_network/new_york'

    # --- Run the conversion ---
    if os.path.exists(osm_input_uncompressed):
        convert_osm_to_pypsa(osm_input_uncompressed, pypsa_output_dir, gridkit_script='tools/gridkit.py')
    else:
        # Try to uncompress first
        if os.path.exists(osm_input_gz):
            import gzip
            import shutil
            print(f"Uncompressing {osm_input_gz}...")
            with gzip.open(osm_input_gz, 'rb') as f_in:
                with open(osm_input_uncompressed, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Now run the conversion
            convert_osm_to_pypsa(osm_input_uncompressed, pypsa_output_dir, gridkit_script='tools/gridkit.py')
        else:
            print(f"Error: Input OSM file not found: {osm_input_uncompressed} or {osm_input_gz}")
