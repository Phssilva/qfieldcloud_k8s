from django.core.management.base import BaseCommand
import os
import boto3
from django.conf import settings
from qfieldcloud.core.models import Project
from qfieldcloud.core.utils import get_project_file_with_full_path, get_storage_object

class Command(BaseCommand):
    help = 'Create a valid QGIS project file for a specified project'

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=str, help='ID of the project to fix')

    def handle(self, *args, **options):
        project_id = options['project_id']
        
        try:
            # Get the project
            project = Project.objects.get(id=project_id)
            self.stdout.write(f'Found project: {project.name} (ID: {project.id})')
            self.stdout.write(f'Current status: {project.status}')
            
            # Set legacy storage name if needed
            if hasattr(settings, 'LEGACY_STORAGE_NAME'):
                self.stdout.write(f'Setting LEGACY_STORAGE_NAME to "{settings.LEGACY_STORAGE_NAME}"')
            else:
                self.stdout.write(self.style.WARNING('LEGACY_STORAGE_NAME not set in settings'))
            
            # Create a minimal valid QGIS project file
            qgis_project_content = f'''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="{project.name}" version="3.16.0-Hannover">
  <title>{project.name}</title>
  <projectCrs>
    <spatialrefsys>
      <wkt>GEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["unknown"],AREA["World"],BBOX[-90,-180,90,180]],ID["EPSG",4326]]</wkt>
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
'''
            
            # Get the storage object
            storage = get_storage_object(project.owner)
            
            # Create the project directory if it doesn't exist
            project_path = f'projects/{project.id}'
            
            # Define the QGIS project file name
            qgs_filename = f'{project.name}.qgs'
            qgs_key = f'{project_path}/{qgs_filename}'
            
            # Check if the file already exists
            try:
                existing_files = storage.listdir(project_path)[1]  # [1] contains files
                self.stdout.write(f'Found existing files: {existing_files}')
                
                if qgs_filename in existing_files:
                    self.stdout.write(self.style.WARNING(f'QGIS project file already exists: {qgs_key}'))
                    # Update the project's QGIS file name if needed
                    if project.the_qgis_file_name != qgs_filename:
                        project.the_qgis_file_name = qgs_filename
                        project.save(update_fields=['the_qgis_file_name'])
                        self.stdout.write(self.style.SUCCESS(f'Updated project.the_qgis_file_name to: {qgs_filename}'))
                    return
            except Exception as e:
                self.stdout.write(f'Error checking existing files: {e}')
                # Directory might not exist, create it
                pass
            
            # Upload the QGIS project file
            storage.save(qgs_key, qgis_project_content)
            
            # Update the project's QGIS file name
            project.the_qgis_file_name = qgs_filename
            project.save(update_fields=['the_qgis_file_name'])
            
            self.stdout.write(self.style.SUCCESS(f'Created QGIS project file: {qgs_key}'))
            self.stdout.write(self.style.SUCCESS(f'Updated project.the_qgis_file_name to: {qgs_filename}'))
            
            # Create a job to process the project
            from qfieldcloud.core.models import Job, ProcessProjectfileJob
            
            # Check if there are already running jobs for this project
            running_jobs = ProcessProjectfileJob.objects.filter(
                project=project,
                status__in=[Job.Status.PENDING, Job.Status.QUEUED, Job.Status.STARTED]
            )
            
            if running_jobs.exists():
                self.stdout.write(self.style.WARNING(f'There are already {running_jobs.count()} running jobs for this project'))
                for job in running_jobs:
                    self.stdout.write(f'- Job ID: {job.id}, Status: {job.status}')
            else:
                # Create a new job to process the project
                job = ProcessProjectfileJob.objects.create(
                    project=project,
                    type=Job.Type.PROCESS_PROJECTFILE,
                    status=Job.Status.PENDING,
                    created_by=project.owner
                )
                self.stdout.write(self.style.SUCCESS(f'Created new job to process the project: {job.id}'))
            
            # Reload the project to get the updated status
            project = Project.objects.get(id=project.id)
            self.stdout.write(f'Current project status: {project.status}')
            
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project not found: {project_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
