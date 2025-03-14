from django.core.management.base import BaseCommand
from django.conf import settings
from qfieldcloud.core.models import Project, ProcessProjectfileJob, Job

class Command(BaseCommand):
    help = 'Trigger project processing for a project'

    def add_arguments(self, parser):
        parser.add_argument('project_name', type=str, help='Name of the project to process')

    def handle(self, *args, **options):
        project_name = options['project_name']
        
        try:
            # Get the project
            project = Project.objects.get(name=project_name)
            self.stdout.write(f'Found project: {project.name} (ID: {project.id})')
            self.stdout.write(f'Current status: {project.status}')
            
            # Check if there are already running jobs for this project
            running_jobs = ProcessProjectfileJob.objects.filter(
                project=project,
                status__in=[Job.Status.PENDING, Job.Status.QUEUED, Job.Status.STARTED]
            )
            
            if running_jobs.exists():
                self.stdout.write(self.style.WARNING(f'There are already {running_jobs.count()} running jobs for this project'))
                for job in running_jobs:
                    self.stdout.write(f'- Job ID: {job.id}, Status: {job.status}')
            
            # Create a new job to process the project
            job = ProcessProjectfileJob.objects.create(
                project=project,
                type=Job.Type.PROCESS_PROJECTFILE,
                status=Job.Status.PENDING,
                created_by=project.owner
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created new job to process project: {job.id}'))
            
            # Provide instructions
            self.stdout.write('\nInstructions:')
            self.stdout.write('1. Wait a few moments for the project to be processed')
            self.stdout.write('2. Check the project status again with:')
            self.stdout.write('   docker-compose exec app python manage.py shell -c "from qfieldcloud.core.models import Project; p = Project.objects.get(name=\'teste\'); print(\'Status:\', p.status)"')
            self.stdout.write('3. If the status is still "failed", check the job status with:')
            self.stdout.write(f'   docker-compose exec app python manage.py shell -c "from qfieldcloud.core.models import Job; j = Job.objects.get(id=\'{job.id}\'); print(\'Status:\', j.status); print(\'Feedback:\', j.feedback)"')
            self.stdout.write('4. Make sure the worker is running:')
            self.stdout.write('   docker-compose ps worker')
            self.stdout.write('5. If the worker is not running, start it with:')
            self.stdout.write('   docker-compose up -d worker')
            
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project not found: {project_name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
