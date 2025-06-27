#!/usr/bin/env python3
"""
Script to regenerate SUMO networks with updated traffic light configuration
"""

import os
import subprocess
import sys

# Get SUMO binary path from config
try:
    from config import SUMO_PATH
    NETCONVERT_BINARY = os.path.join(SUMO_PATH, "bin/netconvert")
except ImportError:
    print("Error: Could not import SUMO_PATH from config.py")
    sys.exit(1)

def regenerate_network(city_dir):
    """Regenerate the network for a specific city"""
    print(f"Regenerating network for {city_dir}...")
    
    # Change to the city directory
    original_dir = os.getcwd()
    os.chdir(city_dir)
    
    try:
        # Check if netccfg file exists
        netccfg_file = "osm.netccfg"
        if not os.path.exists(netccfg_file):
            print(f"Warning: {netccfg_file} not found in {city_dir}")
            return False
        
        # Run netconvert
        cmd = [NETCONVERT_BINARY, "-c", netccfg_file]
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully regenerated network for {city_dir}")
            return True
        else:
            print(f"Error regenerating network for {city_dir}:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Exception while regenerating network for {city_dir}: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """Main function to regenerate all networks"""
    cities = ["los_angeles", "miami"]
    
    print("Regenerating SUMO networks with updated traffic light configuration...")
    print(f"Using netconvert: {NETCONVERT_BINARY}")
    
    success_count = 0
    for city in cities:
        if regenerate_network(city):
            success_count += 1
    
    print(f"\nRegeneration complete: {success_count}/{len(cities)} cities successful")
    
    if success_count == len(cities):
        print("All networks regenerated successfully!")
        print("The traffic lights should now follow proper green → yellow → red → green cycling.")
    else:
        print("Some networks failed to regenerate. Check the error messages above.")

if __name__ == "__main__":
    main() 