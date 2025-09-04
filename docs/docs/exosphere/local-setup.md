# Local Setup Guide

This guide walks you through setting up Exosphere locally for development and testing. You'll learn how to run both the state manager and dashboard components, either using Docker Compose for quick setup or running them individually for more control.

## Overview

Exosphere consists of two main components that work together:

1. **State Manager** - Backend service that handles workflow execution and state management
2. **Dashboard** - Web interface for monitoring and managing workflows

You can set these up using:

- **Docker Compose** (recommended for quick start) - runs both services together
- **Individual Setup** - run each service separately for development

## Prerequisites

Before you begin, ensure you have:

- [Docker](https://docs.docker.com/get-docker/) installed (for Docker Compose approach)
- [Python 3.12+](https://www.python.org/downloads/) (for individual setup)
- [Node.js 18+](https://nodejs.org/) (for dashboard development)
- [MongoDB](https://www.mongodb.com/try/download/community) instance (cloud or local)

## Setup

=== "Docker Compose Setup (Recommended)"

    The fastest way to get Exosphere running locally is using Docker Compose. This approach handles all the configuration and networking automatically.

    Follow the guide: [Get Exosphere running locally with Docker](../docker-compose-setup.md)

=== "Individual Component Setup"

    If you prefer more control over each component or want to develop locally, you can set up the state manager and dashboard separately.

    To get Exosphere state manager running, follow [State Manager Setup](./state-manager-setup.md)

    For complete monitoring dashboard setup details, see our [Dashboard Guide](./dashboard.md).


## Testing Your Setup

Once both services are running, test the complete setup:

1. **Verify state manager**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify dashboard**:
   ```bash
   curl http://localhost:3000
   ```

3. **Check API documentation**:
   - Open http://localhost:8000/docs in your browser
   - Test the `/health` endpoint

## Next Steps

With your local Exosphere instance running, you're ready to:

1. **[Register your first node](./register-node.md)** - Create custom processing logic
2. **[Create and run workflows](./create-graph.md)** - Build your first workflow
3. **[Monitor execution](./dashboard.md)** - Use the dashboard to track progress

## Troubleshooting

### Common Issues

**Port conflicts**: If ports 8000 or 3000 are already in use, modify the port mappings in your Docker commands or configuration files.

**MongoDB connection**: Ensure your MongoDB instance is accessible and the connection string is correct.

**Authentication errors**: Verify that `EXOSPHERE_API_KEY` matches `STATE_MANAGER_SECRET`.

**Dashboard can't connect**: Check that the state manager is running and accessible at the configured URI.

### Getting Help

- Check the [Docker Compose Setup Guide](../docker-compose-setup.md) for detailed configuration
- Review the [State Manager Setup Guide](./state-manager-setup.md) for backend troubleshooting
- Consult the [Dashboard Guide](./dashboard.md) for frontend issues
- Join our [Discord community](https://discord.com/invite/zT92CAgvkj) for support

## Production Considerations

For production deployment options, see our [hosted platform](https://exosphere.host) or contact our team for enterprise solutions.