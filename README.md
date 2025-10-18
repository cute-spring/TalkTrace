# Talk Trace - Test Sample Management Platform

A simplified enterprise internal tool for filtering representative data from BigQuery conversation data and processing it according to standardized test case formats.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Google Cloud project and BigQuery access permissions

### One-Click Setup
```bash
# Clone the project
git clone <your-repo-url>
cd talk-trace

# Run the setup script
./scripts/setup.sh
```

### Manual Setup
```bash
# 1. Copy environment variables file
cp .env.example .env

# 2. Edit the .env file to configure GCP_PROJECT_ID and other necessary parameters

# 3. Start the development environment
docker-compose -f docker-compose.dev.yml up -d

# 4. View logs
docker-compose -f docker-compose.dev.yml logs -f
```

## 📱 Access URLs

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Info**: http://localhost:8001/api
- **Health Check**: http://localhost:8001/health

## 🏗️ Technology Stack

- **Frontend**: React 18 + TypeScript + Ant Design + Vite
- **Backend**: Python FastAPI + SQLAlchemy + PostgreSQL
- **Data Source**: Google BigQuery
- **Deployment**: Docker + Docker Compose

## 📋 Key Features

1. **History Query** - Query and filter conversation data from BigQuery
2. **Data Import** - Convert selected conversations to test cases
3. **Test Case Management** - Edit, delete, and batch manage test cases
4. **Simple Statistics** - Basic data statistics and analysis

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database Configuration
DATABASE_URL="postgresql://user:password@localhost:5432/testdb"
POSTGRES_DB=testdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_URL="redis://localhost:6379"

# Google Cloud Configuration
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-credentials.json

# Application Configuration
ENVIRONMENT=development
PORT=8001
```

### Google Cloud Credentials
1. Download the service account key file
2. Place the file in `backend/credentials/google-credentials.json`
3. Ensure the account has BigQuery access permissions

## 📁 Project Structure

```
talk-trace/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── package.json
├── backend-python/           # Python backend application
│   ├── app/
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   ├── middleware/     # Middleware
│   │   └── utils/          # Utilities
│   └── requirements.txt
├── database/                 # Database scripts
├── scripts/                  # Deployment scripts
├── docker-compose.dev.yml    # Development environment
└── README.md
```

## 🛠️ Common Commands

```bash
# View service status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Restart services
docker-compose -f docker-compose.dev.yml restart

# Rebuild
docker-compose -f docker-compose.dev.yml build --no-cache
```

## 📚 API Endpoints

### History
- `GET /api/v1/history/search` - Search historical records
- `GET /api/v1/history/models` - Get model list

### Import Functionality
- `POST /api/v1/import/preview` - Preview import data
- `POST /api/v1/import/execute` - Execute import
- `GET /api/v1/import/progress/:taskId` - Query import progress

### Test Cases
- `GET /api/v1/test-cases` - Get test case list
- `POST /api/v1/test-cases` - Create test case
- `PUT /api/v1/test-cases/:id` - Update test case
- `DELETE /api/v1/test-cases/:id` - Delete test case

## 🐛 Troubleshooting

### BigQuery Connection Failed
1. Check if GCP_PROJECT_ID is correct
2. Confirm credentials file path is correct
3. Verify service account permissions

### Database Connection Failed
1. Check if PostgreSQL container is running properly
2. Verify database connection string
3. Confirm database is initialized

### Frontend Cannot Access Backend
1. Check if backend service is running properly
2. Confirm port mapping is correct
3. Check network connection configuration

## 📄 License

MIT License