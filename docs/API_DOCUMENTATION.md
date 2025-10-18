# Talk Trace API Documentation

## Overview

This document provides comprehensive documentation for the Talk Trace REST API. The API allows you to manage test cases, query conversation history, and handle data imports from BigQuery.

**Base URL**: `http://localhost:8001`

**API Version**: v1

**Content-Type**: `application/json`

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Health Check

### GET /health

Check if the API service is running properly.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

## History Management

### GET /api/v1/history/search

Search and filter conversation history from BigQuery.

**Query Parameters**:
- `query` (string, optional): Search query string
- `model` (string, optional): Filter by model name
- `start_date` (string, optional): Start date in ISO format (YYYY-MM-DD)
- `end_date` (string, optional): End date in ISO format (YYYY-MM-DD)
- `limit` (integer, optional): Maximum number of results (default: 50)
- `offset` (integer, optional): Number of results to skip (default: 0)

**Example Request**:
```
GET /api/v1/history/search?query=chatgpt&model=gpt-4&start_date=2024-01-01&limit=20
```

**Response**:
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "conv_123456",
        "model": "gpt-4",
        "timestamp": "2024-01-01T10:00:00Z",
        "messages": [
          {
            "role": "user",
            "content": "Hello, how are you?",
            "timestamp": "2024-01-01T10:00:00Z"
          },
          {
            "role": "assistant",
            "content": "I'm doing well, thank you!",
            "timestamp": "2024-01-01T10:00:05Z"
          }
        ],
        "metadata": {
          "token_count": 150,
          "language": "en"
        }
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  }
}
```

### GET /api/v1/history/models

Get a list of available models from BigQuery history.

**Response**:
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "name": "gpt-4",
        "count": 1250,
        "last_used": "2024-01-15T14:30:00Z"
      },
      {
        "name": "gpt-3.5-turbo",
        "count": 3420,
        "last_used": "2024-01-15T16:45:00Z"
      }
    ]
  }
}
```

## Import Management

### POST /api/v1/import/preview

Preview data before importing conversations as test cases.

**Request Body**:
```json
{
  "conversation_ids": ["conv_123456", "conv_789012"],
  "format_options": {
    "include_metadata": true,
    "custom_fields": ["category", "priority"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "preview": [
      {
        "conversation_id": "conv_123456",
        "title": "Customer Service Conversation",
        "estimated_tokens": 250,
        "test_case_format": {
          "input": "Customer greeting",
          "expected_output": "Professional response",
          "context": "Customer service scenario"
        }
      }
    ],
    "total_conversations": 2,
    "estimated_import_time": "2-3 minutes"
  }
}
```

### POST /api/v1/import/execute

Execute the import of selected conversations as test cases.

**Request Body**:
```json
{
  "conversation_ids": ["conv_123456", "conv_789012"],
  "import_options": {
    "category": "customer_service",
    "priority": "high",
    "tags": ["greeting", "professional"],
    "auto_format": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "task_id": "import_task_456789",
    "status": "started",
    "estimated_duration": "2-3 minutes",
    "conversations_count": 2
  }
}
```

### GET /api/v1/import/progress/:taskId

Check the progress of an import task.

**Path Parameters**:
- `taskId` (string): The import task ID

**Response**:
```json
{
  "success": true,
  "data": {
    "task_id": "import_task_456789",
    "status": "processing",
    "progress": {
      "current": 1,
      "total": 2,
      "percentage": 50
    },
    "started_at": "2024-01-15T10:00:00Z",
    "estimated_completion": "2024-01-15T10:02:30Z",
    "results": {
      "successful": 1,
      "failed": 0,
      "pending": 1
    }
  }
}
```

## Test Case Management

### GET /api/v1/test-cases

Get a list of test cases with filtering and pagination.

**Query Parameters**:
- `category` (string, optional): Filter by category
- `priority` (string, optional): Filter by priority (high, medium, low)
- `tags` (string, optional): Comma-separated list of tags
- `search` (string, optional): Search in title and description
- `limit` (integer, optional): Maximum number of results (default: 20)
- `offset` (integer, optional): Number of results to skip (default: 0)

**Example Request**:
```
GET /api/v1/test-cases?category=customer_service&priority=high&limit=10
```

**Response**:
```json
{
  "success": true,
  "data": {
    "test_cases": [
      {
        "id": "tc_123456",
        "title": "Customer Greeting Response",
        "description": "Test proper greeting response in customer service scenarios",
        "category": "customer_service",
        "priority": "high",
        "tags": ["greeting", "professional", "response"],
        "input": {
          "role": "user",
          "content": "Hello, I need help with my order",
          "context": "Customer contacting support"
        },
        "expected_output": {
          "role": "assistant",
          "content": "Hello! I'd be happy to help you with your order. Could you please provide your order number?",
          "requirements": ["Polite tone", "Request order information", "Offer assistance"]
        },
        "metadata": {
          "source_conversation_id": "conv_123456",
          "created_at": "2024-01-15T10:00:00Z",
          "updated_at": "2024-01-15T10:30:00Z",
          "created_by": "user_123",
          "version": 1,
          "test_count": 5,
          "success_rate": 0.95
        }
      }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0,
    "categories": ["customer_service", "technical_support", "sales"],
    "priorities": ["high", "medium", "low"]
  }
}
```

### POST /api/v1/test-cases

Create a new test case.

**Request Body**:
```json
{
  "title": "Technical Support Diagnosis",
  "description": "Test troubleshooting steps for common technical issues",
  "category": "technical_support",
  "priority": "medium",
  "tags": ["troubleshooting", "diagnosis", "technical"],
  "input": {
    "role": "user",
    "content": "My application is running slowly",
    "context": "User reporting performance issues"
  },
  "expected_output": {
    "role": "assistant",
    "content": "I understand you're experiencing slow performance. Let me help you diagnose this issue. Can you tell me more about when this started and what specific actions are slow?",
    "requirements": ["Empathetic response", "Ask clarifying questions", "Systematic approach"]
  },
  "metadata": {
    "version": 1,
    "test_count": 0,
    "success_rate": 0.0
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "tc_789012",
    "title": "Technical Support Diagnosis",
    "description": "Test troubleshooting steps for common technical issues",
    "category": "technical_support",
    "priority": "medium",
    "tags": ["troubleshooting", "diagnosis", "technical"],
    "input": {
      "role": "user",
      "content": "My application is running slowly",
      "context": "User reporting performance issues"
    },
    "expected_output": {
      "role": "assistant",
      "content": "I understand you're experiencing slow performance. Let me help you diagnose this issue. Can you tell me more about when this started and what specific actions are slow?",
      "requirements": ["Empathetic response", "Ask clarifying questions", "Systematic approach"]
    },
    "metadata": {
      "source_conversation_id": null,
      "created_at": "2024-01-15T11:00:00Z",
      "updated_at": "2024-01-15T11:00:00Z",
      "created_by": "user_456",
      "version": 1,
      "test_count": 0,
      "success_rate": 0.0
    }
  }
}
```

### GET /api/v1/test-cases/:id

Get a specific test case by ID.

**Path Parameters**:
- `id` (string): Test case ID

**Response**: Same format as individual test case in the list response

### PUT /api/v1/test-cases/:id

Update an existing test case.

**Path Parameters**:
- `id` (string): Test case ID

**Request Body**: Same format as create test case request

**Response**: Updated test case object

### DELETE /api/v1/test-cases/:id

Delete a test case.

**Path Parameters**:
- `id` (string): Test case ID

**Response**:
```json
{
  "success": true,
  "message": "Test case deleted successfully"
}
```

### POST /api/v1/test-cases/batch

Perform batch operations on test cases.

**Request Body**:
```json
{
  "action": "delete",
  "test_case_ids": ["tc_123456", "tc_789012"],
  "options": {
    "confirm": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "processed": 2,
    "successful": 2,
    "failed": 0,
    "results": [
      {
        "id": "tc_123456",
        "status": "deleted"
      },
      {
        "id": "tc_789012",
        "status": "deleted"
      }
    ]
  }
}
```

## Statistics

### GET /api/v1/stats/overview

Get overview statistics about test cases and imports.

**Response**:
```json
{
  "success": true,
  "data": {
    "test_cases": {
      "total": 150,
      "by_category": {
        "customer_service": 75,
        "technical_support": 45,
        "sales": 30
      },
      "by_priority": {
        "high": 45,
        "medium": 75,
        "low": 30
      },
      "recent_activity": 25
    },
    "imports": {
      "total": 12,
      "successful": 11,
      "failed": 1,
      "total_conversations": 150
    },
    "performance": {
      "average_success_rate": 0.87,
      "total_test_runs": 1250,
      "last_updated": "2024-01-15T12:00:00Z"
    }
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `NOT_FOUND` | Resource not found |
| `PERMISSION_DENIED` | Access denied |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Internal server error |
| `BIGQUERY_ERROR` | BigQuery operation failed |
| `IMPORT_ERROR` | Import operation failed |
| `DATABASE_ERROR` | Database operation failed |

## Rate Limiting

API requests are limited to 100 requests per minute per IP address. Rate limit headers are included in all responses:

- `X-RateLimit-Limit`: Maximum requests per minute
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit resets (Unix timestamp)

## SDK and Client Libraries

Currently, no official SDKs are available. The API can be accessed using any HTTP client library.

## Support

For API support and questions, please contact the development team or create an issue in the project repository.