#!/usr/bin/env python3

import os
import re

def update_env_file(env_file_path):
    """Update the .env file with worker configuration"""
    
    # Read the current .env file
    with open(env_file_path, 'r') as f:
        content = f.read()
    
    # Add configurations if they don't exist
    configs_to_add = {
        'QFIELDCLOUD_WORKER_CONTAINER_TIMEOUT_SECS': '3600',
        'LEGACY_STORAGE_NAME': 'default'
    }
    
    for key, value in configs_to_add.items():
        # Check if configuration already exists
        if re.search(f'^{key}=', content, re.MULTILINE):
            # Update the existing configuration
            content = re.sub(
                f'^{key}=.*$',
                f'{key}={value}',
                content,
                flags=re.MULTILINE
            )
        else:
            # Add configuration at the end of the file
            if not content.endswith('\n'):
                content += '\n'
            content += f'{key}={value}\n'
    
    # Write the updated content back to the .env file
    with open(env_file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {env_file_path} with worker configurations")

if __name__ == "__main__":
    env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    update_env_file(env_file_path)
