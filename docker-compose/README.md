# Exosphere Docker Compose Setup

This directory contains Docker Compose files for running Exosphere locally with enhanced security.

## 🔒 **Security Updates**

The dashboard has been refactored to use **Server-Side Rendering (SSR)** for enhanced security:

- **API Key Protection**: All sensitive credentials are stored server-side
- **Secure Communication**: Client never directly communicates with state-manager
- **Environment Isolation**: Sensitive config separated from public code

## 📋 **Required Environment Variables**

### **Dashboard Configuration**
```bash
# Server-side secure configuration (NOT exposed to browser)
EXOSPHERE_STATE_MANAGER_URI=http://exosphere-state-manager:8000
EXOSPHERE_API_KEY=your-secure-api-key

# Client-side configuration (exposed to browser)
NEXT_PUBLIC_DEFAULT_NAMESPACE=your-namespace
```

> **💡 Default API Key**: If not specified, `EXOSPHERE_API_KEY` defaults to `exosphere@123` (same as `STATE_MANAGER_SECRET` in the state manager container)
> 
> **🔐 Authentication**: When the dashboard sends API requests to the state-manager, the `EXOSPHERE_API_KEY` value is checked for equality with the `STATE_MANAGER_SECRET` value in the state-manager container.

### **State Manager Configuration**
```bash
MONGO_URI=mongodb://admin:password@exosphere-mongodb:27017/
STATE_MANAGER_SECRET=your-secret-key
MONGO_DATABASE_NAME=exosphere
SECRETS_ENCRYPTION_KEY=your-encryption-key
```

## 🚀 **Quick Start**

1. **Set environment variables** in `.env` file
2. **Run with MongoDB**: `docker-compose -f docker-compose-with-mongodb.yml up -d`
3. **Run without MongoDB**: `docker-compose up -d`

For detailed setup instructions, please refer to the **[Docker Compose Setup Guide](https://docs.exosphere.host/docker-compose-setup)** in our official documentation.