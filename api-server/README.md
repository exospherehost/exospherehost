# ExosphereHost API Server

The ExosphereHost API Server is a FastAPI-based REST API that serves as the public interface for the ExosphereHost platform. It provides endpoints for managing projects, users, authentication, and orchestrating AI workflows through the satellite and cluster APIs.

## 🏗️ Architecture

The API server is built with a modular architecture consisting of:

- **🔐 Authentication & Authorization**: JWT-based authentication with role-based access control
- **👥 User Management**: User registration, profile management, and verification
- **📁 Project Management**: Multi-tenant project organization with billing integration
- **🛰️ Satellite API**: Direct satellite execution and status monitoring
- **🌌 Cluster API**: Workflow orchestration and management
- **📊 Middleware**: Request logging, error handling, and rate limiting

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MongoDB (for data persistence)
- UV package manager (recommended)

### Installation

1. **Navigate to the API server directory:**
   ```bash
   cd api-server
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

   Configure the following environment variables in `.env`:
   ```bash
   MONGO_URI=mongodb://localhost:27017
   MONGO_DATABASE_NAME=exosphere-api-server
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=development
   LOG_LEVEL=info
   ```

4. **Run the development server:**
   ```bash
   uv run python run.py
   ```

The API server will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f api-server
   ```

## 📚 API Documentation

### Interactive API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/token` - Token refresh
- `GET /auth/me` - Get current user info

#### User Management
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update user profile
- `DELETE /users/profile` - Delete user account

#### Project Management
- `GET /projects/` - List user projects
- `POST /projects/` - Create new project
- `GET /projects/{project_id}` - Get project details
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project

#### Satellite API
- `POST /satellites/{project_name}/{satellite_name}` - Execute satellite
- `GET /satellites/{project_name}/{satellite_name}/{execution_id}` - Get execution status

#### Cluster API
- `POST /clusters/` - Create cluster from YAML
- `GET /clusters/{cluster_id}` - Get cluster status
- `POST /clusters/{cluster_id}/trigger` - Trigger cluster execution
- `DELETE /clusters/{cluster_id}` - Delete cluster

## 🏛️ Data Models

### User Model
```json
{
  "_id": "ObjectId",
  "name": "string",
  "type": "human|api",
  "identifier": "email|phone|api_key",
  "verification_status": "verified|not_verified|blocked|deleted|not_required",
  "credential": "hashed_password|api_key",
  "status": "active|inactive|deleted|blocked",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Project Model
```json
{
  "_id": "ObjectId",
  "name": "string",
  "status": "active|inactive|blocked|deleted",
  "billing_account": {
    "company_name": "string",
    "company_address": "string",
    "tax_number_type": "vat|gst|ein",
    "tax_number": "string",
    "country": "string"
  },
  "users": [
    {
      "role": "admin|user|viewer",
      "user": "ObjectId"
    }
  ],
  "super_admin": "ObjectId",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 🛠️ Development

### Project Structure

```
api-server/
├── 📁 app/                    # Main application code
│   ├── 📄 main.py            # FastAPI application setup
│   ├── 📁 auth/              # Authentication module
│   ├── 📁 user/              # User management module
│   ├── 📁 project/           # Project management module
│   ├── 📁 middlewares/       # Custom middleware
│   └── 📁 singletons/        # Singleton services
├── 📄 run.py                 # Application entry point
├── 📄 pyproject.toml         # Python dependencies
├── 📄 Dockerfile             # Container configuration
└── 📄 docker-compose.yml     # Multi-service setup
```

### Adding New Endpoints

1. **Create a new module** in the `app/` directory
2. **Define models** using Beanie (MongoDB ODM)
3. **Create routes** using FastAPI router
4. **Add middleware** if needed
5. **Include router** in `main.py`

Example:
```python
from fastapi import APIRouter, Depends
from .models import YourModel

router = APIRouter(prefix="/your-endpoint", tags=["Your Module"])

@router.get("/")
async def list_items():
    return await YourModel.find_all().to_list()

@router.post("/")
async def create_item(item: YourModel):
    return await item.create()
```

### Testing

Run tests using pytest:
```bash
uv run pytest
```

### Code Quality

Format code with black:
```bash
uv run black .
```

Lint with flake8:
```bash
uv run flake8 .
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGO_DATABASE_NAME` | Database name | `exosphere-api-server` |
| `JWT_SECRET_KEY` | JWT signing key | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `30` |
| `ENVIRONMENT` | Environment mode | `development` |
| `LOG_LEVEL` | Logging level | `info` |

### Logging

The API server uses structured logging with the following levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about application flow
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

Logs are formatted as JSON in production for better parsing.

## 🚀 Deployment

### Production Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t exosphere-api-server .
   ```

2. **Run with production settings:**
   ```bash
   docker run -d \
     --name exosphere-api-server \
     -p 8000:8000 \
     -e ENVIRONMENT=production \
     -e MONGO_URI=your-production-mongo-uri \
     exosphere-api-server
   ```

### Kubernetes Deployment

Use the Kubernetes manifests in the `/k8s` directory:
```bash
kubectl apply -f ../k8s/api-server/
```

### Health Checks

The API server provides health check endpoints:
- `GET /health` - Basic health check
- `GET /health/db` - Database connectivity check

## 🔒 Security

### Authentication

The API uses JWT tokens for authentication:
1. Users authenticate with `/auth/login`
2. Receive JWT access token
3. Include token in `Authorization: Bearer <token>` header

### Authorization

Role-based access control (RBAC) with the following roles:
- **Super Admin**: Full project control
- **Admin**: Project management and user invitation
- **User**: Resource creation and management
- **Viewer**: Read-only access

### Rate Limiting

API endpoints are rate-limited to prevent abuse:
- **Authentication**: 5 requests per minute
- **General API**: 100 requests per minute
- **Satellite execution**: 10 requests per minute

## 📊 Monitoring

### Metrics

The API server exposes metrics for monitoring:
- Request count and latency
- Database connection pool status
- Authentication success/failure rates
- Resource usage statistics

### Logging

All requests are logged with:
- Request ID for tracing
- User ID (if authenticated)
- Endpoint and method
- Response status and time
- Error details (if any)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/api-enhancement`
3. **Make your changes** following the coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### Code Standards

- Follow PEP 8 for Python code style
- Use type hints for all function parameters and return types
- Write docstrings for all public functions and classes
- Maintain test coverage above 80%

## 📄 License

This API server is part of the ExosphereHost project and is licensed under the Elastic License 2.0 (ELv2).

## 📞 Support

For API server specific issues:
- **GitHub Issues**: [Create an issue](https://github.com/exospherehost/exospherehost/issues)
- **Email**: [nivedit@exosphere.host](mailto:nivedit@exosphere.host)
- **Discord**: [Join our community](https://discord.gg/JzCT6HRN)

---

**Built with ❤️ by the ExosphereHost team**