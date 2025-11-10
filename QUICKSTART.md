# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Docker (Easiest)

```bash
# Start all services
docker-compose up --build

# Wait for services to start, then access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api
# API Docs: http://localhost:8000/api/docs
```

### Option 2: Manual Setup

#### 1. Backend (Terminal 1)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start backend server
python manage.py runserver
```

#### 2. Frontend (Terminal 2)
```bash
# Go to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start frontend server
npm run dev
```

#### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **API Docs**: http://localhost:8000/api/docs

## 📝 First Steps

1. **Register a new account** at http://localhost:3000/register
2. **Login** with your credentials
3. **Create a Project** to get started
4. **Add Epics** to your project
5. **Create User Stories** within epics
6. **Write Test Cases** for your stories
7. **Create Test Runs** to execute tests
8. **View Dashboard** for analytics

## 🔑 Default Admin Access

If you created a superuser, access Django admin:
- URL: http://localhost:8000/admin
- Use your superuser credentials

## 🛠️ Technology Overview

### Backend (Django REST API)
- JWT authentication
- RESTful API endpoints
- MySQL database
- API documentation with Swagger

### Frontend (Next.js)
- Modern React with TypeScript
- Tailwind CSS for styling
- Responsive design
- Real-time updates

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register
- `POST /api/auth/login/` - Login
- `GET /api/auth/me/` - Current user

### Resources
- `/api/projects/` - Projects
- `/api/epics/` - Epics
- `/api/stories/` - User Stories
- `/api/testcases/` - Test Cases
- `/api/test-runs/` - Test Runs
- `/api/test-suites/` - Test Suites

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check MySQL is running
docker ps

# Reset database
docker-compose down -v
docker-compose up --build
```

### Frontend errors
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### CORS issues
Ensure `.env` has:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 📖 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Explore [API documentation](http://localhost:8000/api/docs)
- Check frontend [README](frontend/README.md) for frontend details

## 💡 Tips

1. **Use the API docs** at `/api/docs` to explore endpoints
2. **Check browser console** for frontend errors
3. **Check terminal** for backend errors
4. **JWT tokens** are stored in localStorage
5. **Tokens auto-refresh** on expiration

## 🎯 What's Next?

After setup, you can:
- Customize the UI in `frontend/src/`
- Add new API endpoints in `test_cases/api_views.py`
- Extend models in `test_cases/models.py`
- Add new pages in `frontend/src/app/`

Happy testing! 🧪
