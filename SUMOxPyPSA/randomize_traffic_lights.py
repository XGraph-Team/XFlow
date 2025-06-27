#!/usr/bin/env python3
"""
Script to randomize traffic light timing to break synchronization
"""

import gzip
import xml.etree.ElementTree as ET
import os
import random

def randomize_traffic_lights(netfile):
    """Extract traffic lights and randomize their timing"""
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
                    # Add slight randomization to phase duration (±2 seconds)
                    original_duration = int(duration)
                    randomized_duration = max(1, original_duration + random.randint(-2, 2))
                    
                    phases.append({
                        'duration': randomized_duration,
                        'state': state
                    })
            
            if phases:
                # Add random offset (0-60 seconds) to break synchronization
                offset = random.randint(0, 60)
                
                # Better randomization of initial state
                # Instead of random phase shift, we'll create a more realistic distribution
                # 40% start with red, 30% start with yellow, 30% start with green
                rand_val = random.random()
                
                if rand_val < 0.4:  # 40% start with red
                    # Find a red phase or create one
                    red_phases = [i for i, p in enumerate(phases) if 'r' in p['state'].lower() and 'g' not in p['state'].lower()]
                    if red_phases:
                        phase_shift = random.choice(red_phases)
                    else:
                        # If no red phase, start at a random phase
                        phase_shift = random.randint(0, len(phases) - 1)
                        
                elif rand_val < 0.7:  # 30% start with yellow
                    # Find a yellow phase
                    yellow_phases = [i for i, p in enumerate(phases) if 'y' in p['state'].lower()]
                    if yellow_phases:
                        phase_shift = random.choice(yellow_phases)
                    else:
                        # If no yellow phase, start at a random phase
                        phase_shift = random.randint(0, len(phases) - 1)
                        
                else:  # 30% start with green
                    # Find a green phase
                    green_phases = [i for i, p in enumerate(phases) if 'g' in p['state'].lower()]
                    if green_phases:
                        phase_shift = random.choice(green_phases)
                    else:
                        # If no green phase, start at a random phase
                        phase_shift = random.randint(0, len(phases) - 1)
                
                # Apply the phase shift
                shifted_phases = phases[phase_shift:] + phases[:phase_shift]
                
                traffic_lights[tl_id] = {
                    'type': tl.get('type', 'static'),
                    'programID': tl.get('programID', '0'),
                    'offset': offset,
                    'phases': shifted_phases,
                    'initial_state': shifted_phases[0]['state'] if shifted_phases else 'unknown'
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

def generate_randomized_traffic_lights_xml(traffic_lights, output_file):
    """Generate traffic_lights.add.xml with randomized timing"""
    
    root = ET.Element('additional')
    
    for tl_id, tl_info in traffic_lights.items():
        # Create tlLogic element
        tl_elem = ET.SubElement(root, 'tlLogic')
        tl_elem.set('id', tl_id)
        tl_elem.set('type', tl_info['type'])
        tl_elem.set('programID', '1')  # Use programID '1' to avoid conflicts with existing logic
        tl_elem.set('offset', str(tl_info['offset']))
        
        # Fix the phases and add all-red safety phases
        fixed_phases = fix_traffic_light_phases(tl_info['phases'])
        
        # Add phases
        for phase in fixed_phases:
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
    
    print("Traffic Light Randomization Generator")
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
        
        # Randomize traffic lights
        traffic_lights = randomize_traffic_lights(net_file)
        
        if not traffic_lights:
            print(f"  No traffic lights found in {city}")
            continue
        
        print(f"  Found {len(traffic_lights)} traffic lights")
        
        # Show first few IDs as examples
        ids_list = list(traffic_lights.keys())
        print(f"  Example IDs: {ids_list[:5]}")
        
        # Generate randomized add file
        output_file = os.path.join(city_dir, 'traffic_lights_randomized.add.xml')
        count = generate_randomized_traffic_lights_xml(traffic_lights, output_file)
        
        print(f"  Generated {output_file} with {count} randomized traffic lights")
        
        # Show example randomization
        if traffic_lights:
            first_id = ids_list[0]
            first_tl = traffic_lights[first_id]
            print(f"  Example: {first_id} - offset: {first_tl['offset']}s, phases: {len(first_tl['phases'])}")
            
            # Show phase durations
            durations = [phase['duration'] for phase in first_tl['phases']]
            print(f"    Phase durations: {durations}")
            
            # Show initial state distribution
            red_count = sum(1 for tl in traffic_lights.values() if 'r' in tl['initial_state'].lower() and 'g' not in tl['initial_state'].lower())
            yellow_count = sum(1 for tl in traffic_lights.values() if 'y' in tl['initial_state'].lower())
            green_count = sum(1 for tl in traffic_lights.values() if 'g' in tl['initial_state'].lower())
            total = len(traffic_lights)
            
            print(f"  Initial state distribution:")
            print(f"    Red: {red_count}/{total} ({red_count/total*100:.1f}%)")
            print(f"    Yellow: {yellow_count}/{total} ({yellow_count/total*100:.1f}%)")
            print(f"    Green: {green_count}/{total} ({green_count/total*100:.1f}%)")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("- Added random offsets (0-60s) to break synchronization")
    print("- Randomized initial states by shifting phases")
    print("- Varied phase durations slightly (±2s)")
    print("- Added all-red safety phases")
    print("- Created traffic_lights_randomized.add.xml files")
    print("- Use these files to replace the synchronized ones")

if __name__ == "__main__":
    main() 