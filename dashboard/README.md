# Exosphere Dashboard

A modern Next.js dashboard for visualizing and managing the Exosphere State Manager workflow. This application provides an intuitive interface for understanding and interacting with the state manager's node registration, graph template creation, and state execution processes.

## ✨ Features

### 🔒 **Secure Server-Side Architecture**
- **Server-Side Rendering (SSR)**: All API calls handled securely on the server
- **Protected API Keys**: Sensitive credentials never exposed to the browser
- **Production Ready**: Enterprise-grade security for production deployments
- **Environment Isolation**: Secure separation of sensitive and public configuration

### 📊 Overview Dashboard
- **Namespace Overview**: Comprehensive view of your state manager namespace
- **Real-time Statistics**: Live metrics and status indicators
- **Quick Actions**: Fast access to common operations
- **Visual Analytics**: Charts and graphs showing system performance

### 🔧 Graph Template Management
- **Visual Graph Builder**: Create and edit graph templates with an intuitive drag-and-drop interface
- **Node Configuration**: Add, edit, and remove nodes with their parameters
- **Connection Management**: Define node relationships and data flow with visual connections
- **Template Validation**: Real-time validation of graph templates
- **Template Details**: Comprehensive view of saved graph templates

### 📈 State Execution Tracking
- **Run States View**: Track execution states by run ID
- **Real-time Status Updates**: Monitor state progression through the workflow
- **Execution Control**: Execute, retry, or cancel states directly from the UI
- **Detailed State Information**: Expand states to view inputs, outputs, and metadata
- **State Lifecycle Visualization**: Color-coded status indicators for all state types

### 🔍 Node Management
- **Node Schema Viewer**: Detailed view of registered nodes with input/output schemas
- **Parameter Highlighting**: Clear visualization of required vs optional parameters
- **Secret Management**: View and manage node secrets securely
- **Schema Validation**: JSON schema rendering with type information
- **Node Details Modal**: Comprehensive node information display

## 🚀 Getting Started

### Prerequisites

- **Node.js 18+** 
- **A running State Manager backend** (default: http://localhost:8000)
- **Valid API key and namespace**
- **Environment configuration file** (`.env.local`)

### Quick Start

1. **Clone and navigate to the dashboard directory:**
```bash
cd dashboard
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
# Copy the example environment file
cp env.example .env.local

# Edit .env.local with your configuration
EXOSPHERE_STATE_MANAGER_URI=http://localhost:8000
EXOSPHERE_API_KEY=your-secure-api-key-here
NEXT_PUBLIC_DEFAULT_NAMESPACE=your-namespace
```

4. **Start the development server:**
```bash
npm run dev
```

5. **Open your browser** and navigate to `http://localhost:3000`

### Environment Configuration

The dashboard uses a secure server-side architecture with the following environment variables:

#### 🔒 **Server-Side Variables (NOT exposed to browser)**
| Variable | Default | Description |
|----------|---------|-------------|
| `EXOSPHERE_STATE_MANAGER_URI` | `http://localhost:8000` | URI of the State Manager backend API |
| `EXOSPHERE_API_KEY` | `exosphere@123` | **REQUIRED**: Your secure API key for state manager access |

#### 🌐 **Client-Side Variables (exposed to browser)**
| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_DEFAULT_NAMESPACE` | `testnamespace` | Default namespace to use on dashboard startup |

> **⚠️ Security Note**: Server-side variables are never exposed to the browser, keeping your API keys secure.
> 
> **💡 Default API Key**: `EXOSPHERE_API_KEY` defaults to `exosphere@123` (same as `STATE_MANAGER_SECRET` in the state manager container)
> 
> **🔐 Authentication**: When the dashboard sends API requests to the state-manager, the `EXOSPHERE_API_KEY` value is checked for equality with the `STATE_MANAGER_SECRET` value in the state-manager container.

## 🐳 Docker Deployment

### Using Docker

1. **Build the image:**
```bash
docker build -t exosphere-dashboard .
```

2. **Run the container with secure environment variables:**
```bash
docker run -d \
  -p 3000:3000 \
  -e EXOSPHERE_STATE_MANAGER_URI=http://your-state-manager-url:8000 \
  -e EXOSPHERE_API_KEY=your-secure-api-key \
  -e NEXT_PUBLIC_DEFAULT_NAMESPACE=your-namespace \
  exosphere-dashboard
```

> **🔒 Security**: API keys are securely handled server-side and never exposed to the browser.
> 
> **💡 Default API Key**: If not specified, `EXOSPHERE_API_KEY` defaults to `exosphere@123` (same as `STATE_MANAGER_SECRET` in the state manager container)
> 
> **🔐 Authentication**: When the dashboard sends API requests to the state-manager, the `EXOSPHERE_API_KEY` value is checked for equality with the `STATE_MANAGER_SECRET` value in the state-manager container.

## 🔒 Security Architecture

### **Server-Side Rendering (SSR) Implementation**

The dashboard has been refactored to use Next.js API routes for enhanced security:

- **API Key Protection**: All sensitive credentials are stored server-side
- **Secure Communication**: Client never directly communicates with state-manager
- **Environment Isolation**: Sensitive config separated from public code
- **Production Ready**: Enterprise-grade security for production deployments

### **API Route Structure**

```
/api/runs              → Secure runs fetching with pagination
/api/graph-structure   → Protected graph visualization data
/api/namespace-overview → Secure namespace summary
/api/graph-template    → Protected template management
```

### **Security Benefits**

1. **No API Key Exposure**: Credentials never visible in browser
2. **Server-Side Validation**: All requests validated before reaching state-manager
3. **Environment Security**: Sensitive variables isolated from client bundle
4. **Audit Trail**: All API calls logged server-side for monitoring

## 📖 Usage Guide

### 1. Overview Dashboard

The Overview tab provides a comprehensive view of your namespace:

- **Namespace Statistics**: View total nodes, graphs, and states
- **Recent Activity**: See the latest state executions and updates
- **Quick Actions**: Fast access to create new graphs or view states
- **System Health**: Monitor the overall health of your state manager

### 2. Graph Template Builder

Create and manage graph templates:

1. **Navigate to the "Graph Template" tab**
2. **Add Nodes**: Click to add nodes to your graph
3. **Configure Parameters**: Set input/output parameters for each node
4. **Create Connections**: Define data flow between nodes
5. **Save Template**: Save your graph template to the state manager
6. **View Details**: Click on saved templates to see detailed information

### 3. State Execution Tracking

Monitor and control state execution:

1. **Navigate to the "Run States" tab**
2. **View States by Run ID**: See all states for a specific execution run
3. **Monitor Status**: Track state progression through the workflow
4. **Control Execution**: Execute, retry, or cancel states as needed
5. **View Details**: Expand states to see inputs, outputs, and metadata

### 4. Node Management

Explore registered nodes:

1. **Access from Overview**: Click on nodes in the overview
2. **View Schemas**: See detailed input/output specifications
3. **Parameter Details**: Understand required vs optional parameters
4. **Secret Information**: View node secret requirements

## 🔧 Configuration

### Header Configuration

Configure your dashboard settings in the header:

- **Namespace**: Your state manager namespace
- **API Key**: Authentication key for the state manager
- **Runtime Name**: Name for your runtime (used in node registration)
- **Graph Name**: Name for your graph template

### API Integration

The dashboard integrates with the State Manager API endpoints:

- `PUT /v0/namespace/{namespace}/nodes/` - Register nodes
- `PUT /v0/namespace/{namespace}/graph/{graph_name}` - Create/update graph template
- `GET /v0/namespace/{namespace}/graph/{graph_name}` - Get graph template
- `POST /v0/namespace/{namespace}/graph/{graph_name}/states/create` - Create states
- `POST /v0/namespace/{namespace}/states/enqueue` - Enqueue states
- `POST /v0/namespace/{namespace}/states/{state_id}/executed` - Execute state
- `GET /v0/namespace/{namespace}/state/{state_id}/secrets` - Get secrets

## 🏗️ Architecture

### Technology Stack

- **Frontend Framework**: Next.js 15 with React 19
- **Styling**: Tailwind CSS 4
- **UI Components**: Custom components with Lucide React icons
- **Graph Visualization**: ReactFlow for graph building
- **Charts**: Recharts for data visualization
- **Type Safety**: TypeScript throughout

### Project Structure

```
dashboard/
├── src/
│   ├── app/
│   │   └── page.tsx              # Main dashboard application
│   ├── components/
│   │   ├── GraphTemplateBuilder.tsx    # Graph template creation
│   │   ├── NamespaceOverview.tsx       # Overview dashboard
│   │   ├── StatesByRunId.tsx           # State execution tracking
│   │   ├── NodeDetailModal.tsx         # Node details modal
│   │   ├── GraphTemplateDetailModal.tsx # Graph template details
│   │   └── GraphVisualization.tsx      # Graph visualization
│   ├── services/
│   │   └── api.ts               # API service layer
│   └── types/
│       └── state-manager.ts     # TypeScript definitions
├── public/                      # Static assets
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose setup
└── env.example                  # Environment variables template
```

### Key Components

- **NamespaceOverview**: Main dashboard with statistics and quick actions
- **GraphTemplateBuilder**: Visual graph template creation interface
- **StatesByRunId**: State execution tracking and management
- **NodeDetailModal**: Detailed node information display
- **GraphTemplateDetailModal**: Comprehensive graph template view
- **GraphVisualization**: Interactive graph visualization

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Development Features

- **Hot Reload**: Fast development with Next.js hot reloading
- **TypeScript**: Full type safety throughout the application
- **ESLint**: Code quality and consistency
- **Turbopack**: Fast bundling for development

### State Status Types

The application tracks various state statuses:

- **CREATED**: State has been created and is waiting to be processed
- **QUEUED**: State is queued and waiting for execution
- **EXECUTED**: State has been executed successfully
- **NEXT_CREATED**: Next state has been created based on this execution
- **RETRY_CREATED**: Retry state has been created due to failure
- **TIMEDOUT**: State execution timed out
- **ERRORED**: State execution failed with an error
- **CANCELLED**: State execution was cancelled
- **SUCCESS**: State completed successfully

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests if applicable
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Submit a pull request**

### Development Guidelines

- Follow TypeScript best practices
- Use Tailwind CSS for styling
- Write clean, readable code
- Add appropriate error handling
- Test your changes thoroughly

## 📄 License

This project is part of the Exosphere State Manager ecosystem.

## 🆘 Support

For support and questions:

- Check the [Exosphere State Manager documentation](https://docs.exosphere.com)
- Open an issue in the repository
- Contact the development team

---

**Built with ❤️ for the Exosphere ecosystem**
