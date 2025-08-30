# Project Dashboard Backend

A professional Django REST API for project and task management with time tracking capabilities.

## Features

- **Authentication System**: Secure login/logout with custom landing page
- **Project Management**: Create, edit, delete, and list projects with pagination and filtering
- **Task Management**: Comprehensive task management with status tracking and time estimation
- **Time Tracking**: Start/stop timers for tasks with automatic time accumulation
- **Dashboard Analytics**: Aggregate metrics and reporting with caching optimization
- **Advanced Filtering**: Search and filter across projects and tasks
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Tech Stack

- **Backend**: Django 5 + Django REST Framework
- **Database**: PostgreSQL (with  fallback)
- **Caching**: Redis for performance optimization
- **Containerization**: Docker & Docker Compose
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Testing**: pytest + factory-boy

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd project-dashboard
   ```

2. **Start the application**
   ```bash
   docker-compose up -d --build
   ```

3. **Run migrations and create sample data**
   ```bash
   docker-compose exec -it web python manage.py migrate
   docker-compose exec -it web python manage.py create_sample_data
   ```

4. **Access the application**
   - API: http://localhost:8000/api/v1/
   - Swagger Documentation: http://localhost:8000/api/docs/
   - Admin Panel: http://localhost:8000/admin/

### Local Development

1. **Setup virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment configuration**
   ```bash
   # Create .env file
   echo "DEBUG=True" > .env
   echo "DATABASE_URL=sqlite:///db.sqlite3" >> .env
   echo "REDIS_URL=redis://localhost:6379/1" >> .env
   ```

3. **Run migrations and create sample data**
   ```bash
   python manage.py migrate
   python manage.py create_sample_data --projects 10 --tasks-per-project 8
   python manage.py createsuperuser
   ```

4. **Start development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Projects
- `GET /api/v1/projects/` - List projects with pagination and filtering
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/{id}/` - Get project details
- `PUT /api/v1/projects/{id}/` - Update project
- `DELETE /api/v1/projects/{id}/` - Delete project

### Tasks
- `GET /api/v1/tasks/` - List tasks with filtering
- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/{id}/` - Get task details
- `PUT /api/v1/tasks/{id}/` - Update task
- `DELETE /api/v1/tasks/{id}/` - Delete task

### Time Tracking
- `POST /api/v1/tasks/{id}/start-timer/` - Start timer for task
- `POST /api/v1/tasks/{id}/stop-timer/` - Stop active timer

### Dashboard
- `GET /api/v1/dashboard/` - Get dashboard overview with metrics

### Tokens
- `POST /api/token/refresh/` - Refreshes the JWT access token using a valid refresh token.
- `POST /api/token/` - Obtain JWT access and refresh tokens for authentication.

### Authentication
- `POST /api/auth/logout/` - For Logging out
- `POST /api/auth/register/` - For Logging out



## Architecture Highlights

### Performance Optimizations
- **Database**: Optimized queries with `select_related()` and `prefetch_related()`
- **Caching**: Redis caching for dashboard metrics and frequent queries
- **Indexing**: Strategic database indexes on frequently queried fields
- **Pagination**: Efficient pagination for large datasets

### Code Quality
- **Type Hints**: Full type annotation throughout the codebase
- **Transaction Safety**: `@transaction.atomic` for data consistency
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Logging**: Structured logging for debugging and monitoring

### Security
- **Validation**: Input validation at serializer and model levels
- **Constraints**: Database-level constraints for data integrity
- **UUID**: UUIDs as primary keys to prevent enumeration attacks

## Testing

Run the test suite:

```bash
# Using Docker
docker-compose exec web bash pytest --cov=project

# Local development
pytest --cov=project
```

## Development Notes

### What I Enjoyed
- Implementing the time tracking system with database constraints
- Optimizing queries with Django ORM features
- Creating comprehensive API documentation + Custom Landing Page for accessing API's
- Building a robust caching strategy using Redis

### What Could Be Improved With More Time
- **WebSocket Integration**: Real-time timer updates
- **Advanced Analytics**: More detailed reporting and charts
- **File Uploads**: Task attachments and project documents
- **Notification System**: Email/push notifications for task updates


### Satisfied Components
- **Database Design**: Well-normalized schema with proper relationships
- **API Architecture**: RESTful design with consistent patterns
- **Performance**: Efficient queries and caching implementation