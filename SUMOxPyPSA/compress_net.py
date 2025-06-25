import gzip
import shutil
import os
import sys

def compress_file(input_file):
    """Compress a file using gzip compression"""
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist")
        return False
    
    output_file = input_file + '.gz'
    try:
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"Successfully compressed {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Error compressing file: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compress_net.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    compress_file(input_file) 