from django.core.management.base import BaseCommand
from django.conf import settings
from qfieldcloud.core.models import Project, ProcessProjectfileJob, Job

class Command(BaseCommand):
    help = 'Fix all projects by triggering project processing'

    def handle(self, *args, **options):
        # Ensure LEGACY_STORAGE_NAME is set correctly
        if not hasattr(settings, 'LEGACY_STORAGE_NAME') or not settings.LEGACY_STORAGE_NAME:
            self.stdout.write(self.style.WARNING('Setting LEGACY_STORAGE_NAME to "default"'))
            settings.LEGACY_STORAGE_NAME = 'default'
        
        # Get all projects
        projects = Project.objects.all()
        self.stdout.write(f'Found {len(projects)} projects')
        
        for project in projects:
            self.stdout.write(f'Processing project: {project.name} (ID: {project.id})')
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
                continue
            
            # Create a new job to process the project
            try:
                job = ProcessProjectfileJob.objects.create(
                    project=project,
                    type=Job.Type.PROCESS_PROJECTFILE,
                    status=Job.Status.PENDING,
                    created_by=project.owner
                )
                
                self.stdout.write(self.style.SUCCESS(f'Created new job to process project: {job.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating job: {e}'))
        
        # Provide instructions
        self.stdout.write('\nInstructions:')
        self.stdout.write('1. Wait a few moments for the projects to be processed')
        self.stdout.write('2. Check the project status again with:')
        self.stdout.write('   docker-compose exec app python manage.py shell -c "from qfieldcloud.core.models import Project; print([(p.name, p.status) for p in Project.objects.all()])"')
        self.stdout.write('3. If any project is still "failed", restart the worker_wrapper service:')
        self.stdout.write('   docker-compose restart worker_wrapper')
