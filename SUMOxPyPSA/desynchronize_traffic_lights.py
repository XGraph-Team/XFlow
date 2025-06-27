#!/usr/bin/env python3
"""
Script to desynchronize traffic lights by adding random phase offsets
"""

import gzip
import xml.etree.ElementTree as ET
import os
import random

def extract_and_desynchronize_traffic_lights(netfile):
    """Extract traffic lights and add random offsets to desynchronize them"""
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
                # Add random offset to desynchronize this traffic light
                offset = random.randint(0, 40)  # Random offset between 0-40 seconds
                
                traffic_lights[tl_id] = {
                    'type': tl.get('type', 'static'),
                    'programID': tl.get('programID', '0'),
                    'offset': offset,
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

def create_opposing_phases_for_intersection(phases):
    """Create opposing phases for traffic lights at the same intersection"""
    if not phases:
        return phases
    
    state_length = len(phases[0]['state'])
    
    # Create two different phase patterns for opposing directions
    # Pattern 1: First half green, second half red
    # Pattern 2: First half red, second half green (opposite)
    
    # Split the state into two halves
    half_length = state_length // 2
    
    # Create opposing phases
    opposing_phases = []
    
    # Phase 1: North/South green, East/West red
    phase1_state = 'G' * half_length + 'r' * (state_length - half_length)
    opposing_phases.append({'duration': 15, 'state': phase1_state})
    
    # Phase 2: North/South yellow, East/West red
    phase2_state = 'y' * half_length + 'r' * (state_length - half_length)
    opposing_phases.append({'duration': 3, 'state': phase2_state})
    
    # Phase 3: All red
    phase3_state = 'r' * state_length
    opposing_phases.append({'duration': 2, 'state': phase3_state})
    
    # Phase 4: North/South red, East/West green
    phase4_state = 'r' * half_length + 'G' * (state_length - half_length)
    opposing_phases.append({'duration': 15, 'state': phase4_state})
    
    # Phase 5: North/South red, East/West yellow
    phase5_state = 'r' * half_length + 'y' * (state_length - half_length)
    opposing_phases.append({'duration': 3, 'state': phase5_state})
    
    # Phase 6: All red
    opposing_phases.append({'duration': 2, 'state': phase3_state})
    
    return opposing_phases

def generate_desynchronized_traffic_lights_xml(traffic_lights, output_file, use_opposing=False):
    """Generate traffic_lights.add.xml with desynchronized logic"""
    
    root = ET.Element('additional')
    
    for tl_id, tl_info in traffic_lights.items():
        # Create tlLogic element
        tl_elem = ET.SubElement(root, 'tlLogic')
        tl_elem.set('id', tl_id)
        tl_elem.set('type', tl_info['type'])
        tl_elem.set('programID', tl_info['programID'])
        tl_elem.set('offset', str(tl_info['offset']))
        
        # Choose phases based on whether we want opposing logic
        if use_opposing:
            phases = create_opposing_phases_for_intersection(tl_info['phases'])
        else:
            phases = fix_traffic_light_phases(tl_info['phases'])
        
        # Add phases
        for phase in phases:
            phase_elem = ET.SubElement(tl_elem, 'phase')
            phase_elem.set('duration', str(phase['duration']))
            phase_elem.set('state', phase['state'])
    
    # Write to file
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += ET.tostring(root, encoding='unicode')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    return len(traffic_lights)

def main():
    """Main function"""
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    cities = ['miami', 'los_angeles', 'new_york']
    
    print("Traffic Light Desynchronization Generator")
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
        
        # Extract and desynchronize traffic lights
        traffic_lights = extract_and_desynchronize_traffic_lights(net_file)
        
        if not traffic_lights:
            print(f"  No traffic lights found in {city}")
            continue
        
        print(f"  Found {len(traffic_lights)} traffic lights")
        
        # Show first few IDs as examples
        ids_list = list(traffic_lights.keys())
        print(f"  Example IDs: {ids_list[:5]}")
        
        # Generate desynchronized add file
        output_file = os.path.join(city_dir, 'traffic_lights_desync.add.xml')
        count = generate_desynchronized_traffic_lights_xml(traffic_lights, output_file, use_opposing=False)
        
        print(f"  Generated {output_file} with {count} desynchronized traffic lights")
        
        # Generate opposing add file
        output_file_opposing = os.path.join(city_dir, 'traffic_lights_opposing.add.xml')
        count_opposing = generate_desynchronized_traffic_lights_xml(traffic_lights, output_file_opposing, use_opposing=True)
        
        print(f"  Generated {output_file_opposing} with {count_opposing} opposing traffic lights")
        
        # Show example offsets
        if traffic_lights:
            first_id = ids_list[0]
            first_tl = traffic_lights[first_id]
            print(f"  Example: {first_id} - offset: {first_tl['offset']}s")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("- Generated desynchronized traffic light logic")
    print("- Added random phase offsets to prevent synchronization")
    print("- Created traffic_lights_desync.add.xml (with offsets)")
    print("- Created traffic_lights_opposing.add.xml (with opposing phases)")
    print("- Use these files to replace the synchronized ones")

if __name__ == "__main__":
    main() 