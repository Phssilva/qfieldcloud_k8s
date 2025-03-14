from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import boto3
from django.conf import settings
import logging

class Command(BaseCommand):
    help = 'Test storage connection and functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing storage connection...')
        
        try:
            # Get storage configuration
            storage_config = settings.STORAGES.get('default', {})
            self.stdout.write(f'Storage backend: {default_storage.__class__.__name__}')
            self.stdout.write(f'Storage config: {storage_config}')
            
            # Test direct connection to MinIO using boto3
            self.stdout.write('Testing direct connection to MinIO...')
            options = storage_config.get('OPTIONS', {})
            s3 = boto3.client(
                's3',
                endpoint_url=options.get('endpoint_url'),
                aws_access_key_id=options.get('access_key'),
                aws_secret_access_key=options.get('secret_key'),
                region_name=options.get('region_name', None)
            )
            
            # List buckets
            self.stdout.write('Listing buckets...')
            buckets = s3.list_buckets()
            for bucket in buckets['Buckets']:
                self.stdout.write(f'- {bucket["Name"]}')
            
            # Test if the configured bucket exists
            bucket_name = options.get('bucket_name')
            self.stdout.write(f'Testing if bucket {bucket_name} exists...')
            try:
                s3.head_bucket(Bucket=bucket_name)
                self.stdout.write(self.style.SUCCESS(f'Bucket {bucket_name} exists'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error checking bucket: {e}'))
                return
            
            # Try to save a file
            self.stdout.write('Trying to save a test file...')
            try:
                path = default_storage.save('test_file.txt', ContentFile(b'This is a test file'))
                self.stdout.write(self.style.SUCCESS(f'File saved successfully at: {path}'))
                
                # Try to read the file
                self.stdout.write('Trying to read the test file...')
                content = default_storage.open(path).read()
                self.stdout.write(self.style.SUCCESS(f'File content: {content}'))
                
                # Try to delete the file
                self.stdout.write('Trying to delete the test file...')
                default_storage.delete(path)
                self.stdout.write(self.style.SUCCESS('File deleted successfully'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error with file operations: {e}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error testing storage: {e}'))
