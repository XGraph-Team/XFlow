import gzip
import xml.etree.ElementTree as ET

def extract_tllogics(filename):
    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        for tl in root.findall('tlLogic'):
            print(f"\n<tlLogic id=\"{tl.get('id')}\" type=\"{tl.get('type')}\" programID=\"{tl.get('programID')}\" offset=\"{tl.get('offset')}\">")
            for phase in tl.findall('phase'):
                print(f"    <phase duration=\"{phase.get('duration')}\" state=\"{phase.get('state')}\"/>")
            print("</tlLogic>")

if __name__ == "__main__":
    extract_tllogics('osm.net.xml.gz')