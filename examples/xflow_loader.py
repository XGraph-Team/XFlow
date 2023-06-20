import sys
import os
current_script_directory = os.path.dirname(os.path.abspath(__file__))
xflow_path = os.path.join(current_script_directory, '..', '..', 'xflow')
sys.path.insert(1, xflow_path)