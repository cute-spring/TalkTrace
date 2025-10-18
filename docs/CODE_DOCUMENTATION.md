# Talk Trace Code Documentation

## Overview

This document provides detailed code documentation for the Talk Trace project, including architecture patterns, module descriptions, and code conventions.

## Architecture Overview

The Talk Trace application follows a modern web application architecture with clear separation between frontend and backend components.

```
┌─────────────────┐    HTTP API    ┌──────────────────┐
│   Frontend      │ ◄─────────────► │    Backend       │
│   (React + TS)  │                │  (FastAPI + Py)  │
└─────────────────┘                └──────────────────┘
                                           │
                                           ▼
                                ┌──────────────────┐
                                │   PostgreSQL     │
                                │     Database     │
                                └──────────────────┘
                                           ▲
                                           │
                                ┌──────────────────┐
                                │   BigQuery       │
                                │   Data Source    │
                                └──────────────────┘
```

## Frontend Architecture

### Technology Stack
- **React 18**: UI framework with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript for better development experience
- **Ant Design**: UI component library with consistent design system
- **Vite**: Fast build tool and development server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication

### Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Layout/        # Layout components
│   │   │   ├── AppLayout.tsx
│   │   │   └── index.ts
│   │   └── Common/        # Common components
│   ├── pages/             # Page components
│   │   ├── HistoryPage.tsx
│   │   ├── ImportPage.tsx
│   │   └── TestCasePage.tsx
│   ├── services/          # API service layer
│   │   └── api.ts
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── hooks/             # Custom React hooks
│   ├── App.tsx           # Main application component
│   └── main.tsx          # Application entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.example
```

### Key Components

#### AppLayout.tsx
Main layout component providing navigation and structure for the application.

```typescript
interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  // Layout implementation with sidebar, header, and content area
};
```

#### API Service Layer
Centralized API communication with proper error handling and type safety.

```typescript
// services/api.ts
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

export class ApiService {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    // Implementation with error handling
  }

  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    // Implementation with error handling
  }
}
```

### Type Definitions

```typescript
// types/index.ts
export interface TestCase {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  tags: string[];
  input: {
    role: string;
    content: string;
    context?: string;
  };
  expectedOutput: {
    role: string;
    content: string;
    requirements: string[];
  };
  metadata: {
    sourceConversationId?: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    version: number;
    testCount: number;
    successRate: number;
  };
}

export interface HistoryRecord {
  id: string;
  model: string;
  timestamp: string;
  messages: Array<{
    role: string;
    content: string;
    timestamp: string;
  }>;
  metadata: {
    tokenCount: number;
    language: string;
  };
}
```

### State Management

The application uses React's built-in state management with hooks:

```typescript
// Custom hook for test case management
export const useTestCases = () => {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTestCases = async (filters?: TestCaseFilters) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get<TestCase[]>('/test-cases', { params: filters });
      if (response.success && response.data) {
        setTestCases(response.data);
      }
    } catch (err) {
      setError('Failed to fetch test cases');
    } finally {
      setLoading(false);
    }
  };

  return {
    testCases,
    loading,
    error,
    fetchTestCases
  };
};
```

## Backend Architecture

### Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.9+**: Programming language
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **PostgreSQL**: Primary database
- **BigQuery**: Data source for conversation history
- **Docker**: Containerization

### Project Structure

```
backend-python/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration management
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   ├── test_case.py
│   │   ├── history.py
│   │   ├── import_models.py
│   │   └── common.py
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   ├── test_case_service.py
│   │   ├── history_service.py
│   │   └── import_service.py
│   ├── middleware/         # Custom middleware
│   │   ├── __init__.py
│   │   └── logging.py
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   └── logger.py
│   └── routers/            # API route definitions
│       ├── __init__.py
│       ├── test_cases.py
│       ├── history.py
│       └── import.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )

    # Server Configuration
    port: int = 8001
    host: str = "0.0.0.0"
    environment: str = "development"

    # Database Configuration
    database_url: str
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Google Cloud Configuration
    gcp_project_id: str
    google_application_credentials: str

    # CORS Configuration
    allowed_origins: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

settings = Settings()
```

### Data Models

#### Test Case Model

```python
# app/models/test_case.py
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False, index=True)
    priority = Column(String, nullable=False, index=True)  # high, medium, low
    tags = Column(JSON)  # List of strings
    input_data = Column(JSON, nullable=False)  # Role, content, context
    expected_output = Column(JSON, nullable=False)  # Role, content, requirements
    source_conversation_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, nullable=False)
    version = Column(Integer, default=1)
    test_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
```

#### History Record Model

```python
# app/models/history.py
class HistoryRecord(Base):
    __tablename__ = "history_records"

    id = Column(String, primary_key=True)
    model = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    messages = Column(JSON, nullable=False)  # List of message objects
    metadata = Column(JSON)  # Token count, language, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Service Layer

#### Test Case Service

```python
# app/services/test_case_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.test_case import TestCase
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate
import uuid

class TestCaseService:
    def __init__(self, db: Session):
        self.db = db

    def create_test_case(self, test_case_data: TestCaseCreate) -> TestCase:
        """Create a new test case"""
        db_test_case = TestCase(
            id=str(uuid.uuid4()),
            **test_case_data.dict()
        )
        self.db.add(db_test_case)
        self.db.commit()
        self.db.refresh(db_test_case)
        return db_test_case

    def get_test_cases(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[TestCase]:
        """Get test cases with filtering and pagination"""
        query = self.db.query(TestCase)

        if category:
            query = query.filter(TestCase.category == category)
        if priority:
            query = query.filter(TestCase.priority == priority)
        if search:
            query = query.filter(
                TestCase.title.contains(search) |
                TestCase.description.contains(search)
            )

        return query.offset(skip).limit(limit).all()

    def get_test_case_by_id(self, test_case_id: str) -> Optional[TestCase]:
        """Get a specific test case by ID"""
        return self.db.query(TestCase).filter(TestCase.id == test_case_id).first()

    def update_test_case(
        self,
        test_case_id: str,
        test_case_data: TestCaseUpdate
    ) -> Optional[TestCase]:
        """Update an existing test case"""
        db_test_case = self.get_test_case_by_id(test_case_id)
        if db_test_case:
            update_data = test_case_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_test_case, field, value)

            db_test_case.version += 1
            db_test_case.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(db_test_case)
        return db_test_case

    def delete_test_case(self, test_case_id: str) -> bool:
        """Delete a test case"""
        db_test_case = self.get_test_case_by_id(test_case_id)
        if db_test_case:
            self.db.delete(db_test_case)
            self.db.commit()
            return True
        return False
```

### API Routes

```python
# app/routers/test_cases.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.test_case_service import TestCaseService
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate, TestCaseResponse

router = APIRouter(prefix="/api/v1/test-cases", tags=["test-cases"])

@router.get("/", response_model=List[TestCaseResponse])
async def get_test_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get test cases with filtering and pagination"""
    service = TestCaseService(db)
    test_cases = service.get_test_cases(
        skip=skip,
        limit=limit,
        category=category,
        priority=priority,
        search=search
    )
    return test_cases

@router.post("/", response_model=TestCaseResponse)
async def create_test_case(
    test_case_data: TestCaseCreate,
    db: Session = Depends(get_db)
):
    """Create a new test case"""
    service = TestCaseService(db)
    test_case = service.create_test_case(test_case_data)
    return test_case

@router.get("/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(
    test_case_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific test case by ID"""
    service = TestCaseService(db)
    test_case = service.get_test_case_by_id(test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case
```

### Pydantic Schemas

```python
# app/schemas/test_case.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class MessageSchema(BaseModel):
    role: str
    content: str
    context: Optional[str] = None

class ExpectedOutputSchema(BaseModel):
    role: str
    content: str
    requirements: List[str]

class TestCaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=1, max_length=50)
    priority: str = Field(..., regex="^(high|medium|low)$")
    tags: List[str] = Field(default_factory=list)
    input_data: MessageSchema
    expected_output: ExpectedOutputSchema
    created_by: str = Field(..., min_length=1)

class TestCaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    priority: Optional[str] = Field(None, regex="^(high|medium|low)$")
    tags: Optional[List[str]] = None
    input_data: Optional[MessageSchema] = None
    expected_output: Optional[ExpectedOutputSchema] = None

class TestCaseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    category: str
    priority: str
    tags: List[str]
    input_data: MessageSchema
    expected_output: ExpectedOutputSchema
    source_conversation_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    version: int
    test_count: int
    success_rate: float

    class Config:
        from_attributes = True
```

### Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import test_cases, history, import
from app.middleware.logging import LoggingMiddleware

app = FastAPI(
    title="Talk Trace API",
    description="Test Sample Management Platform API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(test_cases.router)
app.include_router(history.router)
app.include_router(import.router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api")
async def api_info():
    return {
        "name": "Talk Trace API",
        "version": "1.0.0",
        "description": "Test Sample Management Platform API",
        "endpoints": [
            "/api/v1/test-cases",
            "/api/v1/history",
            "/api/v1/import"
        ]
    }
```

## Database Schema

### Tables

1. **test_cases**: Stores test case data with metadata
2. **history_records**: Caches BigQuery conversation history
3. **import_tasks**: Tracks import operation progress
4. **users**: User management (future feature)

### Relationships

- `test_cases` can be linked to `history_records` via `source_conversation_id`
- `import_tasks` track progress of bulk operations

## Error Handling

### Frontend Error Handling

```typescript
// Error boundary component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Result
          status="error"
          title="Something went wrong"
          subTitle="An unexpected error occurred. Please try refreshing the page."
          extra={<Button type="primary" onClick={() => window.location.reload()}>
            Refresh Page
          </Button>}
        />
      );
    }

    return this.props.children;
  }
}
```

### Backend Error Handling

```python
# Custom exception handler
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred"
            }
        }
    )
```

## Testing

### Frontend Testing

```typescript
// Component test example
import { render, screen, fireEvent } from '@testing-library/react';
import { TestCasePage } from './TestCasePage';

describe('TestCasePage', () => {
  test('renders test case list', () => {
    render(<TestCasePage />);
    expect(screen.getByText('Test Cases')).toBeInTheDocument();
  });

  test('handles test case creation', async () => {
    render(<TestCasePage />);

    const createButton = screen.getByText('Create Test Case');
    fireEvent.click(createButton);

    // Test form submission
    expect(screen.getByText('Create')).toBeInTheDocument();
  });
});
```

### Backend Testing

```python
# Service test example
import pytest
from app.services.test_case_service import TestCaseService
from app.schemas.test_case import TestCaseCreate

def test_create_test_case(db_session):
    service = TestCaseService(db_session)

    test_case_data = TestCaseCreate(
        title="Test Case 1",
        description="Test description",
        category="test",
        priority="high",
        input_data={"role": "user", "content": "Hello"},
        expected_output={"role": "assistant", "content": "Hi there!", "requirements": []},
        created_by="test_user"
    )

    test_case = service.create_test_case(test_case_data)

    assert test_case.title == "Test Case 1"
    assert test_case.category == "test"
    assert test_case.priority == "high"
```

## Code Standards

### Python Standards
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style
- Maintain test coverage above 80%

### TypeScript Standards
- Use strict TypeScript configuration
- Prefer interfaces over types for object shapes
- Use functional components with hooks
- Follow React best practices and naming conventions

### Git Standards
- Use conventional commit messages
- Create feature branches from main
- Ensure all tests pass before merging
- Keep commits small and focused

## Development Workflow

1. **Setup**: Clone repository and install dependencies
2. **Development**: Run development servers for frontend and backend
3. **Testing**: Run unit tests and integration tests
4. **Code Review**: Submit pull requests for review
5. **Deployment**: Use Docker for consistent deployments

This documentation provides a comprehensive overview of the codebase architecture and implementation patterns used in the Talk Trace project.