# Docker Compose Setup Guide

Get Exosphere running locally with Docker Compose in under 2 minutes. This guide provides everything you need to run the complete Exosphere stack locally for development and testing.

## Download Docker Compose Files

First, download the Docker Compose files from the GitHub repository:

### Option 1: Download Both Files

```bash
# Download docker-compose file for cloud MongoDB (recommended)
curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose.yml

# Download docker-compose file with local MongoDB included
curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose-with-mongodb.yml
```

### Option 2: Using wget

```bash
# Download docker-compose file for cloud MongoDB (recommended)
wget https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose.yml

# Download docker-compose file with local MongoDB included
wget https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose-with-mongodb.yml
```

## Quick Start

We **recommend using a cloud MongoDB managed service** (MongoDB Atlas, AWS DocumentDB, etc.) for better performance, reliability, and security.

### Option 1: With Cloud MongoDB (Recommended)

1. Set up a cloud MongoDB instance (MongoDB Atlas, AWS DocumentDB, etc.)

2. Create a `.env` file with your MongoDB connection:
   ```bash
   MONGO_URI=mongodb+srv://username:password@your-cluster.mongodb.net/
   ```

3. Download and start the services:
   ```bash
   curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose.yml && docker compose -f docker-compose.yml up -d
   ```

This will start:
- Exosphere State Manager (port 8000)  
- Exosphere Dashboard (port 3000)

### Option 2: With Local MongoDB (Development Only)

For quick local testing only:

```bash
curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose-with-mongodb.yml && docker compose -f docker-compose-with-mongodb.yml up -d
```

This will start:
- MongoDB database (port 27017)
- Exosphere State Manager (port 8000)  
- Exosphere Dashboard (port 3000)

## Beta Version

To run the latest beta version of Exosphere with the newest features, replace container tags with `beta-latest`:

### Quick Beta Setup with Cloud MongoDB
```bash
# Download and modify for beta with cloud MongoDB
curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose.yml
perl -pi -e 's/:latest/:beta-latest/g' docker-compose.yml
# Set your MONGO_URI in .env file, then:
docker compose -f docker-compose.yml up -d
```

### Quick Beta Setup with Local MongoDB
```bash
# Download and modify for beta with local MongoDB
curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose-with-mongodb.yml
perl -pi -e 's/:latest/:beta-latest/g' docker-compose-with-mongodb.yml
docker compose -f docker-compose-with-mongodb.yml up -d
```

### Manual Beta Setup (Alternative)

1. Download the docker-compose file
2. Edit the file and change:
   ```yaml
   # Change from:
   image: ghcr.io/exospherehost/exosphere-state-manager:latest
   image: ghcr.io/exospherehost/exosphere-dashboard:latest
   
   # To:
   image: ghcr.io/exospherehost/exosphere-state-manager:beta-latest
   image: ghcr.io/exospherehost/exosphere-dashboard:beta-latest
   ```
3. Start the services with `docker compose up -d`

## Environment Variables

### Environment Variables for State Manager

| Variable | Description | Default Value | Required |
|----------|-------------|---------------|----------|
| `MONGO_URI` | MongoDB connection string | - | Required (for docker-compose.yml) |
| `STATE_MANAGER_SECRET` | API key for state manager authentication | `exosphere@123` | Has default |
| `MONGO_DATABASE_NAME` | MongoDB database name | `exosphere` | Has default |
| `SECRETS_ENCRYPTION_KEY` | Base64-encoded encryption key for secrets | `YTzpUlBGLSwm-3yKJRJTZnb0_aQuQQHyz64s8qAERVU=` | Has default |

> **Important**: The `SECRETS_ENCRYPTION_KEY` is used to encrypt secrets in the database. Changing this value will make existing encrypted secrets unreadable. Only change this key when setting up a new instance or if you're okay with losing access to existing encrypted data.

### Dashboard Environment Variables (All Optional)

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL` | State manager API URL | `http://exosphere-state-manager:8000` |
| `NEXT_PUBLIC_DEFAULT_NAMESPACE` | Default namespace for workflows | `WhatPeopleWant` |
| `NEXT_PUBLIC_DEFAULT_API_KEY` | Default API key for dashboard | `exosphere@123` |

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

**Example SDK setup**:
```bash
# Set environment variables for SDK
export EXOSPHERE_STATE_MANAGER_URI=http://localhost:8000
export EXOSPHERE_API_KEY=exosphere@123

# Or add to your .env file for your Python project
echo "EXOSPHERE_STATE_MANAGER_URI=http://localhost:8000" >> .env
echo "EXOSPHERE_API_KEY=exosphere@123" >> .env
```

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

# Dashboard Configuration (Optional)
NEXT_PUBLIC_DEFAULT_NAMESPACE=YourNamespace
NEXT_PUBLIC_DEFAULT_API_KEY=your-custom-secret-key

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

## Access Your Services

After running the Docker Compose command:

- **Exosphere Dashboard**: http://localhost:3000
- **State Manager API**: http://localhost:8000
- **MongoDB** (if using with-mongodb): http://localhost:27017
- **API Documentation**: http://localhost:8000/docs

## Development Commands

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

## Troubleshooting

### Check Service Health

```bash
# Check if all containers are running
docker compose -f docker-compose-with-mongodb.yml ps

# Check state manager health
curl http://localhost:8000/health

# View container logs
docker compose -f docker-compose-with-mongodb.yml logs exosphere-state-manager
```

### Common Issues

1. **Port already in use**: Change the port mappings in the docker-compose file if ports 3000, 8000, or 27017 are already in use.

2. **MongoDB connection issues**: Ensure MongoDB is fully started before the state manager. The `depends_on` configuration handles this automatically.

3. **Authentication errors**: Verify your `STATE_MANAGER_SECRET` matches between the state manager and dashboard configuration.

4. **SDK connection issues**: Make sure `EXOSPHERE_STATE_MANAGER_URI` points to the correct URL and `EXOSPHERE_API_KEY` matches your `STATE_MANAGER_SECRET`.

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

4. **Explore the dashboard** at http://localhost:3000

5. **Check out the API documentation** at http://localhost:8000/docs

## Support

- [Documentation](https://docs.exosphere.host)
- [Discord Community](https://discord.com/invite/zT92CAgvkj)
- [GitHub Issues](https://github.com/exospherehost/exospherehost/issues)
