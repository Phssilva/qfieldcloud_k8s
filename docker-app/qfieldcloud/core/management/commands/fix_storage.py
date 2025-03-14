from django.core.management.base import BaseCommand
from django.conf import settings
import os
import boto3
from botocore.client import Config

class Command(BaseCommand):
    help = 'Fix storage configuration and test connection'

    def handle(self, *args, **options):
        self.stdout.write('Fixing storage configuration...')
        
        try:
            # Get the current storage configuration
            storage_config = settings.STORAGES.get('default', {})
            options = storage_config.get('OPTIONS', {})
            
            # Create a direct connection to MinIO with fixed configuration
            endpoint_url = options.get('endpoint_url')
            access_key = options.get('access_key')
            secret_key = options.get('secret_key')
            bucket_name = options.get('bucket_name')
            
            self.stdout.write(f'Connecting to MinIO at {endpoint_url}')
            self.stdout.write(f'Using bucket: {bucket_name}')
            
            # Create S3 client with addressing_style='path' to fix region issues
            s3 = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1',  # Use a default region
                config=Config(s3={'addressing_style': 'path'})  # Use path style instead of virtual-hosted style
            )
            
            # Test connection by listing buckets
            self.stdout.write('Testing connection by listing buckets...')
            buckets = s3.list_buckets()
            for bucket in buckets['Buckets']:
                self.stdout.write(f'- {bucket["Name"]}')
            
            # Check if our bucket exists
            self.stdout.write(f'Checking if bucket {bucket_name} exists...')
            bucket_exists = False
            for bucket in buckets['Buckets']:
                if bucket['Name'] == bucket_name:
                    bucket_exists = True
                    break
            
            if not bucket_exists:
                self.stdout.write(f'Creating bucket {bucket_name}...')
                s3.create_bucket(Bucket=bucket_name)
                self.stdout.write(self.style.SUCCESS(f'Bucket {bucket_name} created successfully'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Bucket {bucket_name} already exists'))
            
            # Test file operations
            self.stdout.write('Testing file operations...')
            test_key = 'test-file.txt'
            test_content = b'This is a test file'
            
            # Upload a test file
            s3.put_object(Bucket=bucket_name, Key=test_key, Body=test_content)
            self.stdout.write(self.style.SUCCESS(f'Test file uploaded to {test_key}'))
            
            # Download the test file
            response = s3.get_object(Bucket=bucket_name, Key=test_key)
            content = response['Body'].read()
            self.stdout.write(self.style.SUCCESS(f'Test file downloaded, content: {content}'))
            
            # Delete the test file
            s3.delete_object(Bucket=bucket_name, Key=test_key)
            self.stdout.write(self.style.SUCCESS('Test file deleted'))
            
            self.stdout.write(self.style.SUCCESS('Storage configuration is working correctly!'))
            
            # Provide instructions for updating .env file
            self.stdout.write('\nTo permanently fix the storage configuration, update your .env file with:')
            self.stdout.write('STORAGES=\'{\n    "default": {\n        "BACKEND": "qfieldcloud.filestorage.backend.QfcS3Boto3Storage",\n        "OPTIONS": {\n            "access_key": "minioadmin",\n            "secret_key": "minioadmin",\n            "bucket_name": "qfieldcloud-local",\n            "region_name": "us-east-1",\n            "endpoint_url": "http://minio:9000"\n        },\n        "QFC_IS_LEGACY": false\n    }\n}\'')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fixing storage: {e}'))
