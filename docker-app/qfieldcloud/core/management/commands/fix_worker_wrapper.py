from django.core.management.base import BaseCommand
import os
import re

class Command(BaseCommand):
    help = 'Fix the worker_wrapper container_timeout_secs issue'

    def handle(self, *args, **options):
        # Path to the wrapper.py file
        wrapper_file_path = '/usr/src/app/worker_wrapper/wrapper.py'
        
        # Check if the file exists
        if not os.path.exists(wrapper_file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {wrapper_file_path}'))
            self.stdout.write('This command must be run inside the app container')
            return
        
        # Read the current content of the file
        with open(wrapper_file_path, 'r') as f:
            content = f.read()
        
        # Find the line with container_timeout_secs
        pattern = r'(self\.container_timeout_secs\s*=\s*)([^#\n]+)'
        match = re.search(pattern, content)
        
        if not match:
            self.stdout.write(self.style.ERROR('Could not find container_timeout_secs in the file'))
            return
        
        # Get the current assignment
        current_assignment = match.group(2).strip()
        
        # Create the new assignment with int() conversion
        if 'int' not in current_assignment:
            new_assignment = f'int({current_assignment})'
        else:
            new_assignment = current_assignment
        
        # Replace the line
        new_content = re.sub(pattern, f'\\1{new_assignment}', content)
        
        # Write the updated content back to the file
        with open(wrapper_file_path, 'w') as f:
            f.write(new_content)
        
        self.stdout.write(self.style.SUCCESS(f'Updated {wrapper_file_path}'))
        self.stdout.write(f'Changed container_timeout_secs assignment from "{current_assignment}" to "{new_assignment}"')
        self.stdout.write('Restart the worker_wrapper service for the changes to take effect:')
        self.stdout.write('docker-compose restart worker_wrapper')
