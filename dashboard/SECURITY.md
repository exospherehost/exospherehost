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
EXOSPHERE_STATE_MANAGER_URI=http://localhost:8000
EXOSPHERE_API_KEY=exosphere@123
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
2. **Optional**: Override the default API key in `EXOSPHERE_API_KEY` (defaults to `exosphere@123`, same as `STATE_MANAGER_SECRET` in the state manager container)
3. **Authentication**: The `EXOSPHERE_API_KEY` value is checked for equality with the `STATE_MANAGER_SECRET` value when making API requests to the state-manager
4. Configure your state-manager URI in `EXOSPHERE_STATE_MANAGER_URI`
5. Set your default namespace in `NEXT_PUBLIC_DEFAULT_NAMESPACE`

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