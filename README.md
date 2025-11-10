# Test Case Management System

A modern full-stack test case management system with Django REST API backend and Next.js frontend.

## Architecture

This project has been transformed into a modern architecture with separate frontend and backend:

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────┐
│   Next.js       │ API  │   Django REST    │      │    MySQL     │
│   Frontend      │─────▶│   Framework      │─────▶│   Database   │
│  (Port 3000)    │      │   (Port 8000)    │      │  (Port 3306) │
└─────────────────┘      └──────────────────┘      └──────────────┘
```

### Backend (Django REST API)
- **Framework**: Django 5.2.0 + Django REST Framework
- **Authentication**: JWT (JSON Web Tokens) using Simple JWT
- **Database**: MySQL 8.0
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **CORS**: Configured for Next.js frontend

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Forms**: React Hook Form
- **Notifications**: React Hot Toast

## Features

### Core Functionality
- ✅ **User Authentication** - JWT-based login and registration
- ✅ **Project Management** - CRUD operations for projects
- ✅ **Epic Management** - Organize work into epics
- ✅ **User Stories** - Define requirements and acceptance criteria
- ✅ **Test Cases** - Create, manage, and execute test cases
- ✅ **Test Suites** - Group related test cases
- ✅ **Test Runs** - Execute test suites and track results
- ✅ **Dashboard** - Real-time statistics and analytics
- ✅ **Reporting** - Test execution reports and metrics

### Technical Features
- 🔐 JWT Authentication with automatic token refresh
- 🔍 Search and filtering on all entities
- 📄 Pagination for large datasets
- 🎨 Responsive UI with Tailwind CSS
- 📊 Interactive dashboards and charts
- 🔄 Real-time data synchronization
- 📝 Form validation
- 🚀 Docker support for easy deployment

## Quick Start

### Prerequisites
- Docker and Docker Compose (recommended)
- OR
  - Python 3.10+
  - Node.js 20+
  - MySQL 8.0

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd DjangoTestCaseManagement
   ```

2. Start all services:
   ```bash
   docker-compose up --build
   ```

3. The application will be available at:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000/api
   - **API Documentation**: http://localhost:8000/api/docs

4. Create a superuser (optional):
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

### Manual Setup

#### Backend Setup

1. Create virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure environment variables (create `.env` file):
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=testcase_management
   DB_USER=root
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=3306
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic
   ```

4. Start development server:
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment (create `.env.local`):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. Start development server:
   ```bash
   npm run dev
   ```

5. Open http://localhost:3000

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user

### Resource Endpoints
All resources support standard CRUD operations:

- **Projects**: `/api/projects/`
- **Epics**: `/api/epics/`
- **User Stories**: `/api/stories/`
- **Test Cases**: `/api/testcases/`
- **Test Suites**: `/api/test-suites/`
- **Test Runs**: `/api/test-runs/`
- **Test Executions**: `/api/test-executions/`

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Project Structure

```
DjangoTestCaseManagement/
├── backend/                    # Django backend
│   ├── test_cases/            # Main Django app
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── api_views.py       # API viewsets
│   │   ├── api_urls.py        # API URL routing
│   │   └── views.py           # Original Django views (legacy)
│   ├── testcase_management/   # Django project settings
│   │   ├── settings.py        # Project configuration
│   │   └── urls.py            # Main URL routing
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js pages (App Router)
│   │   │   ├── dashboard/     # Dashboard page
│   │   │   ├── login/         # Login page
│   │   │   ├── register/      # Registration page
│   │   │   └── layout.tsx     # Root layout
│   │   ├── components/        # React components
│   │   │   └── layout/        # Layout components
│   │   ├── lib/               # Utilities
│   │   │   └── api.ts         # API client
│   │   ├── store/             # State management
│   │   │   └── auth.ts        # Auth store
│   │   └── types/             # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docker-compose.yml          # Docker orchestration
└── README.md                   # This file
```

## Development

### Backend Development

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   python manage.py test
   ```

3. Create new migrations:
   ```bash
   python manage.py makemigrations
   ```

4. Access Django admin:
   - URL: http://localhost:8000/admin
   - Create superuser: `python manage.py createsuperuser`

### Frontend Development

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run development server with hot reload:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   npm start
   ```

4. Lint code:
   ```bash
   npm run lint
   ```

## Environment Variables

### Backend (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=testcase_management
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Deployment

### Docker Production Build

1. Update environment variables in `docker-compose.yml`
2. Build and start:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

### Manual Production Deployment

#### Backend
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn testcase_management.wsgi:application --bind 0.0.0.0:8000
```

#### Frontend
```bash
cd frontend
npm install
npm run build
npm start
```

## Troubleshooting

### Common Issues

1. **CORS errors**: Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
2. **Database connection**: Check MySQL is running and credentials are correct
3. **JWT token expired**: Frontend will auto-refresh tokens
4. **Port already in use**: Change ports in docker-compose.yml or .env files

### Reset Database
```bash
docker-compose down -v
docker-compose up --build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue in the repository
- Check API documentation at http://localhost:8000/api/docs

## Technology Stack Summary

**Backend:**
- Django 5.2.0
- Django REST Framework 3.15.2
- Simple JWT 5.4.0
- MySQL 8.0
- CORS Headers
- drf-spectacular

**Frontend:**
- Next.js 14
- React 18
- TypeScript 5
- Tailwind CSS 3
- Zustand (state management)
- Axios (HTTP client)
- React Hook Form
- Chart.js
- React Hot Toast

**DevOps:**
- Docker & Docker Compose
- Gunicorn
- WhiteNoise (static files)
