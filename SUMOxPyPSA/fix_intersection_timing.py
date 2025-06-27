#!/usr/bin/env python3
"""
Script to fix synchronized traffic lights at intersections by creating opposing logic
"""

import gzip
import xml.etree.ElementTree as ET
import os
import re

def analyze_intersection_traffic_lights(netfile):
    """Analyze traffic lights to find which ones are at the same intersection"""
    intersections = {}
    
    with gzip.open(netfile, 'rt', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
        # First, get all traffic lights and their controlled links
        traffic_lights = {}
        for tl in root.findall('tlLogic'):
            tl_id = tl.get('id')
            if tl_id is None:
                continue
            
            # Get controlled links for this traffic light
            controlled_links = []
            for connection in root.findall('connection'):
                if connection.get('tl') == tl_id:
                    controlled_links.append({
                        'from': connection.get('from'),
                        'to': connection.get('to'),
                        'fromLane': connection.get('fromLane'),
                        'toLane': connection.get('toLane')
                    })
            
            traffic_lights[tl_id] = {
                'controlled_links': controlled_links,
                'phases': []
            }
            
            # Get phases
            for phase in tl.findall('phase'):
                duration = phase.get('duration')
                state = phase.get('state')
                if duration and state:
                    traffic_lights[tl_id]['phases'].append({
                        'duration': int(duration),
                        'state': state
                    })
        
        # Group traffic lights by intersection (junction)
        for tl_id, tl_info in traffic_lights.items():
            if not tl_info['controlled_links']:
                continue
            
            # Find the junction this traffic light controls
            # We'll use the 'from' edge to find the junction
            from_edge = tl_info['controlled_links'][0]['from']
            
            # Find the junction that connects this edge
            for junction in root.findall('junction'):
                junction_id = junction.get('id')
                if junction_id:
                    # Check if this junction has the from_edge as an incoming edge
                    for inc in junction.findall('incLane'):
                        edge_id = inc.get('id').split('_')[0]  # Remove lane suffix
                        if edge_id == from_edge:
                            if junction_id not in intersections:
                                intersections[junction_id] = []
                            intersections[junction_id].append(tl_id)
                            break
    
    return intersections, traffic_lights

def create_opposing_traffic_light_logic(traffic_lights, intersections):
    """Create opposing traffic light logic for intersections"""
    opposing_logic = {}
    
    for junction_id, tl_ids in intersections.items():
        if len(tl_ids) < 2:
            continue  # Skip single traffic light intersections
        
        print(f"Processing intersection {junction_id} with {len(tl_ids)} traffic lights")
        
        # Create opposing logic for this intersection
        opposing_logic[junction_id] = {}
        
        for i, tl_id in enumerate(tl_ids):
            if tl_id not in traffic_lights:
                continue
            
            original_phases = traffic_lights[tl_id]['phases']
            if not original_phases:
                continue
            
            # Create opposing phases with offset
            offset = (i * 50) % 100  # Offset each traffic light by 50% of cycle
            
            # Create 4-phase logic: Green1 -> Yellow1 -> Red -> Green2 -> Yellow2 -> Red
            state_length = len(original_phases[0]['state'])
            
            # Determine which lanes should be green in each phase
            # This is a simplified approach - you may need to customize based on your network
            if i == 0:  # First traffic light - North/South
                phase1_state = 'G' * (state_length // 2) + 'r' * (state_length // 2)
                phase2_state = 'y' * (state_length // 2) + 'r' * (state_length // 2)
                phase3_state = 'r' * state_length
                phase4_state = 'r' * (state_length // 2) + 'G' * (state_length // 2)
                phase5_state = 'r' * (state_length // 2) + 'y' * (state_length // 2)
            else:  # Second traffic light - East/West (opposite timing)
                phase1_state = 'r' * (state_length // 2) + 'G' * (state_length // 2)
                phase2_state = 'r' * (state_length // 2) + 'y' * (state_length // 2)
                phase3_state = 'r' * state_length
                phase4_state = 'G' * (state_length // 2) + 'r' * (state_length // 2)
                phase5_state = 'y' * (state_length // 2) + 'r' * (state_length // 2)
            
            opposing_logic[junction_id][tl_id] = {
                'offset': offset,
                'phases': [
                    {'duration': 15, 'state': phase1_state},  # Green
                    {'duration': 3, 'state': phase2_state},   # Yellow
                    {'duration': 2, 'state': phase3_state},   # All Red
                    {'duration': 15, 'state': phase4_state},  # Green (opposite)
                    {'duration': 3, 'state': phase5_state},   # Yellow
                    {'duration': 2, 'state': phase3_state},   # All Red
                ]
            }
    
    return opposing_logic

def generate_opposing_traffic_lights_xml(opposing_logic, output_file):
    """Generate traffic_lights.add.xml with opposing logic"""
    
    root = ET.Element('additional')
    
    for junction_id, tl_logics in opposing_logic.items():
        for tl_id, tl_info in tl_logics.items():
            # Create tlLogic element
            tl_elem = ET.SubElement(root, 'tlLogic')
            tl_elem.set('id', tl_id)
            tl_elem.set('type', 'static')
            tl_elem.set('programID', '0')
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
    
    return len([tl for junction in opposing_logic.values() for tl in junction.keys()])

def main():
    """Main function"""
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    cities = ['miami', 'los_angeles', 'new_york']
    
    print("Traffic Light Opposition Generator")
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
        
        # Analyze intersections
        intersections, traffic_lights = analyze_intersection_traffic_lights(net_file)
        
        print(f"  Found {len(intersections)} intersections")
        print(f"  Found {len(traffic_lights)} traffic lights")
        
        # Create opposing logic
        opposing_logic = create_opposing_traffic_light_logic(traffic_lights, intersections)
        
        # Generate the add file
        output_file = os.path.join(city_dir, 'traffic_lights_opposing.add.xml')
        count = generate_opposing_traffic_lights_xml(opposing_logic, output_file)
        
        print(f"  Generated {output_file} with {count} opposing traffic lights")
        
        # Show example
        if opposing_logic:
            first_junction = list(opposing_logic.keys())[0]
            first_tls = list(opposing_logic[first_junction].keys())
            print(f"  Example intersection {first_junction}: {first_tls}")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("- Generated opposing traffic light logic for intersections")
    print("- Traffic lights at same intersection now have different phase offsets")
    print("- Created traffic_lights_opposing.add.xml files")
    print("- Use these files instead of the synchronized ones")

if __name__ == "__main__":
    main() 