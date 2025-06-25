#!/usr/bin/env python3
"""
Unified build script for SUMO network generation
"""

import os
import sys
import subprocess
from sumo_config import SUMO_COMMON_CONFIG, CITY_CONFIGS

def run_command(cmd, cwd=None):
    """Run a shell command and print its output"""
    print(f"Running: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        print(line, end='')
    process.wait()
    return process.returncode

def build_city(city):
    """Build SUMO network for a specific city"""
    if city not in CITY_CONFIGS:
        print(f"Unknown city: {city}")
        return False
    
    city_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), city)
    if not os.path.exists(city_dir):
        print(f"City directory not found: {city_dir}")
        return False
    
    # Run netconvert
    netconvert_cmd = [
        "netconvert",
        "--osm-files", CITY_CONFIGS[city]['netccfg']['input']['osm-files'],
        "--output-file", CITY_CONFIGS[city]['netccfg']['output']['output-file'],
        "--type-files", CITY_CONFIGS[city]['netccfg']['input'].get('type-files', ''),
        "--lefthand" if CITY_CONFIGS[city]['netccfg']['processing'].get('lefthand') == 'true' else "",
        "--keep-edges.by-vclass", CITY_CONFIGS[city]['netccfg']['edge_removal'].get('keep-edges.by-vclass', ''),
        "--remove-edges.by-vclass", CITY_CONFIGS[city]['netccfg']['edge_removal'].get('remove-edges.by-vclass', ''),
    ]
    
    # Filter out empty arguments
    netconvert_cmd = [arg for arg in netconvert_cmd if arg]
    
    if run_command(netconvert_cmd, cwd=city_dir) != 0:
        print(f"Failed to build network for {city}")
        return False
    
    print(f"Successfully built network for {city}")
    return True

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python build.py [manchester|newyork]")
        return 1
    
    city = sys.argv[1].lower()
    if build_city(city):
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main()) 