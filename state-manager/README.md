# ExosphereHost State Manager

The ExosphereHost State Manager is a distributed state management service that coordinates the execution of satellites and clusters across the ExosphereHost platform. It provides reliable state persistence, workflow orchestration, and execution tracking for AI workflows.

## 🏗️ Overview

The State Manager serves as the central coordination hub for the ExosphereHost platform, handling:

- **🔄 Workflow Orchestration**: Managing the execution flow of satellite clusters
- **📊 State Persistence**: Reliable storage and retrieval of execution state
- **🔗 Dependency Management**: Handling satellite dependencies and data flow
- **⚡ Real-time Updates**: WebSocket-based real-time status updates
- **🔄 Retry Logic**: Automatic retry mechanisms for failed executions
- **📈 Scaling**: Horizontal scaling of satellite execution across compute resources

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Redis (for state storage and pub/sub)
- PostgreSQL or MongoDB (for persistent storage)
- UV package manager (recommended)

### Installation

1. **Navigate to the state manager directory:**
   ```bash
   cd state-manager
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
   REDIS_URI=redis://localhost:6379
   DATABASE_URI=postgresql://user:password@localhost:5432/exosphere_state
   ENVIRONMENT=development
   LOG_LEVEL=info
   MAX_CONCURRENT_EXECUTIONS=100
   RETRY_ATTEMPTS=3
   RETRY_DELAY=5
   ```

4. **Run the state manager:**
   ```bash
   uv run python run.py
   ```

The state manager will be available at `http://localhost:8001`

### Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f state-manager
   ```

## 🏛️ Architecture

### Core Components

```
State Manager
├── 📊 Execution Engine     # Orchestrates satellite execution
├── 🔄 State Store         # Manages execution state
├── 📡 Message Broker      # Handles inter-service communication
├── 🔗 Dependency Resolver # Manages satellite dependencies
├── 📈 Metrics Collector   # Collects performance metrics
└── 🔌 API Interface       # REST and WebSocket APIs
```

### Data Flow

1. **Cluster Submission**: Clusters are submitted via API or SDK
2. **Dependency Analysis**: State manager analyzes satellite dependencies
3. **Execution Planning**: Creates execution plan with optimal parallelization
4. **Resource Allocation**: Allocates compute resources for satellites
5. **Execution Monitoring**: Tracks progress and handles failures
6. **State Updates**: Provides real-time updates to clients
7. **Completion Handling**: Manages cleanup and result aggregation

## 🛠️ Core Features

### Workflow Orchestration

```python
# Example: Submitting a cluster for execution
from exospherehost.state_manager import StateManagerClient

client = StateManagerClient(uri="http://localhost:8001")

cluster_config = {
    "identifier": "my-project/data-processing",
    "sla": "6h",
    "satellites": [
        {
            "name": "data-ingestion",
            "uses": "satellite/exospherehost/get-files-from-s3",
            "config": {"bucket": "my-data-bucket"}
        },
        {
            "name": "data-processing",
            "uses": "satellite/exospherehost/parse-pdf-with-docling",
            "dependencies": ["data-ingestion"]
        }
    ]
}

execution_id = await client.submit_cluster(cluster_config)
```

### Real-time Status Updates

```python
# Example: Monitoring execution status
async def monitor_execution(execution_id):
    async with client.watch_execution(execution_id) as stream:
        async for update in stream:
            print(f"Status: {update.status}")
            print(f"Progress: {update.progress}%")
            if update.status == "completed":
                print(f"Results: {update.results}")
                break
```

### State Persistence

The State Manager provides persistent storage for:
- **Execution History**: Complete audit trail of all executions
- **Intermediate Results**: Satellite outputs for dependency resolution
- **Error Logs**: Detailed error information for debugging
- **Metrics**: Performance and resource usage statistics

## 📊 State Model

### Execution State

```json
{
  "execution_id": "uuid",
  "cluster_id": "string",
  "status": "pending|running|completed|failed|cancelled",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "sla": "6h|12h|24h",
  "satellites": [
    {
      "satellite_id": "string",
      "name": "string",
      "status": "pending|running|completed|failed",
      "start_time": "timestamp",
      "end_time": "timestamp",
      "output": "object",
      "error": "string",
      "retries": "number"
    }
  ],
  "dependencies": {
    "satellite_id": ["dependency_ids"]
  },
  "progress": {
    "total_satellites": "number",
    "completed_satellites": "number",
    "failed_satellites": "number"
  }
}
```

### Satellite State

```json
{
  "satellite_id": "string",
  "execution_id": "string",
  "name": "string",
  "identifier": "satellite/project/name",
  "status": "pending|running|completed|failed",
  "config": "object",
  "input": "object",
  "output": "object",
  "error": "string",
  "start_time": "timestamp",
  "end_time": "timestamp",
  "duration_ms": "number",
  "retries": "number",
  "resource_usage": {
    "cpu_time": "number",
    "memory_peak": "number",
    "gpu_time": "number"
  }
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URI` | Redis connection string | `redis://localhost:6379` |
| `DATABASE_URI` | Database connection string | Required |
| `MAX_CONCURRENT_EXECUTIONS` | Max parallel executions | `100` |
| `RETRY_ATTEMPTS` | Default retry attempts | `3` |
| `RETRY_DELAY` | Retry delay in seconds | `5` |
| `EXECUTION_TIMEOUT` | Max execution time | `3600` |
| `CLEANUP_INTERVAL` | State cleanup interval | `300` |
| `METRICS_ENABLED` | Enable metrics collection | `true` |

### Advanced Configuration

```yaml
# config.yaml
state_manager:
  execution:
    max_concurrent: 100
    timeout_seconds: 3600
    retry_policy:
      max_attempts: 3
      backoff_strategy: exponential
      base_delay: 5
  
  storage:
    redis:
      uri: redis://localhost:6379
      pool_size: 10
    database:
      uri: postgresql://localhost:5432/exosphere
      pool_size: 20
  
  monitoring:
    metrics_enabled: true
    health_check_interval: 30
    log_level: info
```

## 📡 API Reference

### REST Endpoints

#### Execution Management
- `POST /executions` - Submit cluster for execution
- `GET /executions/{execution_id}` - Get execution status
- `DELETE /executions/{execution_id}` - Cancel execution
- `GET /executions` - List executions with filtering

#### Satellite Management
- `GET /satellites/{satellite_id}` - Get satellite status
- `POST /satellites/{satellite_id}/retry` - Retry failed satellite
- `GET /satellites/{satellite_id}/logs` - Get satellite logs

#### State Queries
- `GET /state/summary` - Get system state summary
- `GET /state/metrics` - Get performance metrics
- `GET /state/health` - Health check endpoint

### WebSocket Endpoints

#### Real-time Updates
- `WS /ws/executions/{execution_id}` - Real-time execution updates
- `WS /ws/satellites/{satellite_id}` - Real-time satellite updates
- `WS /ws/system/metrics` - Real-time system metrics

## 🔄 Retry and Error Handling

### Retry Policies

The State Manager supports configurable retry policies:

```python
retry_policy = {
    "max_attempts": 3,
    "backoff_strategy": "exponential",  # linear, exponential, fixed
    "base_delay": 5,  # seconds
    "max_delay": 300,  # seconds
    "jitter": True,  # add random jitter
    "retry_on": ["timeout", "network_error", "resource_unavailable"]
}
```

### Error Categories

- **Transient Errors**: Network timeouts, resource unavailability (retryable)
- **Configuration Errors**: Invalid satellite config, missing secrets (not retryable)
- **Resource Errors**: Insufficient compute, storage limits (retryable with backoff)
- **Logic Errors**: Satellite execution failures (configurable retry)

## 📈 Monitoring and Observability

### Metrics

The State Manager exposes metrics for monitoring:

- **Execution Metrics**: Total executions, success/failure rates, duration
- **Satellite Metrics**: Execution times, resource usage, error rates
- **System Metrics**: Memory usage, CPU utilization, queue depths
- **Business Metrics**: Cost per execution, SLA compliance

### Logging

Structured logging with the following information:
- Execution lifecycle events
- Satellite state transitions
- Error details with stack traces
- Performance metrics
- Resource allocation events

### Health Checks

- **Liveness**: Basic service health
- **Readiness**: Service ready to accept requests
- **Dependencies**: Redis, database, and external service health

## 🚀 Deployment

### Production Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t exosphere-state-manager .
   ```

2. **Run with production settings:**
   ```bash
   docker run -d \
     --name exosphere-state-manager \
     -p 8001:8001 \
     -e ENVIRONMENT=production \
     -e REDIS_URI=redis://production-redis:6379 \
     -e DATABASE_URI=postgresql://prod-db:5432/exosphere \
     exosphere-state-manager
   ```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: state-manager
spec:
  replicas: 3
  selector:
    matchLabels:
      app: state-manager
  template:
    metadata:
      labels:
        app: state-manager
    spec:
      containers:
      - name: state-manager
        image: exosphere-state-manager:latest
        ports:
        - containerPort: 8001
        env:
        - name: REDIS_URI
          value: "redis://redis-service:6379"
        - name: DATABASE_URI
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database-uri
```

### Scaling Considerations

- **Horizontal Scaling**: Multiple state manager instances with shared Redis/DB
- **Redis Clustering**: Use Redis Cluster for high availability
- **Database Sharding**: Partition execution data by project or time
- **Load Balancing**: Use consistent hashing for WebSocket connections

## 🔒 Security

### Authentication

The State Manager integrates with the API Server for authentication:
- JWT token validation
- Project-based authorization
- API key authentication for services

### Data Security

- **Encryption at Rest**: Database and Redis data encryption
- **Encryption in Transit**: TLS for all external communications
- **Secret Management**: Secure handling of satellite secrets
- **Audit Logging**: Complete audit trail of all operations

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/state-manager-enhancement`
3. **Make your changes** following the coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### Development Guidelines

- Use async/await for all I/O operations
- Implement proper error handling and logging
- Add comprehensive tests for state transitions
- Follow the existing code structure and patterns
- Update API documentation for new endpoints

## 📄 License

This State Manager is part of the ExosphereHost project and is licensed under the Elastic License 2.0 (ELv2).

## 📞 Support

For State Manager specific issues:
- **GitHub Issues**: [Create an issue](https://github.com/exospherehost/exospherehost/issues)
- **Email**: [nivedit@exosphere.host](mailto:nivedit@exosphere.host)
- **Discord**: [Join our community](https://discord.gg/JzCT6HRN)

---

**Orchestrating the future of AI workflows 🚀**