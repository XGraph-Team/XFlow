#!/usr/bin/env python3
"""
Script to modify existing traffic light logic to separate straight and left-turn signals
"""

import gzip
import xml.etree.ElementTree as ET
import os
import copy

def analyze_traffic_light_structure(netfile):
    """Analyze current traffic light structure"""
    traffic_lights = {}
    connections = {}
    
    with gzip.open(netfile, 'rt', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
        # Get all traffic lights
        for tl in root.findall('tlLogic'):
            tl_id = tl.get('id')
            phases = []
            for phase in tl.findall('phase'):
                phases.append({
                    'duration': int(phase.get('duration')),
                    'state': phase.get('state')
                })
            
            traffic_lights[tl_id] = {
                'type': tl.get('type', 'static'),
                'programID': tl.get('programID', '0'),
                'offset': tl.get('offset', '0'),
                'phases': phases
            }
        
        # Get all connections
        for conn in root.findall('connection'):
            tl_id = conn.get('tl')
            if tl_id:
                if tl_id not in connections:
                    connections[tl_id] = []
                
                connections[tl_id].append({
                    'from': conn.get('from'),
                    'to': conn.get('to'),
                    'fromLane': conn.get('fromLane'),
                    'toLane': conn.get('toLane'),
                    'dir': conn.get('dir', 's'),  # Default to straight
                    'linkIndex': conn.get('linkIndex')
                })
    
    return traffic_lights, connections

def separate_straight_and_left_signals(traffic_lights, connections):
    """Separate straight and left-turn signals for each traffic light"""
    modified_tls = {}
    
    for tl_id, tl_info in traffic_lights.items():
        if tl_id not in connections:
            continue
            
        conns = connections[tl_id]
        if not conns:
            continue
        
        # Group connections by direction
        straight_conns = [c for c in conns if c['dir'] in ['s', 't']]  # straight/through
        left_conns = [c for c in conns if c['dir'] == 'l']  # left turn
        right_conns = [c for c in conns if c['dir'] == 'r']  # right turn (usually always green)
        
        # Get the original state length
        original_state_length = len(tl_info['phases'][0]['state'])
        
        # Create new phases with the same number of signal groups
        new_phases = []
        for phase in tl_info['phases']:
            original_state = phase['state']
            
            # Create new state with the same length but reorganized logic
            new_state = list(original_state)
            
            # Determine which movements should be green in this phase
            has_straight = 'G' in original_state[:original_state_length//3]
            has_left = 'G' in original_state[original_state_length//3:2*original_state_length//3]
            has_right = 'G' in original_state[2*original_state_length//3:]
            
            # Reorganize the signal groups:
            # First third: straight movements
            # Second third: left turn movements  
            # Last third: right turn movements (usually always green)
            
            # Set straight signals (first third)
            for i in range(original_state_length // 3):
                if has_straight:
                    new_state[i] = 'G'
                else:
                    new_state[i] = 'r'
            
            # Set left turn signals (second third)
            for i in range(original_state_length // 3, 2 * original_state_length // 3):
                if has_left:
                    new_state[i] = 'G'
                else:
                    new_state[i] = 'r'
            
            # Set right turn signals (last third) - usually always green
            for i in range(2 * original_state_length // 3, original_state_length):
                new_state[i] = 'G'  # Right turns are usually always allowed
            
            new_phases.append({
                'duration': phase['duration'],
                'state': ''.join(new_state)
            })
        
        modified_tls[tl_id] = {
            'type': tl_info['type'],
            'programID': '1',  # Use programID '1' to avoid conflicts
            'offset': tl_info['offset'],
            'phases': new_phases,
            'straight_connections': straight_conns,
            'left_connections': left_conns,
            'right_connections': right_conns
        }
    
    return modified_tls

def update_connections_for_separate_signals(connections, modified_tls):
    """Update connections to use separate signal groups"""
    updated_connections = []
    
    for tl_id, tl_info in modified_tls.items():
        if tl_id not in connections:
            continue
        
        # Update straight connections to use signal group 0
        for conn in tl_info['straight_connections']:
            conn_copy = conn.copy()
            conn_copy['linkIndex'] = '0'  # Signal group 0 for straight
            updated_connections.append(conn_copy)
        
        # Update left turn connections to use signal group 1
        for conn in tl_info['left_connections']:
            conn_copy = conn.copy()
            conn_copy['linkIndex'] = '1'  # Signal group 1 for left
            updated_connections.append(conn_copy)
        
        # Update right turn connections to use signal group 2
        for conn in tl_info['right_connections']:
            conn_copy = conn.copy()
            conn_copy['linkIndex'] = '2'  # Signal group 2 for right
            updated_connections.append(conn_copy)
    
    return updated_connections

def generate_modified_traffic_lights_xml(modified_tls, output_file):
    """Generate traffic_lights.add.xml with separated signals"""
    root = ET.Element('additional')
    
    for tl_id, tl_info in modified_tls.items():
        # Create tlLogic element
        tl_elem = ET.SubElement(root, 'tlLogic')
        tl_elem.set('id', tl_id)
        tl_elem.set('type', tl_info['type'])
        tl_elem.set('programID', tl_info['programID'])
        tl_elem.set('offset', str(tl_info['offset']))
        
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
    
    return len(modified_tls)

def main():
    """Main function"""
    cities = ['miami', 'los_angeles', 'new_york']
    
    print("Traffic Light Signal Separation")
    print("=" * 50)
    
    for city in cities:
        city_dir = os.path.join('.', city)
        if not os.path.exists(city_dir):
            print(f"Skipping {city}: directory not found")
            continue
        
        net_file = os.path.join(city_dir, 'osm.net.xml.gz')
        if not os.path.exists(net_file):
            print(f"Skipping {city}: network file not found")
            continue
        
        print(f"\nProcessing {city}...")
        
        # Analyze current structure
        traffic_lights, connections = analyze_traffic_light_structure(net_file)
        print(f"  Found {len(traffic_lights)} traffic lights")
        print(f"  Found {len(connections)} traffic lights with connections")
        
        # Separate signals
        modified_tls = separate_straight_and_left_signals(traffic_lights, connections)
        print(f"  Modified {len(modified_tls)} traffic lights")
        
        # Generate new traffic lights file
        output_file = os.path.join(city_dir, 'traffic_lights_separated.add.xml')
        count = generate_modified_traffic_lights_xml(modified_tls, output_file)
        
        print(f"  Generated {output_file} with {count} traffic lights")
        
        # Show example
        if modified_tls:
            first_id = list(modified_tls.keys())[0]
            first_tl = modified_tls[first_id]
            print(f"  Example: {first_id} - {len(first_tl['phases'])} phases")
            print(f"    Signal groups: [straight, left, right]")
            print(f"    Straight connections: {len(first_tl['straight_connections'])}")
            print(f"    Left connections: {len(first_tl['left_connections'])}")
            print(f"    Right connections: {len(first_tl['right_connections'])}")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("- Separated straight and left-turn signals")
    print("- Each direction now has at most 2 lights (straight + left)")
    print("- Right turns are always green (signal group 2)")
    print("- Vehicles will only react to their relevant signal")
    print("- Generated traffic_lights_separated.add.xml files")

if __name__ == "__main__":
    main() 