#!/usr/bin/env python3
"""
Script to fix traffic light synchronization by adding random offsets and varying phase durations
"""

import gzip
import xml.etree.ElementTree as ET
import os
import random

def create_desynchronized_traffic_light_logic(signal_count, tl_id):
    """Create traffic light logic with random offset and varied durations to break synchronization"""
    
    # Use traffic light ID to seed random for consistent but varied behavior
    random.seed(hash(tl_id) % 10000)
    
    # Random offset between 0 and 300 seconds (much more granular for better distribution)
    offset = random.randint(0, 300)
    
    # Vary the green duration slightly (25-35 seconds)
    green_duration = random.randint(25, 35)
    
    # Vary the yellow duration slightly (2-4 seconds)
    yellow_duration = random.randint(2, 4)
    
    # Vary the red buffer duration slightly (1-3 seconds)
    red_buffer_duration = random.randint(1, 3)
    
    if signal_count == 2:
        # For 2 signals: alternate between them
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(offset),
            'phases': [
                {'duration': green_duration, 'state': 'Gr'},   # First signal green
                {'duration': yellow_duration, 'state': 'yr'},  # First signal yellow
                {'duration': red_buffer_duration, 'state': 'rr'}, # All red
                {'duration': green_duration, 'state': 'rG'},   # Second signal green
                {'duration': yellow_duration, 'state': 'ry'},  # Second signal yellow
                {'duration': red_buffer_duration, 'state': 'rr'}, # All red
            ]
        }
    elif signal_count == 3:
        # For 3 signals: cycle through them
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(offset),
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
        # For 4 signals: opposing movements (2 green at a time)
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(offset),
            'phases': [
                {'duration': green_duration, 'state': 'GGrr'}, # First two signals green (opposing)
                {'duration': yellow_duration, 'state': 'yyrr'}, # First two signals yellow
                {'duration': red_buffer_duration, 'state': 'rrrr'}, # All red
                {'duration': green_duration, 'state': 'rrGG'}, # Last two signals green (opposing)
                {'duration': yellow_duration, 'state': 'rryy'}, # Last two signals yellow
                {'duration': red_buffer_duration, 'state': 'rrrr'}, # All red
            ]
        }
    else:
        # For 5+ signals: quarter-based logic (25% green at a time)
        quarter = max(1, signal_count // 4)
        
        # Ensure all phases have exactly the same length
        # Phase 1: First quarter green
        phase1_state = 'G' * quarter + 'r' * (signal_count - quarter)
        
        # Phase 2: First quarter yellow
        phase2_state = 'y' * quarter + 'r' * (signal_count - quarter)
        
        # Phase 3: All red
        phase3_state = 'r' * signal_count
        
        # Phase 4: Second quarter green
        phase4_state = 'r' * quarter + 'G' * quarter + 'r' * (signal_count - 2 * quarter)
        
        # Phase 5: Second quarter yellow
        phase5_state = 'r' * quarter + 'y' * quarter + 'r' * (signal_count - 2 * quarter)
        
        # Phase 6: All red
        phase6_state = 'r' * signal_count
        
        # Phase 7: Third quarter green
        phase7_state = 'r' * (2 * quarter) + 'G' * quarter + 'r' * (signal_count - 3 * quarter)
        
        # Phase 8: Third quarter yellow
        phase8_state = 'r' * (2 * quarter) + 'y' * quarter + 'r' * (signal_count - 3 * quarter)
        
        # Phase 9: All red
        phase9_state = 'r' * signal_count
        
        # Phase 10: Fourth quarter green
        phase10_state = 'r' * (3 * quarter) + 'G' * (signal_count - 3 * quarter)
        
        # Phase 11: Fourth quarter yellow
        phase11_state = 'r' * (3 * quarter) + 'y' * (signal_count - 3 * quarter)
        
        # Phase 12: All red
        phase12_state = 'r' * signal_count
        
        # Verify all phases have the same length
        phases = [phase1_state, phase2_state, phase3_state, phase4_state, phase5_state, 
                 phase6_state, phase7_state, phase8_state, phase9_state, phase10_state, 
                 phase11_state, phase12_state]
        
        # Ensure all phases have exactly signal_count length
        for i, phase in enumerate(phases):
            if len(phase) != signal_count:
                # Pad or truncate to match signal_count
                if len(phase) < signal_count:
                    phase = phase + 'r' * (signal_count - len(phase))
                else:
                    phase = phase[:signal_count]
                phases[i] = phase
        
        return {
            'type': 'static',
            'programID': '1',
            'offset': str(offset),
            'phases': [
                {'duration': green_duration, 'state': phases[0]},
                {'duration': yellow_duration, 'state': phases[1]},
                {'duration': red_buffer_duration, 'state': phases[2]},
                {'duration': green_duration, 'state': phases[3]},
                {'duration': yellow_duration, 'state': phases[4]},
                {'duration': red_buffer_duration, 'state': phases[5]},
                {'duration': green_duration, 'state': phases[6]},
                {'duration': yellow_duration, 'state': phases[7]},
                {'duration': red_buffer_duration, 'state': phases[8]},
                {'duration': green_duration, 'state': phases[9]},
                {'duration': yellow_duration, 'state': phases[10]},
                {'duration': red_buffer_duration, 'state': phases[11]},
            ]
        }

def fix_traffic_synchronization_for_city(city_dir):
    """Fix traffic light synchronization for a specific city"""
    net_file = os.path.join(city_dir, 'osm.net.xml.gz')
    
    if not os.path.exists(net_file):
        print(f"Network file not found: {net_file}")
        return None
    
    print(f"\nProcessing {city_dir}...")
    
    # Create desynchronized traffic lights
    traffic_lights = {}
    
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
            
            # Create desynchronized logic for this traffic light
            traffic_lights[tl_id] = create_desynchronized_traffic_light_logic(signal_count, tl_id)
    
    print(f"  Created {len(traffic_lights)} desynchronized traffic lights")
    
    # Generate statistics
    offset_distribution = {}
    duration_distribution = {}
    
    for tl_id, tl_info in traffic_lights.items():
        offset = int(tl_info['offset'])
        if offset not in offset_distribution:
            offset_distribution[offset] = 0
        offset_distribution[offset] += 1
        
        # Check first green phase duration
        green_duration = tl_info['phases'][0]['duration']
        if green_duration not in duration_distribution:
            duration_distribution[green_duration] = 0
        duration_distribution[green_duration] += 1
    
    print(f"  Offset distribution (0-300s): {len(offset_distribution)} different offsets")
    print(f"  Duration distribution: {len(duration_distribution)} different green durations")
    
    return traffic_lights

def generate_desynchronized_traffic_lights_xml(traffic_lights, output_file):
    """Generate traffic_lights.add.xml file with desynchronized logic"""
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
    
    print("Fixing Traffic Light Synchronization")
    print("=" * 60)
    print("Breaking city-wide synchronization:")
    print("- Random offsets (0-300 seconds)")
    print("- Varied green durations (25-35 seconds)")
    print("- Varied yellow durations (2-4 seconds)")
    print("- Varied red buffer durations (1-3 seconds)")
    print("=" * 60)
    
    for city in cities:
        city_dir = os.path.join('.', city)
        if not os.path.exists(city_dir):
            print(f"Skipping {city}: directory not found")
            continue
        
        # Fix traffic synchronization for this city
        traffic_lights = fix_traffic_synchronization_for_city(city_dir)
        if traffic_lights is None:
            continue
        
        # Generate the desynchronized add file
        output_file = os.path.join(city_dir, 'traffic_lights_desync.add.xml')
        count = generate_desynchronized_traffic_lights_xml(traffic_lights, output_file)
        
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
    print("- Fixed traffic light synchronization across all cities")
    print("- Added random offsets to break city-wide coordination")
    print("- Varied phase durations for realistic behavior")
    print("- Generated traffic_lights_desync.add.xml files")
    print("- Ready to update SUMO configurations")

if __name__ == "__main__":
    main() 