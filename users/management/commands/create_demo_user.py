from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    """Management command to create a demo user for testing."""
    
    help = 'Create demo user for testing login functionality'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@devsecurity.com',
            help='Demo user email (default: admin@devsecurity.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Demo user password (default: admin123)'
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Create as superuser (default: False)'
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        """Create demo user."""
        email = options['email']
        password = options['password']
        is_superuser = options['superuser']
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            return
        
        # Create user
        user_data = {
            'email': email,
            'first_name': 'Demo',
            'last_name': 'User',
            'is_active': True,
            'is_staff': is_superuser,
            'is_superuser': is_superuser,
        }
        
        if is_superuser:
            user = User.objects.create_superuser(password=password, **user_data)
        else:
            user = User.objects.create_user(password=password, **user_data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {"superuser" if is_superuser else "user"}: {email}\n'
                f'Password: {password}\n'
                f'Use these credentials to login at the landing page.'
            )
        )