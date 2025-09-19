# Conference Booking System

A comprehensive Django-based web application for managing conference bookings within organizations. This system provides role-based access control, approval workflows, and comprehensive reporting capabilities.

![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1+-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

### Core Features
- **User Authentication**: Registration, login, logout with secure session management
- **Conference Management**: Create, view, and manage conferences with detailed information
- **Booking System**: Simple and intuitive booking process with real-time availability
- **Role-Based Access**: Different permissions for employees, managers, and administrators
- **Approval Workflow**: Manager approval for conference bookings with justification
- **Dashboard**: Personalized dashboard with statistics and quick actions

### Advanced Features
- **Department Management**: Organize users by departments with budget tracking
- **Email Notifications**: Automated email alerts for booking status changes
- **Reporting System**: Comprehensive reports with export functionality
- **Search & Filter**: Advanced search and filtering capabilities
- **Responsive Design**: Mobile-friendly Bootstrap-based interface
- **Admin Interface**: Full-featured Django admin for system management

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended) or SQLite (development)
- Bootstrap 5.1+

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/conference-booking-system.git
cd conference-booking-system
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv conference_env

# Activate virtual environment
# On Windows:
conference_env\Scripts\activate
# On macOS/Linux:
source conference_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@organization.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Organization Settings
ORGANIZATION_NAME=Your Organization Name
ORGANIZATION_EMAIL=admin@organization.com
```

### 5. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata sample_data.json
```

### 6. Collect Static Files (Production)

```bash
python manage.py collectstatic
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## 📁 Project Structure

```
conference-booking-system/
├── manage.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
├── conference_booking/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── bookings/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── migrations/
│   └── templates/
│       └── bookings/
├── accounts/
│   ├── __init__.py
│   ├── models.py
│   ├── admin.py
│   └── migrations/
├── templates/
│   ├── base.html
│   └── registration/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
    └── conferences/
```

## 🎯 Usage

### For Employees

1. **Register/Login**: Create an account or login with existing credentials
2. **Browse Conferences**: View available conferences with search and filter options
3. **Book Conference**: Submit booking requests with justification
4. **Track Bookings**: Monitor booking status and manage reservations
5. **Dashboard**: View personal statistics and upcoming conferences

### For Managers

1. **Review Bookings**: Approve or reject team member booking requests
2. **Manage Team**: View team bookings and budget utilization
3. **Department Reports**: Generate department-specific reports
4. **Budget Tracking**: Monitor conference expenses against budget

### For Administrators

1. **System Management**: Full access to all system features
2. **Conference Creation**: Add and manage conferences
3. **User Management**: Manage user accounts and roles
4. **Reports & Analytics**: Generate comprehensive system reports
5. **Data Export**: Export data for external analysis

## 🔧 Configuration

### Basic Settings

Key configuration options in `settings.py`:

```python
# Organization Settings
ORGANIZATION_NAME = "Your Organization"
ORGANIZATION_EMAIL = "admin@yourorg.com"

# Authentication
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Email Settings (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### Database Configuration

#### SQLite (Development)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### PostgreSQL (Production)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'conference_booking',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🚀 Deployment

### Using Docker

1. **Build Docker Image**:
```bash
docker build -t conference-booking-system .
```

2. **Run with Docker Compose**:
```bash
docker-compose up -d
```

### Manual Deployment

1. **Install Dependencies**:
```bash
pip install -r requirements.txt gunicorn
```

2. **Configure Environment**:
```bash
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@localhost/dbname
```

3. **Collect Static Files**:
```bash
python manage.py collectstatic --noinput
```

4. **Run with Gunicorn**:
```bash
gunicorn conference_booking.wsgi:application --bind 0.0.0.0:8000
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/your/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Database Models

### Core Models

- **Conference**: Stores conference information (title, date, venue, capacity, etc.)
- **Booking**: Manages booking requests and approvals
- **ConferenceCategory**: Categorizes conferences by type
- **User**: Extended Django user model with department and role information
- **Department**: Organizational structure with budget tracking

### Model Relationships

```
User ←→ Department (Many-to-One)
User ←→ Booking (One-to-Many)
Conference ←→ Booking (One-to-Many)
Conference ←→ ConferenceCategory (Many-to-One)
User ←→ Conference (One-to-Many, as creator)
```

## 🎨 Customization

### Branding

1. **Update Organization Details**:
   - Modify `ORGANIZATION_NAME` in settings
   - Update logo and colors in `base.html`
   - Customize email templates

2. **Styling**:
   - Edit CSS in `static/css/custom.css`
   - Modify Bootstrap variables
   - Update template layouts

### Features

1. **Add Custom Fields**:
   - Extend models with additional fields
   - Create and run migrations
   - Update forms and templates

2. **Workflow Customization**:
   - Modify approval process in views
   - Add custom validation rules
   - Implement custom notifications

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test bookings

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Sample Test Data

```bash
# Load test fixtures
python manage.py loaddata test_data.json

# Create sample conferences
python manage.py shell -c "
from bookings.management.commands.create_sample_data import Command
Command().handle()
"
```

## 📝 API Documentation

### Available Endpoints

- `GET /api/conference/<id>/availability/` - Check conference availability
- `POST /api/booking/create/` - Create booking (authenticated)
- `GET /api/reports/bookings/` - Get booking reports (admin only)

### Example API Usage

```python
import requests

# Check conference availability
response = requests.get('http://yourdomain.com/api/conference/1/availability/')
data = response.json()
print(f"Available seats: {data['available_seats']}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use descriptive commit messages

## 🐛 Troubleshooting

### Common Issues

1. **Migration Errors**:
```bash
python manage.py makemigrations --empty bookings
python manage.py migrate --fake-initial
```

2. **Static Files Not Loading**:
```bash
python manage.py collectstatic --clear
```

3. **Permission Denied**:
```bash
# Check user permissions in admin panel
# Ensure proper role assignments
```

4. **Email Not Sending**:
```bash
# Verify SMTP settin