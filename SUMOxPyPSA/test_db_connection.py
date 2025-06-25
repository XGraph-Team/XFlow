#!/bin/python
import os
import subprocess
import sys

# Set the same environment variables as in map_to_power.py
os.environ['PGUSER'] = 'gridkit'
os.environ['PGHOST'] = 'localhost'
os.environ['PGPORT'] = '5432'
os.environ['PGDATABASE'] = 'gridkit'
os.environ['PGPASSWORD'] = 'gridkit123'

print("Testing PostgreSQL connection with these parameters:")
print(f"PGUSER: {os.environ.get('PGUSER')}")
print(f"PGHOST: {os.environ.get('PGHOST')}")
print(f"PGPORT: {os.environ.get('PGPORT')}")
print(f"PGDATABASE: {os.environ.get('PGDATABASE')}")
print(f"PGPASSWORD: {'*' * len(os.environ.get('PGPASSWORD', ''))}")

# Test 1: Try to connect to postgres database first
print("\nTest 1: Connecting to 'postgres' database...")
try:
    result = subprocess.run(['psql', '-c', 'SELECT version();'], 
                          capture_output=True, text=True, timeout=10)
    print(f"Exit code: {result.returncode}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Try to connect to gridkit database
print("\nTest 2: Connecting to 'gridkit' database...")
try:
    result = subprocess.run(['psql', '-d', 'gridkit', '-c', 'SELECT 1;'], 
                          capture_output=True, text=True, timeout=10)
    print(f"Exit code: {result.returncode}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Check if gridkit database exists
print("\nTest 3: Checking if 'gridkit' database exists...")
try:
    result = subprocess.run(['psql', '-c', "SELECT datname FROM pg_database WHERE datname = 'gridkit';"], 
                          capture_output=True, text=True, timeout=10)
    print(f"Exit code: {result.returncode}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Check PostgreSQL service status
print("\nTest 4: Checking PostgreSQL service status...")
try:
    result = subprocess.run(['systemctl', 'status', 'postgresql'], 
                          capture_output=True, text=True, timeout=10)
    print(f"Exit code: {result.returncode}")
    print(f"STDOUT: {result.stdout[:500]}...")  # First 500 chars
    print(f"STDERR: {result.stderr}")
except Exception as e:
    print(f"Error: {e}") 