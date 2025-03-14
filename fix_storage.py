#!/usr/bin/env python
import json
import os

# Read the current .env file
env_path = os.path.join(os.getcwd(), '.env')
with open(env_path, 'r') as f:
    lines = f.readlines()

# Find the STORAGES configuration
new_lines = []
for line in lines:
    if line.startswith('STORAGES='):
        # Parse the current JSON
        storage_json_str = line[9:].strip()
        try:
            storage_config = json.loads(storage_json_str)
            
            # Fix the region_name - set it to a valid value
            if 'default' in storage_config and 'OPTIONS' in storage_config['default']:
                if storage_config['default']['OPTIONS']['region_name'] == '':
                    storage_config['default']['OPTIONS']['region_name'] = 'us-east-1'  # Default S3 region
                
            # Convert back to JSON string
            new_storage_json = json.dumps(storage_config, indent=4)
            new_lines.append(f'STORAGES={new_storage_json}\n')
        except json.JSONDecodeError:
            # If we can't parse it, keep the original line
            new_lines.append(line)
    else:
        new_lines.append(line)

# Write the updated .env file
with open(env_path, 'w') as f:
    f.writelines(new_lines)

print("Storage configuration updated successfully!")
