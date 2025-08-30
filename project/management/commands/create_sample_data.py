from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random
from project.enum import Status
from project.models import Project, Task, TimeEntry

class Command(BaseCommand):
    """Management command to create sample data for testing."""
    
    help = 'Create sample projects, tasks, and time entries for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--projects',
            type=int,
            default=5,
            help='Number of projects to create (default: 5)'
        )
        parser.add_argument(
            '--tasks-per-project',
            type=int,
            default=8,
            help='Average number of tasks per project (default: 8)'
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        """Create sample data."""
        num_projects = options['projects']
        tasks_per_project = options['tasks_per_project']
        
        self.stdout.write('Creating sample data...')
        
        # Sample project data
        project_templates = [
            {
                'title': 'E-commerce Platform Redesign',
                'description': 'Complete overhaul of the online shopping experience with modern UI/UX and improved performance.'
            },
            {
                'title': 'Mobile App Development',
                'description': 'Native iOS and Android application for customer engagement and loyalty program.'
            },
            {
                'title': 'API Integration Project',
                'description': 'Integration with third-party APIs for payment processing, shipping, and inventory management.'
            },
            {
                'title': 'Database Migration',
                'description': 'Migration from legacy database system to modern cloud-based solution with improved scalability.'
            },
            {
                'title': 'Security Audit & Implementation',
                'description': 'Comprehensive security review and implementation of best practices for data protection.'
            },
            {
                'title': 'Marketing Dashboard',
                'description': 'Analytics dashboard for marketing team with real-time reporting and campaign tracking.'
            },
            {
                'title': 'Customer Support Portal',
                'description': 'Self-service portal for customers with ticketing system and knowledge base.'
            },
        ]
        
        # Sample task templates
        task_templates = [
            ('User Research & Analysis', 'Conduct user interviews and analyze current user behavior patterns'),
            ('Wireframe Creation', 'Create detailed wireframes for all main user flows'),
            ('UI Design Implementation', 'Design and implement the new user interface components'),
            ('Backend API Development', 'Develop RESTful APIs for frontend integration'),
            ('Database Schema Design', 'Design optimized database schema and relationships'),
            ('Frontend Component Development', 'Build reusable React components for the interface'),
            ('Authentication System', 'Implement secure user authentication and authorization'),
            ('Payment Integration', 'Integrate payment gateway with proper error handling'),
            ('Testing & QA', 'Comprehensive testing including unit, integration, and E2E tests'),
            ('Performance Optimization', 'Optimize application performance and loading times'),
            ('Documentation', 'Create technical documentation and user guides'),
            ('Deployment Setup', 'Set up CI/CD pipeline and production deployment'),
        ]
        
        projects_created = 0
        tasks_created = 0
        time_entries_created = 0
        
        for i in range(num_projects):
            # Create project
            template = project_templates[i % len(project_templates)]
            project = Project.objects.create(
                title=f"{template['title']} #{i+1}",
                description=template['description']
            )
            projects_created += 1
            
            # Create tasks for this project
            num_tasks = random.randint(
                max(1, tasks_per_project - 3),
                tasks_per_project + 3
            )
            
            for j in range(num_tasks):
                task_template = random.choice(task_templates)
                
                # Random status distribution
                status_weights = [
                    (Status.DONE, 0.4),
                    (Status.IN_PROGRESS, 0.3),
                    (Status.TODO, 0.3),
                ]
                status = random.choices(
                    [s[0] for s in status_weights],
                    weights=[s[1] for s in status_weights]
                )[0]
                
                # Random estimated time (1-8 hours)
                estimated_hours = random.randint(1, 8)
                estimated_time = timedelta(hours=estimated_hours)
                
                task = Task.objects.create(
                    project=project,
                    title=task_template[0],
                    description=task_template[1],
                    status=status,
                    estimated_time=estimated_time
                )
                tasks_created += 1
                
                # Create time entries for completed and in-progress tasks
                if status in [Status.DONE, Status.IN_PROGRESS]:
                    num_entries = random.randint(1, 4)
                    total_spent = timedelta()
                    
                    for k in range(num_entries):
                        # Random entry duration (15 minutes to 3 hours)
                        entry_minutes = random.randint(15, 180)
                        entry_duration = timedelta(minutes=entry_minutes)
                        
                        # Random start time in the past 30 days
                        days_ago = random.randint(1, 30)
                        start_time = timezone.now() - timedelta(
                            days=days_ago,
                            hours=random.randint(8, 17),
                            minutes=random.randint(0, 59)
                        )
                        
                        end_time = start_time + entry_duration
                        
                        # Don't create entry if it would be in the future
                        if end_time <= timezone.now():
                            TimeEntry.objects.create(
                                task=task,
                                start_time=start_time,
                                end_time=end_time,
                                duration=entry_duration
                            )
                            total_spent += entry_duration
                            time_entries_created += 1
                    
                    # Update task's spent time
                    task.spent_time = total_spent
                    task.save(update_fields=['spent_time'])
                    
                    # Create one active timer for some in-progress tasks
                    if (status == Status.IN_PROGRESS and 
                        random.random() < 0.3):  # 30% chance
                        active_start = timezone.now() - timedelta(
                            minutes=random.randint(5, 120)
                        )
                        TimeEntry.objects.create(
                            task=task,
                            start_time=active_start
                        )
                        time_entries_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'  - {projects_created} projects\n'
                f'  - {tasks_created} tasks\n'
                f'  - {time_entries_created} time entries'
            )
        )