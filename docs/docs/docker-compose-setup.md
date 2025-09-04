# Docker Compose Setup Guide

Get Exosphere running locally with Docker Compose in under 2 minutes. 

## Setup

This guide provides everything you need to run the complete Exosphere stack locally for development and testing.

Exosphere uses MongoDB as the database to manage states. You can either have mongodb setup locally or use a cloud hosted instance (recommended)

=== "Exosphere Local Setup with Cloud MongoDB(Rec)"

    1) Download Docker Compose Files

    First, download the Docker Compose files from the GitHub repository:
    
    === "curl"
        ```bash
        # Download docker-compose file for cloud MongoDB (recommended)
        curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose.yml
        ```
    === "wget"
        ```bash
        # Download docker-compose file for cloud MongoDB (recommended)
        wget https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose.yml
        ```
    
    2) Set up a cloud MongoDB
    Set up a mongodb cluster in a provider of your choice MongoDB Atlas, AWS DocumentDB. Get the mongo db url.
    
    3) Set up the secrets in env
    === ".env file"
        Create a `.env` file with your MongoDB connection:
        ```bash
        MONGO_URI=mongodb+srv://username:password@your-cluster.mongodb.net/
        ```
    === "Environment Variables"
        On your terminal:
        ```bash
        export MONGO_URI=mongodb+srv://username:password@your-cluster.mongodb.net/
        ```
    
    4) Download and start the services:
      ```bash
      docker compose -f docker-compose.yml up -d
      ```

     5) Done! This will start:
     
    - Exosphere State Manager : [http://localhost:8000](http://localhost:8000)
    - Exosphere Dashboard: [http://localhost:3000](http://localhost:3000)

=== "Exosphere Local Setup with Local MongoDB"

    For quick local testing only:

    1) Download Docker Compose Files

    First, download the Docker Compose files from the GitHub repository:
    
    === "curl"
        ```bash
        # Download docker-compose file with local MongoDB included
        curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose-with-mongodb.yml
        ```
    === "wget"
        ```bash
        # Download docker-compose file with local MongoDB included
        wget https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose-with-mongodb.yml
        ```
    
    2) Download and start the services:
      
        ```bash
        curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose-with-mongodb.yml && docker compose -f docker-compose-with-mongodb.yml up -d
        ```

    3) Done! This will start:
     
    - MongoDB database: [http://localhost:27017](http://localhost:27017)
    - Exosphere Dashboard: [http://localhost:3000](http://localhost:3000)
    - Exosphere State Manager: [http://localhost:8000](http://localhost:8000)


## Beta Version

To run the latest beta version of Exosphere with the newest features, replace container tags with `beta-latest`:

=== ".env File"

    ```bash
    EXOSPHERE_TAG=beta-latest
    ```
=== "Environment Variables"

    ```bash
    export EXOSPHERE_TAG=beta-latest
    ```

Get the docker image running:

=== "Cloud Mongodb"

    ```bash
    docker compose -f docker-compose.yml up -d
    ```
=== "Local Mongodb"

    ```bash
    docker compose -f docker-compose-with-mongodb.yml up -d
    ```

## Access Your Services

After running the Docker Compose command:

- **Exosphere Dashboard**: `http://localhost:3000`
- **State Manager API**: `http://localhost:8000`
- **MongoDB** (if using with-mongodb): `mongodb://localhost:27017` (not HTTP - use MongoDB clients like MongoDB Compass or mongosh)
- **API Documentation**: `http://localhost:8000/docs`

## Development Commands

=== "Cloud Mongodb"
    ```bash
    # Start services in background
    docker compose -f docker-compose.yml up -d

    # View logs
    docker compose -f docker-compose.yml logs -f

    # Stop services
    docker compose -f docker-compose.yml down

    # Stop services and remove volumes
    docker compose -f docker-compose.yml down -v

    # Pull latest images
    docker compose -f docker-compose.yml pull

    # Restart a specific service
    docker compose -f docker-compose.yml restart exosphere-state-manager
    ```
=== "Local Mongodb"
    ```bash
    # Start services in background
    docker compose -f docker-compose-with-mongodb.yml up -d

    # View logs
    docker compose -f docker-compose-with-mongodb.yml logs -f

    # Stop services
    docker compose -f docker-compose-with-mongodb.yml down

    # Stop services and remove volumes (⚠️ This will delete your data)
    docker compose -f docker-compose-with-mongodb.yml down -v

    # Pull latest images
    docker compose -f docker-compose-with-mongodb.yml pull

    # Restart a specific service
    docker compose -f docker-compose-with-mongodb.yml restart exosphere-state-manager
    ```


### Check Service Health

=== "Cloud Mongodb"
    ```bash
    # Check if all containers are running
    docker compose -f docker-compose.yml ps

    # Check state manager health
    curl http://localhost:8000/health

    # View container logs
    docker compose -f docker-compose.yml logs exosphere-state-manager
    ```


=== "Local Mongodb"
    ```bash
    # Check if all containers are running
    docker compose -f docker-compose-with-mongodb.yml ps

    # Check state manager health
    curl http://localhost:8000/health

    # View container logs
    docker compose -f docker-compose-with-mongodb.yml logs exosphere-state-manager
    ```

### Testing Your Setup

You can validate your docker-compose configuration before starting services:

=== "Cloud Mongodb"
    ```bash
    # Test configuration syntax
    docker compose -f docker-compose.yml config

    # Pull all required images
    docker compose -f docker-compose.yml pull

    # Start with health monitoring (--wait waits for all health checks)
    docker compose -f docker-compose.yml up -d --wait
    ```

    The `--wait` flag ensures all services pass their health checks before returning. The startup sequence will be:

    1. State Manager starts and passes health check (~10-30 seconds)  
    2. Dashboard starts and passes health check (~10-30 seconds)

=== "Local Mongodb"
    ```bash
    # Test configuration syntax
    docker compose -f docker-compose-with-mongodb.yml config

    # Pull all required images
    docker compose -f docker-compose-with-mongodb.yml pull

    # Start with health monitoring (--wait waits for all health checks)
    docker compose -f docker-compose-with-mongodb.yml up -d --wait
    ```

    The `--wait` flag ensures all services pass their health checks before returning. The startup sequence will be:

    1. MongoDB starts and passes health check (~10-30 seconds)
    2. State Manager starts and passes health check (~10-30 seconds)  
    3. Dashboard starts and passes health check (~10-30 seconds)


## Environment Variables

### Environment Variables for State Manager

| Variable | Description | Default Value | Required |
|----------|-------------|---------------|----------|
| `MONGO_URI` | MongoDB connection string | - | Required (for docker-compose.yml) |
| `STATE_MANAGER_SECRET` | API key for state manager authentication | `exosphere@123` | Has default |
| `MONGO_DATABASE_NAME` | MongoDB database name | `exosphere` | Has default |
| `SECRETS_ENCRYPTION_KEY` | Base64-encoded encryption key for secrets | `YTzpUlBGLSwm-3yKJRJTZnb0_aQuQQHyz64s8qAERVU=` | Has default |

> **Important**: The `SECRETS_ENCRYPTION_KEY` is used to encrypt secrets in the database. Changing this value will make existing encrypted secrets unreadable. Only change this key when setting up a new instance or if you're okay with losing access to existing encrypted data.

### Dashboard Environment Variables

#### **Server-Side Variables (REQUIRED - NOT exposed to browser)**
| Variable | Description | Default Value |
|----------|-------------|---------------|
| `EXOSPHERE_STATE_MANAGER_URI` | State manager API URI | `http://exosphere-state-manager:8000` |
| `EXOSPHERE_API_KEY` | **REQUIRED**: Secure API key for state manager access | `exosphere@123` |

#### **Client-Side Variables (Optional - exposed to browser)**
| Variable | Description | Default Value |
|----------|-------------|---------------|
| `NEXT_PUBLIC_DEFAULT_NAMESPACE` | Default namespace for workflows | `default` |

> **🔒 Security Note**: The dashboard now uses **Server-Side Rendering (SSR)** for enhanced security:
> - **API keys are never exposed** to the browser
> - **All API calls go through** secure server-side routes
> - **Production-ready security** architecture
> - **Environment isolation** between sensitive and public configuration
> 
> **💡 Default API Key**: `EXOSPHERE_API_KEY` defaults to `exosphere@123` (same as state manager's default secret)
> 
> **🔐 Authentication**: When the dashboard sends API requests to the state-manager, the `EXOSPHERE_API_KEY` value is checked for equality with the `STATE_MANAGER_SECRET` value in the state-manager container.

### MongoDB Local Setup Variables (for docker-compose-with-mongodb.yml only)

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `MONGO_INITDB_ROOT_USERNAME` | MongoDB root username | `admin` |
| `MONGO_INITDB_ROOT_PASSWORD` | MongoDB root password | `password` |
| `MONGO_INITDB_DATABASE` | Initial MongoDB database | `exosphere` |

### SDK Environment Variables

To use the Exosphere Python SDK with your running instance, set these environment variables in your development environment:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `EXOSPHERE_STATE_MANAGER_URI` | URL where the state manager is running | `http://localhost:8000` |
| `EXOSPHERE_API_KEY` | API key for authentication (same as STATE_MANAGER_SECRET) | `exosphere@123` |

## Custom Configuration

### Using Your Own Environment Variables

Create a `.env` file in the same directory as your docker-compose file:

```bash
# MongoDB Configuration (REQUIRED for docker-compose.yml)
MONGO_URI=mongodb+srv://username:password@your-cluster.mongodb.net/

# Optional Configuration (has defaults)
MONGO_DATABASE_NAME=exosphere
STATE_MANAGER_SECRET=your-custom-secret-key
SECRETS_ENCRYPTION_KEY=your-base64-encoded-encryption-key

# Dashboard Configuration
# Note: EXOSPHERE_API_KEY defaults to 'exosphere@123' if not specified
EXOSPHERE_API_KEY=your-secure-api-key
NEXT_PUBLIC_DEFAULT_NAMESPACE=YourNamespace

# For local MongoDB setup only (docker-compose-with-mongodb.yml)
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password
MONGO_INITDB_DATABASE=exosphere
```

Then run with your custom configuration:
```bash
# For cloud MongoDB (recommended)
docker compose -f docker-compose.yml up -d

# For local MongoDB
docker compose -f docker-compose-with-mongodb.yml up -d
```

**Note**: The docker-compose files now automatically use `.env` files in the same directory and provide sensible defaults for all optional variables.

### Generating a New Encryption Key

To generate a secure encryption key for `SECRETS_ENCRYPTION_KEY`:

```bash
# Using Python
python -c "import base64; import os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"

# Using OpenSSL
openssl rand -base64 32
```

## Security Architecture

### Server-Side Rendering (SSR) Implementation

The Exosphere Dashboard has been refactored to use Next.js API routes for enhanced security:

- **API Key Protection**: All sensitive credentials are stored server-side
- **Secure Communication**: Client never directly communicates with state-manager
- **Environment Isolation**: Sensitive config separated from public code
- **Production Ready**: Enterprise-grade security for production deployments

### API Route Structure

```
/api/runs              → Secure runs fetching with pagination
/api/graph-structure   → Protected graph visualization data
/api/namespace-overview → Secure namespace summary
/api/graph-template    → Protected template management
```

### Security Benefits

1. **No API Key Exposure**: Credentials never visible in browser
2. **Server-Side Validation**: All requests validated before reaching state-manager
3. **Environment Security**: Sensitive variables isolated from client bundle
4. **Audit Trail**: All API calls logged server-side for monitoring

### Docker Security Features

- **Environment Variable Isolation**: Server-side environment variables are set in containers and available to server processes, but are not exposed to the browser/client bundle
- **Network Security**: Services communicate over isolated Docker networks
- **Health Checks**: Built-in health monitoring for all services
- **Resource Limits**: Configurable resource constraints for production use

> **🔐 Authentication**: When making API requests to the state-manager, the `EXOSPHERE_API_KEY` value is checked for equality with the `STATE_MANAGER_SECRET` value in the state-manager container.

**Example SDK setup**:
```bash
# Set environment variables for SDK
export EXOSPHERE_STATE_MANAGER_URI=http://localhost:8000
export EXOSPHERE_API_KEY=exosphere@123

# Or add to your .env file for your Python project
echo "EXOSPHERE_STATE_MANAGER_URI=http://localhost:8000" >> .env
echo "EXOSPHERE_API_KEY=exosphere@123" >> .env
```

> **⚠️ Development Only — Do Not Use in Production**
>
> The MongoDB credentials above (`MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`, and `MONGO_INITDB_DATABASE`) are intended **only for local development**. These default values must **never be used in production environments**. For production deployments, use environment variable overrides, secure secrets management systems, or generate strong, unique credentials. Always rotate these values before deploying to any non-development environment.

## Legacy Docker Compose v1 Compatibility

If you have the legacy `docker-compose` (v1) binary instead of the newer `docker compose` (v2) plugin, you can use the hyphenated command format:

```bash
# Legacy v1 commands (replace "docker compose" with "docker-compose"):
docker-compose -f docker-compose.yml up -d
docker-compose -f docker-compose-with-mongodb.yml up -d
docker-compose -f docker-compose-with-mongodb.yml logs -f
docker-compose -f docker-compose-with-mongodb.yml down
```

**Creating an alias** (optional): To use the same commands as shown in this guide, create an alias:
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):
alias 'docker compose'='docker-compose'

# Or install the v2 plugin:
# https://docs.docker.com/compose/install/
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port mappings in the docker-compose file if ports 3000, 8000, or 27017 are already in use.

2. **MongoDB connection issues**: Ensure MongoDB is fully started before the state manager. Note that `depends_on` only waits for container startup, not readiness. The provided docker-compose files include proper healthchecks:

   **MongoDB healthcheck** (tests database connectivity):
   ```yaml
   mongodb:
     # ... other config ...
     healthcheck:
       test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
       interval: 10s
       timeout: 5s
       retries: 5
       start_period: 30s
   ```

   **State Manager healthcheck** (tests HTTP API readiness):
   ```yaml
   exosphere-state-manager:
     # ... other config ...
     healthcheck:
       test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
       interval: 10s
       timeout: 5s
       retries: 5
       start_period: 30s
     depends_on:
       mongodb:
         condition: service_healthy
   ```

   **Dashboard healthcheck** (tests Next.js app readiness):
   ```yaml
   exosphere-dashboard:
     # ... other config ...
     healthcheck:
       test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000', (res) => process.exit(res.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"]
       interval: 10s
       timeout: 5s
       retries: 5
       start_period: 30s
     depends_on:
       exosphere-state-manager:
         condition: service_healthy
   ```

3. **Authentication errors**: Verify your `STATE_MANAGER_SECRET` matches between the state manager and dashboard configuration.

4. **SDK connection issues**: Make sure `EXOSPHERE_STATE_MANAGER_URI` points to the correct URL and `EXOSPHERE_API_KEY` matches your `STATE_MANAGER_SECRET`. The `EXOSPHERE_API_KEY` value is checked for equality with the `STATE_MANAGER_SECRET` value when making API requests.

## Next Steps

Once your Exosphere instance is running:

1. **Set up your SDK environment variables**:
   ```bash
   export EXOSPHERE_STATE_MANAGER_URI=http://localhost:8000
   export EXOSPHERE_API_KEY=exosphere@123
   ```

2. **Install the Python SDK**:
   ```bash
   uv add exospherehost
   ```

3. **Create your first workflow** following the [Getting Started Guide](https://docs.exosphere.host/getting-started)

4. **Explore the dashboard** at `http://localhost:3000`

5. **Check out the API documentation** at `http://localhost:8000/docs`

## Support

- [Documentation](https://docs.exosphere.host)
- [Discord Community](https://discord.com/invite/zT92CAgvkj)
- [GitHub Issues](https://github.com/exospherehost/exospherehost/issues)
