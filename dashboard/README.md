# State Manager Frontend

A comprehensive Next.js frontend for visualizing and managing the Exosphere State Manager workflow. This application provides an intuitive interface for understanding and interacting with the state manager's node registration, graph template creation, and state execution processes.

## Features

### 🎯 Workflow Visualization
- **Interactive Workflow Steps**: Visual representation of the complete state manager workflow
- **Real-time Status Updates**: See each step progress from pending → active → completed/error
- **Step-by-step Execution**: Click on any step to execute it individually
- **Auto-advancement**: Automatically progress through the workflow

### 🔧 Node Management
- **Node Schema Viewer**: Detailed view of registered nodes with input/output schemas
- **Parameter Highlighting**: Clear visualization of required vs optional parameters
- **Secret Management**: View and manage node secrets
- **Schema Validation**: JSON schema rendering with type information

### 🏗️ Graph Template Builder
- **Visual Graph Builder**: Create and edit graph templates with a user-friendly interface
- **Node Configuration**: Add, edit, and remove nodes with their parameters
- **Connection Management**: Define node relationships and data flow
- **Secret Configuration**: Manage graph-level secrets

### 📊 State Management
- **State Lifecycle Tracking**: Monitor states through their complete lifecycle
- **Status Visualization**: Color-coded status indicators for all state types
- **Execution Control**: Execute, retry, or cancel states directly from the UI
- **Detailed State Information**: Expand states to view inputs, outputs, and metadata

## State Manager Workflow

The frontend visualizes the complete state manager workflow:

1. **Register Nodes** → Register nodes with their schemas and secrets
2. **Create Graph Template** → Define the workflow structure with nodes and connections
3. **Create States** → Generate execution states for the graph template
4. **Enqueue States** → Queue states for execution
5. **Execute States** → Execute states and handle results

## State Status Types

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

## Getting Started

### Prerequisites

- Node.js 18+ 
- A running State Manager backend (default: http://localhost:8000)
- Valid API key and namespace

### Installation

1. Clone the repository and navigate to the frontend directory:
```bash
cd state-manager-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables (optional):
```bash
# Create .env.local file
NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

### Docker Deployment

You can also run the dashboard using Docker. The container is configurable through environment variables.

#### Using Docker Compose

1. Create a `.env` file in the dashboard directory:
```bash
# Configure the State Manager URL
NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL=http://your-state-manager-url:8000
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

#### Using Docker directly

1. Build the image:
```bash
docker build -t exosphere-dashboard .
```

2. Run the container with custom configuration:
```bash
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL=http://your-state-manager-url:8000 \
  exosphere-dashboard
```

#### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL` | `http://localhost:8000` | URL of the State Manager backend API |

### Configuration

The frontend requires the following configuration:

- **Namespace**: Your state manager namespace
- **API Key**: Authentication key for the state manager
- **Runtime Name**: Name for your runtime (used in node registration)
- **Graph Name**: Name for your graph template

These can be configured in the header of the application.

## Usage

### 1. Workflow Execution

1. Navigate to the "Workflow" tab
2. Configure your namespace and API key in the header
3. Click "Start Workflow" to begin the automated execution
4. Watch as each step progresses through the workflow
5. Click on individual steps to execute them manually

### 2. Node Management

1. Navigate to the "Nodes" tab after running the workflow
2. View registered nodes with their schemas
3. Expand nodes to see detailed input/output specifications
4. Review required secrets and parameters

### 3. Graph Template Building

1. Navigate to the "Graph Template" tab
2. Add nodes with their configurations
3. Define node connections and data flow
4. Configure secrets for the graph
5. Save the template to the state manager

### 4. State Management

1. Navigate to the "States" tab
2. View all created states with their current status
3. Execute, retry, or cancel states as needed
4. Expand states to view detailed information

## API Integration

The frontend integrates with the State Manager API endpoints:

- `PUT /v0/namespace/{namespace}/nodes/` - Register nodes
- `PUT /v0/namespace/{namespace}/graph/{graph_name}` - Create/update graph template
- `GET /v0/namespace/{namespace}/graph/{graph_name}` - Get graph template
- `POST /v0/namespace/{namespace}/graph/{graph_name}/states/create` - Create states
- `POST /v0/namespace/{namespace}/states/enqueue` - Enqueue states
- `POST /v0/namespace/{namespace}/states/{state_id}/executed` - Execute state
- `GET /v0/namespace/{namespace}/state/{state_id}/secrets` - Get secrets

## Architecture

### Components

- **WorkflowVisualizer**: Displays the workflow steps and their status
- **NodeSchemaViewer**: Shows node schemas and parameters
- **StateManager**: Manages state lifecycle and execution
- **GraphTemplateBuilder**: Builds and edits graph templates

### Services

- **apiService**: Handles all API communication with the state manager

### Types

- Complete TypeScript definitions matching the state manager API models
- Workflow state management types
- Component prop interfaces

## Development

### Project Structure

```
src/
├── app/
│   └── page.tsx              # Main dashboard
├── components/
│   ├── WorkflowVisualizer.tsx
│   ├── NodeSchemaViewer.tsx
│   ├── StateManager.tsx
│   └── GraphTemplateBuilder.tsx
├── services/
│   └── api.ts               # API service
└── types/
    └── state-manager.ts     # TypeScript definitions
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Exosphere State Manager ecosystem.
