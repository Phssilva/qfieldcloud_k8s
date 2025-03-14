from django.core.management.base import BaseCommand
from django.conf import settings
import logging

class Command(BaseCommand):
    help = 'Fix legacy storage configuration to make status command work'

    def handle(self, *args, **options):
        self.stdout.write('Fixing legacy storage configuration...')
        
        try:
            # Check if LEGACY_STORAGE_NAME is set to a valid value
            if not hasattr(settings, 'LEGACY_STORAGE_NAME') or settings.LEGACY_STORAGE_NAME == '':
                self.stdout.write(self.style.WARNING('LEGACY_STORAGE_NAME is not set or is empty'))
                self.stdout.write('Setting LEGACY_STORAGE_NAME to "default"...')
                # We can't modify settings directly, but we can set it as an attribute
                settings.LEGACY_STORAGE_NAME = 'default'
                self.stdout.write(self.style.SUCCESS('LEGACY_STORAGE_NAME set to "default"'))
            else:
                self.stdout.write(f'LEGACY_STORAGE_NAME is already set to "{settings.LEGACY_STORAGE_NAME}"')
            
            # Check if the storage configuration exists
            if settings.LEGACY_STORAGE_NAME not in settings.STORAGES:
                self.stdout.write(self.style.ERROR(f'Storage "{settings.LEGACY_STORAGE_NAME}" not found in STORAGES'))
                # If default storage exists, let's try to use that
                if 'default' in settings.STORAGES:
                    self.stdout.write('Setting LEGACY_STORAGE_NAME to "default" instead...')
                    settings.LEGACY_STORAGE_NAME = 'default'
                else:
                    self.stdout.write(self.style.ERROR('No valid storage configuration found'))
                    return
            
            # Print the current storage configuration
            storage_config = settings.STORAGES[settings.LEGACY_STORAGE_NAME]
            self.stdout.write(f'Current storage configuration: {storage_config}')
            
            # Monkey patch the get_legacy_s3_credentials function to work with our configuration
            from qfieldcloud.core import utils
            
            # Define a replacement function that uses our fixed LEGACY_STORAGE_NAME
            def fixed_get_legacy_s3_credentials():
                return settings.STORAGES[settings.LEGACY_STORAGE_NAME]
            
            # Replace the original function with our fixed version
            utils.get_legacy_s3_credentials = fixed_get_legacy_s3_credentials
            
            # Run the status command to check if it works now
            from django.core.management import call_command
            self.stdout.write('Running status command to check if storage is working...')
            call_command('status')
            
            # Provide instructions for permanent fix
            self.stdout.write('\nTo permanently fix the storage configuration, update your .env file to include:')
            self.stdout.write('LEGACY_STORAGE_NAME=default')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fixing legacy storage: {e}'))
