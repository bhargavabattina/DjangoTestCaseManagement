# Test Case Management - Next.js Frontend

This is the Next.js frontend for the Test Case Management System.

## Features

- **Authentication**: JWT-based authentication with login/register
- **Dashboard**: Overview of projects, test cases, and execution stats
- **Projects Management**: CRUD operations for projects
- **Epics Management**: CRUD operations for epics
- **User Stories Management**: CRUD operations for user stories
- **Test Cases**: Create, edit, and manage test cases
- **Test Runs**: Execute test runs and track results
- **Test Suites**: Group test cases into suites
- **Responsive UI**: Built with Tailwind CSS

## Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API requests
- **Zustand**: State management
- **React Hook Form**: Form validation
- **Chart.js**: Data visualization
- **React Hot Toast**: Toast notifications

## Getting Started

### Prerequisites

- Node.js 20+ and npm

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env.local` file:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Docker

Run with Docker Compose (from project root):
```bash
docker-compose up frontend
```

## Project Structure

```
frontend/
├── src/
│   ├── app/           # Next.js App Router pages
│   ├── components/    # Reusable React components
│   ├── lib/           # API client and utilities
│   ├── store/         # Zustand state management
│   └── types/         # TypeScript type definitions
├── public/            # Static assets
└── package.json
```

## API Integration

The frontend communicates with the Django REST API backend:

- Base URL: `http://localhost:8000/api`
- Authentication: JWT tokens (Bearer)
- Endpoints: Projects, Epics, Stories, Test Cases, Test Runs, etc.

## Building for Production

```bash
npm run build
npm start
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL

## License

This project is part of the Test Case Management System.
