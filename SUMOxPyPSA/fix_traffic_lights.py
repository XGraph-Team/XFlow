#!/usr/bin/env python3
"""
Script to fix traffic light logic by adding all-red phases and ensuring proper cycling
"""

import gzip
import xml.etree.ElementTree as ET
import re
import os

def fix_traffic_light_logic(input_file, output_file):
    """
    Fix traffic light logic by adding all-red phases between direction changes
    """
    print(f"Processing {input_file}...")
    
    # Read the network file
    with gzip.open(input_file, 'rt', encoding='utf-8') as f:
        content = f.read()
    
    # Parse XML
    root = ET.fromstring(content)
    
    # Find all tlLogic elements
    tllogics = root.findall('tlLogic')
    print(f"Found {len(tllogics)} traffic light logics")
    
    fixed_count = 0
    
    for tl in tllogics:
        tl_id = tl.get('id')
        print(f"\nProcessing traffic light: {tl_id}")
        
        phases = tl.findall('phase')
        if len(phases) < 2:
            print(f"  Skipping {tl_id}: insufficient phases")
            continue
        
        # Get the state length from the first phase
        first_state = phases[0].get('state')
        state_length = len(first_state)
        print(f"  State length: {state_length}")
        
        # Create new phases with all-red phases inserted
        new_phases = []
        
        for i, phase in enumerate(phases):
            duration = int(phase.get('duration'))
            state = phase.get('state')
            
            # Add the original phase
            new_phases.append({
                'duration': duration,
                'state': state
            })
            
            # Check if this is a yellow phase and next phase is green
            if 'y' in state.lower() and i < len(phases) - 1:
                next_state = phases[i + 1].get('state')
                if 'g' in next_state.lower():
                    # Insert all-red phase between yellow and green
                    all_red_state = 'r' * state_length
                    new_phases.append({
                        'duration': 2,  # 2 seconds all-red
                        'state': all_red_state
                    })
                    print(f"  Added all-red phase after phase {i+1}")
        
        # Replace the phases in the XML
        tl.clear()
        for attr, value in tl.attrib.items():
            tl.set(attr, value)
        
        for phase_data in new_phases:
            phase_elem = ET.SubElement(tl, 'phase')
            phase_elem.set('duration', str(phase_data['duration']))
            phase_elem.set('state', phase_data['state'])
        
        fixed_count += 1
        print(f"  Fixed {tl_id}: {len(phases)} phases -> {len(new_phases)} phases")
    
    # Write the fixed network file
    print(f"\nWriting fixed network to {output_file}...")
    
    # Create the XML tree
    tree = ET.ElementTree(root)
    
    # Write to gzipped file
    with gzip.open(output_file, 'wt', encoding='utf-8') as f:
        # Write XML declaration
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        
        # Convert to string and write
        xml_str = ET.tostring(root, encoding='unicode')
        f.write(xml_str)
    
    print(f"Fixed {fixed_count} traffic light logics")
    print(f"Output written to: {output_file}")

def create_fixed_add_file(city_dir):
    """
    Create a fixed traffic_lights.add.xml file with proper phase cycling
    """
    add_file = os.path.join(city_dir, 'traffic_lights.add.xml')
    fixed_add_file = os.path.join(city_dir, 'traffic_lights_fixed.add.xml')
    
    print(f"Creating fixed traffic lights file: {fixed_add_file}")
    
    # Create a template for a 4-way intersection with proper cycling
    template = '''<?xml version="1.0" encoding="UTF-8"?>
<additional>
    <!-- Template for 4-way intersection with proper green-yellow-red-green cycling -->
    <tlLogic id="intersection_template" type="static" programID="0" offset="0">
        <!-- Phase 1: North-South green, East-West red -->
        <phase duration="15" state="GGGGrrrr"/>
        <!-- Phase 2: North-South yellow, East-West red -->
        <phase duration="3" state="yyyyrrrr"/>
        <!-- Phase 3: All red (safety buffer) -->
        <phase duration="2" state="rrrrrrrr"/>
        <!-- Phase 4: East-West green, North-South red -->
        <phase duration="15" state="rrrrGGGG"/>
        <!-- Phase 5: East-West yellow, North-South red -->
        <phase duration="3" state="rrrryyyy"/>
        <!-- Phase 6: All red (safety buffer) -->
        <phase duration="2" state="rrrrrrrr"/>
    </tlLogic>
    
    <!-- Template for complex intersection with more signal groups -->
    <tlLogic id="complex_intersection_template" type="static" programID="0" offset="0">
        <!-- Phase 1: Main directions green -->
        <phase duration="15" state="GGGGGGGrrrrrrrrrrrrrrr"/>
        <!-- Phase 2: Main directions yellow -->
        <phase duration="3" state="yyyyyyyrrrrrrrrrrrrrrr"/>
        <!-- Phase 3: All red -->
        <phase duration="2" state="rrrrrrrrrrrrrrrrrrrrrrr"/>
        <!-- Phase 4: Cross directions green -->
        <phase duration="15" state="rrrrrrrGGGGGGGrrrrrrrr"/>
        <!-- Phase 5: Cross directions yellow -->
        <phase duration="3" state="rrrrrrryyyyyyyrrrrrrrr"/>
        <!-- Phase 6: All red -->
        <phase duration="2" state="rrrrrrrrrrrrrrrrrrrrrrr"/>
    </tlLogic>
</additional>'''
    
    with open(fixed_add_file, 'w') as f:
        f.write(template)
    
    print(f"Created template file: {fixed_add_file}")
    print("You can use this as a reference for creating proper traffic light logic")

def main():
    """Main function"""
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    cities = ['miami', 'los_angeles', 'new_york']
    
    print("Traffic Light Logic Fixer")
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
        
        # Create backup
        backup_file = os.path.join(city_dir, 'osm.net.xml.gz.backup')
        if not os.path.exists(backup_file):
            import shutil
            shutil.copy2(net_file, backup_file)
            print(f"Created backup: {backup_file}")
        
        # Fix the network file
        fixed_net_file = os.path.join(city_dir, 'osm.net.xml.gz.fixed')
        fix_traffic_light_logic(net_file, fixed_net_file)
        
        # Create template add file
        create_fixed_add_file(city_dir)
        
        print(f"\nFor {city}:")
        print(f"  - Original: {net_file}")
        print(f"  - Fixed: {fixed_net_file}")
        print(f"  - Backup: {backup_file}")
        print(f"  - Template: {city_dir}/traffic_lights_fixed.add.xml")
    
    print("\n" + "=" * 50)
    print("Next steps:")
    print("1. Review the fixed network files")
    print("2. If satisfied, replace the original files:")
    print("   mv osm.net.xml.gz.fixed osm.net.xml.gz")
    print("3. Use the template files as reference for custom traffic light logic")
    print("4. Test the simulation to ensure proper traffic light cycling")

if __name__ == "__main__":
    main()