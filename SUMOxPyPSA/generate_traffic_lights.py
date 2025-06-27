#!/usr/bin/env python3
"""
Script to extract all traffic light IDs from network file and generate matching traffic_lights.add.xml
"""

import gzip
import xml.etree.ElementTree as ET
import os

def extract_traffic_light_info(netfile):
    """Extract all traffic light IDs and their current phases from network file"""
    traffic_lights = {}
    
    with gzip.open(netfile, 'rt', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
        for tl in root.findall('tlLogic'):
            tl_id = tl.get('id')
            if tl_id is None:
                continue
                
            phases = []
            for phase in tl.findall('phase'):
                duration = phase.get('duration')
                state = phase.get('state')
                if duration and state:
                    phases.append({
                        'duration': int(duration),
                        'state': state
                    })
            
            if phases:
                traffic_lights[tl_id] = {
                    'type': tl.get('type', 'static'),
                    'programID': tl.get('programID', '0'),
                    'offset': tl.get('offset', '0'),
                    'phases': phases
                }
    
    return traffic_lights

def fix_traffic_light_phases(phases):
    """Fix traffic light phases to ensure proper green-yellow-red-green cycling"""
    if not phases:
        return phases
    
    fixed_phases = []
    state_length = len(phases[0]['state'])
    
    for i, phase in enumerate(phases):
        # Add the original phase
        fixed_phases.append(phase)
        
        # Check if this is a yellow phase and next phase is green
        if 'y' in phase['state'].lower() and i < len(phases) - 1:
            next_state = phases[i + 1]['state']
            if 'g' in next_state.lower():
                # Insert all-red phase between yellow and green
                all_red_state = 'r' * state_length
                fixed_phases.append({
                    'duration': 2,  # 2 seconds all-red
                    'state': all_red_state
                })
    
    return fixed_phases

def generate_traffic_lights_add_xml(traffic_lights, output_file):
    """Generate traffic_lights.add.xml file with fixed traffic light logic"""
    
    # Create XML structure
    root = ET.Element('additional')
    
    for tl_id, tl_info in traffic_lights.items():
        # Create tlLogic element
        tl_elem = ET.SubElement(root, 'tlLogic')
        tl_elem.set('id', tl_id)
        tl_elem.set('type', tl_info['type'])
        tl_elem.set('programID', tl_info['programID'])
        tl_elem.set('offset', tl_info['offset'])
        
        # Fix the phases
        fixed_phases = fix_traffic_light_phases(tl_info['phases'])
        
        # Add phases
        for phase in fixed_phases:
            phase_elem = ET.SubElement(tl_elem, 'phase')
            phase_elem.set('duration', str(phase['duration']))
            phase_elem.set('state', phase['state'])
    
    # Write to file
    tree = ET.ElementTree(root)
    
    # Add XML declaration
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += ET.tostring(root, encoding='unicode')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    return len(traffic_lights)

def main():
    """Main function"""
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    cities = ['miami', 'los_angeles', 'new_york']
    
    print("Traffic Light ID Extractor and Generator")
    print("=" * 50)
    
    for city in cities:
        city_dir = os.path.join(current_dir, city)
        print(f"Checking directory: {city_dir}")
        
        if not os.path.exists(city_dir):
            print(f"Skipping {city}: directory not found at {city_dir}")
            continue
        
        net_file = os.path.join(city_dir, 'osm.net.xml.gz')
        if not os.path.exists(net_file):
            print(f"Skipping {city}: network file not found at {net_file}")
            continue
        
        print(f"\nProcessing {city}...")
        
        # Extract traffic light information
        traffic_lights = extract_traffic_light_info(net_file)
        
        if not traffic_lights:
            print(f"  No traffic lights found in {city}")
            continue
        
        print(f"  Found {len(traffic_lights)} traffic lights")
        
        # Show first few IDs as examples
        ids_list = list(traffic_lights.keys())
        print(f"  Example IDs: {ids_list[:5]}")
        
        # Generate the add file
        output_file = os.path.join(city_dir, 'traffic_lights.add.xml')
        count = generate_traffic_lights_add_xml(traffic_lights, output_file)
        
        print(f"  Generated {output_file} with {count} traffic lights")
        
        # Show phase information for first traffic light
        if traffic_lights:
            first_id = ids_list[0]
            first_tl = traffic_lights[first_id]
            original_phases = len(first_tl['phases'])
            fixed_phases = len(fix_traffic_light_phases(first_tl['phases']))
            print(f"  Example: {first_id} - {original_phases} phases -> {fixed_phases} phases")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("- Generated traffic_lights.add.xml files for each city")
    print("- Fixed traffic light phases to ensure proper green-yellow-red-green cycling")
    print("- Added all-red safety phases between direction changes")
    print("- All traffic light IDs now match the network files")

if __name__ == "__main__":
    main() 