from django.core.management.base import BaseCommand
from django.db import connection
from qfieldcloud.core.models import Project

class Command(BaseCommand):
    help = 'Fix project status by updating the database directly'

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=str, help='ID of the project to fix')

    def handle(self, *args, **options):
        project_id = options['project_id']
        
        try:
            # Get the project
            project = Project.objects.get(id=project_id)
            self.stdout.write(f'Found project: {project.name} (ID: {project.id})')
            self.stdout.write(f'Current status: {project.status}')
            self.stdout.write(f'Current status code: {project.status_code}')
            
            # Update the status directly in the database
            with connection.cursor() as cursor:
                # First, let's find out the table name and column name
                cursor.execute("""
                    SELECT 
                        table_name, 
                        column_name 
                    FROM 
                        information_schema.columns 
                    WHERE 
                        table_schema = 'public' AND 
                        table_name LIKE '%project%' AND 
                        column_name LIKE '%status%'
                """)
                columns = cursor.fetchall()
                
                self.stdout.write(f'Found columns: {columns}')
                
                # Try to update each possible status column
                for table_name, column_name in columns:
                    try:
                        cursor.execute(f"""
                            UPDATE {table_name}
                            SET {column_name} = ''
                            WHERE id = %s
                        """, [project_id])
                        self.stdout.write(self.style.SUCCESS(f'Updated {table_name}.{column_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Failed to update {table_name}.{column_name}: {e}'))
            
            # Reload the project to get the updated status
            project = Project.objects.get(id=project_id)
            self.stdout.write(f'New status: {project.status}')
            self.stdout.write(f'New status code: {project.status_code}')
            
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project not found: {project_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
