# Security Architecture

## Overview

This dashboard has been refactored to use **Server-Side Rendering (SSR)** for enhanced security. All API calls to the state-manager are now handled server-side, keeping sensitive information like API keys secure.

## Architecture Changes

### Before (Client-Side)
- API key was visible in browser
- Direct calls to state-manager from client
- Security risk in production environments

### After (Server-Side)
- API key stored securely in environment variables
- All API calls go through Next.js API routes
- Client never sees sensitive credentials

## Environment Variables

### Server-Side (NOT exposed to browser)
```bash
EXOSPHERE_STATE_MANAGER_URL=http://localhost:8000
EXOSPHERE_STATE_MANAGER_API_KEY=your-secure-api-key-here
```

### Client-Side (exposed to browser)
```bash
NEXT_PUBLIC_DEFAULT_NAMESPACE=your-namespace
```



## API Routes

The following server-side API routes handle all communication with the state-manager:

- `/api/runs` - Fetch paginated runs
- `/api/graph-structure` - Get graph visualization data
- `/api/namespace-overview` - Get namespace summary data
- `/api/graph-template` - Manage graph templates

## Security Benefits

1. **API Key Protection**: API keys are never exposed to the client
2. **Server-Side Validation**: All requests are validated server-side
3. **Environment Isolation**: Sensitive config separated from client code
4. **Production Ready**: Secure for deployment in production environments

## Setup Instructions

1. Copy `env.example` to `.env.local`
2. Set your actual API key in `EXOSPHERE_STATE_MANAGER_API_KEY`
3. Configure your state-manager URL in `EXOSPHERE_STATE_MANAGER_URL`
4. Set your default namespace in `NEXT_PUBLIC_DEFAULT_NAMESPACE`

## Development vs Production

- **Development**: Uses localhost URLs and development API keys
- **Production**: Uses production URLs and secure API keys
- **Environment**: Automatically detects and uses appropriate configuration

## Best Practices

1. **Never commit `.env.local`** to version control
2. **Use strong, unique API keys** for production
3. **Rotate API keys** regularly
4. **Monitor API usage** for security anomalies
5. **Use HTTPS** in production environments 