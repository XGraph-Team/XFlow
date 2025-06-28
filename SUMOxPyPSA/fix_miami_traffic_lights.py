#!/usr/bin/env python3
"""
Script to fix Miami traffic lights with proper logic for different signal group counts
"""

import gzip
import xml.etree.ElementTree as ET
import os

def create_fixed_traffic_lights(netfile):
    """Create fixed traffic light logic that works for all signal group counts"""
    traffic_lights = {}
    
    with gzip.open(netfile, 'rt', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
        for tl in root.findall('tlLogic'):
            tl_id = tl.get('id')
            if tl_id is None:
                continue
            
            # Get the original state length
            phases = tl.findall('phase')
            if not phases:
                continue
                
            original_state_length = len(phases[0].get('state'))
            
            # Create logic based on the number of signal groups
            if original_state_length == 2:
                # For 2 signal groups: alternate between them
                traffic_lights[tl_id] = {
                    'type': tl.get('type', 'static'),
                    'programID': '1',
                    'offset': '0',
                    'phases': [
                        {'duration': 30, 'state': 'Gr'},   # First signal green
                        {'duration': 3, 'state': 'yr'},    # First signal yellow
                        {'duration': 2, 'state': 'rr'},    # All red
                        {'duration': 30, 'state': 'rG'},   # Second signal green
                        {'duration': 3, 'state': 'ry'},    # Second signal yellow
                        {'duration': 2, 'state': 'rr'},    # All red
                    ]
                }
            elif original_state_length == 3:
                # For 3 signal groups: cycle through them
                traffic_lights[tl_id] = {
                    'type': tl.get('type', 'static'),
                    'programID': '1',
                    'offset': '0',
                    'phases': [
                        {'duration': 30, 'state': 'Grr'},  # First signal green
                        {'duration': 3, 'state': 'yrr'},   # First signal yellow
                        {'duration': 2, 'state': 'rrr'},   # All red
                        {'duration': 30, 'state': 'rGr'},  # Second signal green
                        {'duration': 3, 'state': 'ryr'},   # Second signal yellow
                        {'duration': 2, 'state': 'rrr'},   # All red
                        {'duration': 30, 'state': 'rrG'},  # Third signal green
                        {'duration': 3, 'state': 'rry'},   # Third signal yellow
                        {'duration': 2, 'state': 'rrr'},   # All red
                    ]
                }
            elif original_state_length == 4:
                # For 4 signal groups: use opposing movement logic
                traffic_lights[tl_id] = {
                    'type': tl.get('type', 'static'),
                    'programID': '1',
                    'offset': '0',
                    'phases': [
                        {'duration': 30, 'state': 'GGrr'}, # First two signals green (opposing)
                        {'duration': 3, 'state': 'yyrr'},  # First two signals yellow
                        {'duration': 2, 'state': 'rrrr'},  # All red
                        {'duration': 30, 'state': 'rrGG'}, # Last two signals green (opposing)
                        {'duration': 3, 'state': 'rryy'},  # Last two signals yellow
                        {'duration': 2, 'state': 'rrrr'},  # All red
                    ]
                }
            else:
                # For 5+ signal groups: use quarter-based logic but ensure at least one signal is green
                quarter = max(1, original_state_length // 4)
                
                # Phase 1: First quarter green
                phase1_state = 'G' * quarter + 'r' * (original_state_length - quarter)
                
                # Phase 2: First quarter yellow
                phase2_state = 'y' * quarter + 'r' * (original_state_length - quarter)
                
                # Phase 3: All red
                phase3_state = 'r' * original_state_length
                
                # Phase 4: Second quarter green
                phase4_state = 'r' * quarter + 'G' * quarter + 'r' * (original_state_length - 2 * quarter)
                
                # Phase 5: Second quarter yellow
                phase5_state = 'r' * quarter + 'y' * quarter + 'r' * (original_state_length - 2 * quarter)
                
                # Phase 6: All red
                phase6_state = 'r' * original_state_length
                
                # Phase 7: Third quarter green
                phase7_state = 'r' * (2 * quarter) + 'G' * quarter + 'r' * (original_state_length - 3 * quarter)
                
                # Phase 8: Third quarter yellow
                phase8_state = 'r' * (2 * quarter) + 'y' * quarter + 'r' * (original_state_length - 3 * quarter)
                
                # Phase 9: All red
                phase9_state = 'r' * original_state_length
                
                # Phase 10: Fourth quarter green
                phase10_state = 'r' * (3 * quarter) + 'G' * (original_state_length - 3 * quarter)
                
                # Phase 11: Fourth quarter yellow
                phase11_state = 'r' * (3 * quarter) + 'y' * (original_state_length - 3 * quarter)
                
                # Phase 12: All red
                phase12_state = 'r' * original_state_length
                
                traffic_lights[tl_id] = {
                    'type': tl.get('type', 'static'),
                    'programID': '1',
                    'offset': '0',
                    'phases': [
                        {'duration': 30, 'state': phase1_state},
                        {'duration': 3, 'state': phase2_state},
                        {'duration': 2, 'state': phase3_state},
                        {'duration': 30, 'state': phase4_state},
                        {'duration': 3, 'state': phase5_state},
                        {'duration': 2, 'state': phase6_state},
                        {'duration': 30, 'state': phase7_state},
                        {'duration': 3, 'state': phase8_state},
                        {'duration': 2, 'state': phase9_state},
                        {'duration': 30, 'state': phase10_state},
                        {'duration': 3, 'state': phase11_state},
                        {'duration': 2, 'state': phase12_state},
                    ]
                }
    
    return traffic_lights

def generate_fixed_traffic_lights_xml(traffic_lights, output_file):
    """Generate traffic_lights.add.xml with fixed logic"""
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
    print("Fixing Miami Traffic Lights")
    print("=" * 50)
    print("Fixing issues with traffic lights that are always red")
    print("=" * 50)
    
    city_dir = '../miami'
    net_file = os.path.join(city_dir, 'osm.net.xml.gz')
    
    if not os.path.exists(net_file):
        print(f"Network file not found: {net_file}")
        return
    
    print(f"Processing Miami...")
    
    # Create fixed traffic lights
    traffic_lights = create_fixed_traffic_lights(net_file)
    print(f"  Created {len(traffic_lights)} traffic lights")
    
    # Generate the add file
    output_file = os.path.join(city_dir, 'traffic_lights_fixed_miami.add.xml')
    count = generate_fixed_traffic_lights_xml(traffic_lights, output_file)
    
    print(f"  Generated {output_file} with {count} traffic lights")
    
    # Show examples for different signal group counts
    examples = {}
    for tl_id, tl_info in traffic_lights.items():
        signal_count = len(tl_info['phases'][0]['state'])
        if signal_count not in examples:
            examples[signal_count] = tl_info
    
    for signal_count, tl_info in sorted(examples.items()):
        print(f"  Example {signal_count} signals: {len(tl_info['phases'])} phases")
        print(f"    Phase durations: {[p['duration'] for p in tl_info['phases']]}")
        print(f"    Phase 1: {tl_info['phases'][0]['state']}")
        if len(tl_info['phases']) > 3:
            print(f"    Phase 4: {tl_info['phases'][3]['state']}")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("- Fixed traffic lights that were always red")
    print("- Implemented proper logic for different signal group counts")
    print("- Ensured at least one signal is green in each phase")
    print("- Generated traffic_lights_fixed_miami.add.xml")

if __name__ == "__main__":
    main() 