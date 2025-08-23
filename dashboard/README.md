# Exosphere Dashboard

A modern Next.js dashboard for visualizing and managing the Exosphere State Manager workflow. This application provides an intuitive interface for understanding and interacting with the state manager's node registration, graph template creation, and state execution processes.

## ✨ Features

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
NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL=http://localhost:8000
NEXT_PUBLIC_DEV_MODE=true
```

4. **Start the development server:**
```bash
npm run dev
```

5. **Open your browser** and navigate to [http://localhost:3000](http://localhost:3000)

### Environment Configuration

The dashboard supports the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL` | `http://localhost:8000` | URL of the State Manager backend API |
| `NEXT_PUBLIC_DEV_MODE` | `false` | Enable development mode features |
| `NEXT_PUBLIC_DEFAULT_NAMESPACE` | - | Default namespace to use |
| `NEXT_PUBLIC_DEFAULT_API_KEY` | - | Default API key (use with caution) |
| `NEXT_PUBLIC_DEFAULT_RUNTIME_NAME` | - | Default runtime name |
| `NEXT_PUBLIC_DEFAULT_GRAPH_NAME` | - | Default graph name |

## 🐳 Docker Deployment

### Using Docker

1. **Build the image:**
```bash
docker build -t exosphere-dashboard .
```

2. **Run the container:**
```bash
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL=http://your-state-manager-url:8000 \
  exosphere-dashboard
```

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
