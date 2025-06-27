import gzip
import xml.etree.ElementTree as ET

def get_tllogic_ids_from_net(netfile):
    ids = set()
    with gzip.open(netfile, 'rt', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        for tl in root.findall('tlLogic'):
            tid = tl.get('id')
            if tid is not None:
                ids.add(tid)
    return ids

def get_tllogic_ids_from_add(addfile):
    ids = set()
    tree = ET.parse(addfile)
    root = tree.getroot()
    for tl in root.findall('tlLogic'):
        tid = tl.get('id')
        if tid is not None:
            ids.add(tid)
    return ids

if __name__ == "__main__":
    netfile = 'osm.net.xml.gz'
    addfile = 'traffic_lights.add.xml'
    print(f"Checking network file: {netfile}")
    print(f"Checking add file: {addfile}")

    net_ids = get_tllogic_ids_from_net(netfile)
    add_ids = get_tllogic_ids_from_add(addfile)

    print(f"\nTraffic light IDs in network file ({len(net_ids)}):")
    print(sorted(net_ids))

    print(f"\nTraffic light IDs in add file ({len(add_ids)}):")
    print(sorted(add_ids))

    missing = add_ids - net_ids
    if missing:
        print(f"\nIDs in add file but NOT in network file ({len(missing)}):")
        print(sorted(missing))
    else:
        print("\nAll add file IDs are present in the network file.")

    extra = net_ids - add_ids
    if extra:
        print(f"\nIDs in network file but NOT in add file ({len(extra)}):")
        print(sorted(extra))
    else:
        print("\nAll network file IDs are present in the add file.")