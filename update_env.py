#!/usr/bin/env python3

import os
import re

def update_env_file(env_file_path):
    """Update the .env file with LEGACY_STORAGE_NAME=default"""
    
    # Read the current .env file
    with open(env_file_path, 'r') as f:
        content = f.read()
    
    # Check if LEGACY_STORAGE_NAME is already defined
    if re.search(r'^LEGACY_STORAGE_NAME=', content, re.MULTILINE):
        # Update the existing LEGACY_STORAGE_NAME
        content = re.sub(
            r'^LEGACY_STORAGE_NAME=.*$',
            'LEGACY_STORAGE_NAME=default',
            content,
            flags=re.MULTILINE
        )
    else:
        # Add LEGACY_STORAGE_NAME at the end of the file
        if not content.endswith('\n'):
            content += '\n'
        content += 'LEGACY_STORAGE_NAME=default\n'
    
    # Write the updated content back to the .env file
    with open(env_file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {env_file_path} with LEGACY_STORAGE_NAME=default")

if __name__ == "__main__":
    env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    update_env_file(env_file_path)
