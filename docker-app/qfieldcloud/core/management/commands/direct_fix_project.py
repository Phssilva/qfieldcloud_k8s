from django.core.management.base import BaseCommand
from django.conf import settings
from qfieldcloud.core.models import Project
import boto3
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Directly fix a project by creating a valid QGIS project file and updating the project status'

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=str, help='ID of the project to fix')

    def handle(self, *args, **options):
        project_id = options['project_id']
        
        # Ensure LEGACY_STORAGE_NAME is set
        if not hasattr(settings, 'LEGACY_STORAGE_NAME') or not settings.LEGACY_STORAGE_NAME:
            settings.LEGACY_STORAGE_NAME = 'default'
            self.stdout.write(self.style.WARNING('Setting LEGACY_STORAGE_NAME to "default"'))
        
        try:
            # Get the project
            project = Project.objects.get(id=project_id)
            self.stdout.write(f'Found project: {project.name} (ID: {project.id})')
            self.stdout.write(f'Current status: {project.status}')
            
            # Configure S3 client
            storage_config = settings.STORAGES['default']
            s3 = boto3.resource(
                's3',
                endpoint_url=storage_config['OPTIONS']['endpoint_url'],
                aws_access_key_id=storage_config['OPTIONS']['access_key'],
                aws_secret_access_key=storage_config['OPTIONS']['secret_key'],
                region_name=storage_config['OPTIONS'].get('region_name', 'us-east-1')
            )
            bucket = s3.Bucket(storage_config['OPTIONS']['bucket_name'])
            
            # Check if a QGIS project file already exists
            project_prefix = f'projects/{project.id}/'
            qgis_files = []
            for obj in bucket.objects.filter(Prefix=project_prefix):
                if obj.key.endswith('.qgs') or obj.key.endswith('.qgz'):
                    qgis_files.append(obj.key)
            
            if qgis_files:
                self.stdout.write(f'Found existing QGIS project files: {qgis_files}')
            else:
                # Create a basic QGIS project file
                self.stdout.write('No QGIS project file found. Creating a new one...')
                
                # Create a basic QGIS project file
                qgs_content = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="" version="3.22.0-Białowieża">
  <homePath path=""/>
  <title></title>
  <projectCrs>
    <spatialrefsys>
      <wkt>GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]</wkt>
      <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
      <srsid>3452</srsid>
      <srid>4326</srid>
      <authid>EPSG:4326</authid>
      <description>WGS 84</description>
      <projectionacronym>longlat</projectionacronym>
      <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
      <geographicflag>true</geographicflag>
    </spatialrefsys>
  </projectCrs>
</qgis>
"""
                
                # Create a temporary file
                temp_file_path = f'/tmp/{project.name}.qgs'
                with open(temp_file_path, 'w') as f:
                    f.write(qgs_content)
                
                # Upload the file to S3
                qgs_key = f'{project_prefix}{project.name}.qgs'
                bucket.upload_file(temp_file_path, qgs_key)
                
                # Clean up
                os.remove(temp_file_path)
                
                self.stdout.write(self.style.SUCCESS(f'Created QGIS project file: {qgs_key}'))
            
            try:
                # Vamos usar uma abordagem diferente: criar um job para processar o projeto
                from qfieldcloud.core.models import Job, ProcessProjectfileJob
                
                # Verificar se já existem jobs em execução para este projeto
                running_jobs = ProcessProjectfileJob.objects.filter(
                    project=project,
                    status__in=[Job.Status.PENDING, Job.Status.QUEUED, Job.Status.STARTED]
                )
                
                if running_jobs.exists():
                    self.stdout.write(self.style.WARNING(f'Já existem {running_jobs.count()} jobs em execução para este projeto'))
                    for job in running_jobs:
                        self.stdout.write(f'- Job ID: {job.id}, Status: {job.status}')
                else:
                    # Criar um novo job para processar o projeto
                    job = ProcessProjectfileJob.objects.create(
                        project=project,
                        type=Job.Type.PROCESS_PROJECTFILE,
                        status=Job.Status.PENDING,
                        created_by=project.owner
                    )
                    self.stdout.write(self.style.SUCCESS(f'Criado novo job para processar o projeto: {job.id}'))
                    
                # Recarregar o projeto para obter o status atualizado
                project = Project.objects.get(id=project.id)
                self.stdout.write(f'Status atual do projeto: {project.status}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao criar job: {e}'))
            
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project not found: {project_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
