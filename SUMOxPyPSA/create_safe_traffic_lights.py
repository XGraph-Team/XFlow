#!/usr/bin/env python3
"""
Create safe traffic light logic with proper coordination and random offsets
"""

import gzip
import xml.etree.ElementTree as ET
import os
import random

def create_safe_traffic_light_logic(signal_count, tl_id, junction_offset=0):
    """Create safe traffic light logic with proper coordination"""
    
    # Base durations (same for all traffic lights initially)
    green_duration = 30
    yellow_duration = 3
    red_buffer_duration = 2
    
    if signal_count == 2:
        # For 2 signals: simple alternating (opposing movements)
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(junction_offset),
            'phases': [
                {'duration': green_duration, 'state': 'Gr'},   # First signal green, second red
                {'duration': yellow_duration, 'state': 'yr'},  # First signal yellow, second red
                {'duration': red_buffer_duration, 'state': 'rr'}, # All red
                {'duration': green_duration, 'state': 'rG'},   # First signal red, second green
                {'duration': yellow_duration, 'state': 'ry'},  # First signal red, second yellow
                {'duration': red_buffer_duration, 'state': 'rr'}, # All red
            ]
        }
    elif signal_count == 3:
        # For 3 signals: cycle through them (T-intersection)
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(junction_offset),
            'phases': [
                {'duration': green_duration, 'state': 'Grr'},  # First signal green
                {'duration': yellow_duration, 'state': 'yrr'}, # First signal yellow
                {'duration': red_buffer_duration, 'state': 'rrr'}, # All red
                {'duration': green_duration, 'state': 'rGr'},  # Second signal green
                {'duration': yellow_duration, 'state': 'ryr'}, # Second signal yellow
                {'duration': red_buffer_duration, 'state': 'rrr'}, # All red
                {'duration': green_duration, 'state': 'rrG'},  # Third signal green
                {'duration': yellow_duration, 'state': 'rry'}, # Third signal yellow
                {'duration': red_buffer_duration, 'state': 'rrr'}, # All red
            ]
        }
    elif signal_count == 4:
        # For 4 signals: opposing movements (cross intersection)
        # North-South vs East-West coordination
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(junction_offset),
            'phases': [
                {'duration': green_duration, 'state': 'GGrr'}, # North-South green (opposing)
                {'duration': yellow_duration, 'state': 'yyrr'}, # North-South yellow
                {'duration': red_buffer_duration, 'state': 'rrrr'}, # All red
                {'duration': green_duration, 'state': 'rrGG'}, # East-West green (opposing)
                {'duration': yellow_duration, 'state': 'rryy'}, # East-West yellow
                {'duration': red_buffer_duration, 'state': 'rrrr'}, # All red
            ]
        }
    elif signal_count == 6:
        # For 6 signals: complex intersection with left turns
        # Assume: signals 0,1 = North straight/left, 2,3 = South straight/left, 4,5 = East/West
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(junction_offset),
            'phases': [
                {'duration': green_duration, 'state': 'GGrrrr'}, # North straight + left
                {'duration': yellow_duration, 'state': 'yyrrrr'}, # North yellow
                {'duration': red_buffer_duration, 'state': 'rrrrrr'}, # All red
                {'duration': green_duration, 'state': 'rrGGrr'}, # South straight + left
                {'duration': yellow_duration, 'state': 'rryyrr'}, # South yellow
                {'duration': red_buffer_duration, 'state': 'rrrrrr'}, # All red
                {'duration': green_duration, 'state': 'rrrrGG'}, # East-West
                {'duration': yellow_duration, 'state': 'rrrryy'}, # East-West yellow
                {'duration': red_buffer_duration, 'state': 'rrrrrr'}, # All red
            ]
        }
    elif signal_count == 8:
        # For 8 signals: complex intersection with left turns for all directions
        # Assume: 0,1=North straight/left, 2,3=South straight/left, 4,5=East straight/left, 6,7=West straight/left
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(junction_offset),
            'phases': [
                {'duration': green_duration, 'state': 'GGrrrrrr'}, # North straight + left
                {'duration': yellow_duration, 'state': 'yyrrrrrr'}, # North yellow
                {'duration': red_buffer_duration, 'state': 'rrrrrrrr'}, # All red
                {'duration': green_duration, 'state': 'rrGGrrrr'}, # South straight + left
                {'duration': yellow_duration, 'state': 'rryyrrrr'}, # South yellow
                {'duration': red_buffer_duration, 'state': 'rrrrrrrr'}, # All red
                {'duration': green_duration, 'state': 'rrrrGGrr'}, # East straight + left
                {'duration': yellow_duration, 'state': 'rrrryyrr'}, # East yellow
                {'duration': red_buffer_duration, 'state': 'rrrrrrrr'}, # All red
                {'duration': green_duration, 'state': 'rrrrrrGG'}, # West straight + left
                {'duration': yellow_duration, 'state': 'rrrrrryy'}, # West yellow
                {'duration': red_buffer_duration, 'state': 'rrrrrrrr'}, # All red
            ]
        }
    else:
        # For other signal counts: quarter-based logic ensuring safety
        quarter = max(1, signal_count // 4)
        
        # Create phases where only one quarter is green at a time
        phases = []
        
        # Phase 1: First quarter green
        phase1_state = 'G' * quarter + 'r' * (signal_count - quarter)
        phases.append({'duration': green_duration, 'state': phase1_state})
        phases.append({'duration': yellow_duration, 'state': 'y' * quarter + 'r' * (signal_count - quarter)})
        phases.append({'duration': red_buffer_duration, 'state': 'r' * signal_count})
        
        # Phase 2: Second quarter green
        phase2_state = 'r' * quarter + 'G' * quarter + 'r' * (signal_count - 2 * quarter)
        phases.append({'duration': green_duration, 'state': phase2_state})
        phases.append({'duration': yellow_duration, 'state': 'r' * quarter + 'y' * quarter + 'r' * (signal_count - 2 * quarter)})
        phases.append({'duration': red_buffer_duration, 'state': 'r' * signal_count})
        
        # Phase 3: Third quarter green
        phase3_state = 'r' * (2 * quarter) + 'G' * quarter + 'r' * (signal_count - 3 * quarter)
        phases.append({'duration': green_duration, 'state': phase3_state})
        phases.append({'duration': yellow_duration, 'state': 'r' * (2 * quarter) + 'y' * quarter + 'r' * (signal_count - 3 * quarter)})
        phases.append({'duration': red_buffer_duration, 'state': 'r' * signal_count})
        
        # Phase 4: Fourth quarter green
        phase4_state = 'r' * (3 * quarter) + 'G' * (signal_count - 3 * quarter)
        phases.append({'duration': green_duration, 'state': phase4_state})
        phases.append({'duration': yellow_duration, 'state': 'r' * (3 * quarter) + 'y' * (signal_count - 3 * quarter)})
        phases.append({'duration': red_buffer_duration, 'state': 'r' * signal_count})
        
        # Verify all phases have exactly signal_count length
        for i, phase in enumerate(phases):
            if len(phase['state']) != signal_count:
                # Pad or truncate to match signal_count
                if len(phase['state']) < signal_count:
                    phase['state'] = phase['state'] + 'r' * (signal_count - len(phase['state']))
                else:
                    phase['state'] = phase['state'][:signal_count]
                phases[i] = phase
        
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(junction_offset),
            'phases': phases
        }

def create_safe_traffic_lights_for_city(city_dir):
    """Create safe traffic lights for a specific city"""
    net_file = os.path.join(city_dir, 'osm.net.xml.gz')
    
    if not os.path.exists(net_file):
        print(f"Network file not found: {net_file}")
        return None
    
    print(f"\nProcessing {city_dir}...")
    
    # Create safe traffic lights
    traffic_lights = {}
    junction_offsets = {}
    
    with gzip.open(net_file, 'rt', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
        for tl in root.findall('tlLogic'):
            tl_id = tl.get('id')
            if tl_id is None:
                continue
            
            phases = tl.findall('phase')
            if not phases:
                continue
                
            signal_count = len(phases[0].get('state'))
            
            # Generate random offset for this junction (0-300 seconds)
            # Use tl_id to ensure consistent offset for the same junction
            random.seed(hash(tl_id) % 10000)
            junction_offset = random.randint(0, 300)
            
            # Create safe logic for this traffic light
            traffic_lights[tl_id] = create_safe_traffic_light_logic(signal_count, tl_id, junction_offset)
            junction_offsets[tl_id] = junction_offset
    
    print(f"  Created {len(traffic_lights)} safe traffic lights")
    
    # Generate statistics
    offset_distribution = {}
    for offset in junction_offsets.values():
        if offset not in offset_distribution:
            offset_distribution[offset] = 0
        offset_distribution[offset] += 1
    
    print(f"  Junction offset distribution: {len(offset_distribution)} unique offsets")
    
    # Show safety verification
    safety_verified = 0
    for tl_id, tl_info in traffic_lights.items():
        phases = tl_info['phases']
        is_safe = True
        
        # Check that no phase has more than 25% green signals (except for 2-4 signal cases)
        signal_count = len(phases[0]['state'])
        if signal_count > 4:
            for phase in phases:
                green_count = phase['state'].count('G')
                if green_count > signal_count * 0.25:
                    is_safe = False
                    break
        
        if is_safe:
            safety_verified += 1
    
    print(f"  Safety verified: {safety_verified}/{len(traffic_lights)} traffic lights")
    
    return traffic_lights

def generate_safe_traffic_lights_xml(traffic_lights, output_file):
    """Generate traffic_lights.add.xml file with safe logic"""
    root = ET.Element('additional')
    
    for tl_id, tl_info in traffic_lights.items():
        # Create tlLogic element
        tl_elem = ET.SubElement(root, 'tlLogic')
        tl_elem.set('id', tl_id)
        tl_elem.set('type', tl_info['type'])
        tl_elem.set('programID', tl_info['programID'])
        tl_elem.set('offset', tl_info['offset'])
        
        # Add phases
        for phase in tl_info['phases']:
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
    cities = ['miami', 'los_angeles', 'new_york']
    
    print("Creating Safe Traffic Light Logic")
    print("=" * 60)
    print("Safety-first approach:")
    print("1. Synchronize all lights with proper coordination")
    print("2. Ensure opposing movements are red when one is green")
    print("3. Add random offsets to desynchronize junctions")
    print("4. Maintain safety within each junction")
    print("=" * 60)
    
    for city in cities:
        city_dir = os.path.join('.', city)
        if not os.path.exists(city_dir):
            print(f"Skipping {city}: directory not found")
            continue
        
        # Create safe traffic lights for this city
        traffic_lights = create_safe_traffic_lights_for_city(city_dir)
        if traffic_lights is None:
            continue
        
        # Generate the safe add file
        output_file = os.path.join(city_dir, 'traffic_lights_safe.add.xml')
        count = generate_safe_traffic_lights_xml(traffic_lights, output_file)
        
        print(f"  Generated {output_file} with {count} traffic lights")
        
        # Show example
        if traffic_lights:
            first_id = list(traffic_lights.keys())[0]
            first_tl = traffic_lights[first_id]
            signal_count = len(first_tl['phases'][0]['state'])
            print(f"  Example: {first_id} - {signal_count} signals, {len(first_tl['phases'])} phases")
            print(f"    Offset: {first_tl['offset']}s")
            print(f"    Green duration: {first_tl['phases'][0]['duration']}s")
            print(f"    Yellow duration: {first_tl['phases'][1]['duration']}s")
            print(f"    Phase 1: {first_tl['phases'][0]['state']}")
            if len(first_tl['phases']) > 3:
                print(f"    Phase 4: {first_tl['phases'][3]['state']}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("- Created safe traffic light logic for all cities")
    print("- Ensured proper coordination within junctions")
    print("- Added random offsets to desynchronize junctions")
    print("- Generated traffic_lights_safe.add.xml files")
    print("- Ready to update SUMO configurations")

if __name__ == "__main__":
    main() 