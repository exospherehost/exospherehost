# Exosphere TypeScript SDK (unofficial)

TypeScript SDK mirroring the Python SDK concepts: upsert graphs, upsert node models, trigger runs, await completion, and stream events. Built for Node 18+ and modern bundlers.

## Install

```bash
npm install exosphere-ts-sdk
```

## Usage

```ts
import { ExosphereClient, StateManager, awaitRun, streamRunEvents } from "exosphere-ts-sdk";

const client = new ExosphereClient({ apiKey: process.env.EXOSPHERE_API_KEY! });
const sm = new StateManager(client, "hello-world");

// 1) Upsert a graph (Python parity)
await sm.upsert_graph({
  graph_name: "my-first-graph",
  graph_nodes: [
    {
      node_name: "MyFirstNode",
      namespace: "hello-world",
      identifier: "describe_city",
      inputs: { city: "initial" },
      next_nodes: [],
    },
  ],
  secrets: {},
});

// 2) Trigger a run
const { runId } = await sm.trigger("my-first-graph", { city: "World" });

// 3a) Poll until completion
const finalRun = await awaitRun(client, runId, { pollIntervalMs: 1000 });
console.log(finalRun.status, finalRun.output);

// 3b) Or stream events (Server-Sent Events)
await streamRunEvents(client, runId, (evt) => {
  console.log("event", evt.type, evt.data);
});
```

## Runtime and Event Loop

- All methods are `async` and non-blocking; they use Node's event loop correctly.
- Streaming uses the Fetch ReadableStream with an SSE parser; cancellation is supported via `AbortSignal`.

## Build

```bash
npm run build
```

## Node Support

- Requires Node 18+ (built-in `fetch`). Provide `fetchImpl` in the client options if you need a custom fetch.

## Disclaimer

This is an unofficial TypeScript SDK. Endpoints may need adjustment to match your Exosphere deployment.

![logo light](assets/logo-light.svg#gh-light-mode-only)
![logo dark](assets/logo-dark.svg#gh-dark-mode-only)

<p align="center">
  <a href="https://docs.exosphere.host"><img src="https://img.shields.io/badge/docs-latest-success" alt="Docs"></a>
  <a href="https://github.com/exospherehost/exospherehost/commits/main"><img src="https://img.shields.io/github/last-commit/exospherehost/exospherehost" alt="Last commit"></a>
  <a href="https://pypi.org/project/exospherehost/"><img src="https://img.shields.io/pypi/v/exospherehost" alt="PyPI - Version"></a>
  <a href="https://codecov.io/gh/exospherehost/exospherehost"><img src="https://img.shields.io/codecov/c/gh/exospherehost/exospherehost" alt="Coverage"></a>
  <a href="https://github.com/orgs/exospherehost/packages?repo_name=exospherehost"><img src="https://img.shields.io/badge/Kubernetes-native-326ce5?logo=kubernetes&logoColor=white" alt="Kubernetes"></a>
  <a href="https://discord.com/invite/zT92CAgvkj"><img src="https://badgen.net/discord/members/zT92CAgvkj" alt="Discord"></a>
  <a href="https://github.com/exospherehost/exospherehost"><img src="https://img.shields.io/github/stars/exospherehost/exospherehost?style=social" alt="Stars"></a>
  <a href="https://github.com/exospherehost/exospherehost/actions/workflows/integration-tests.yml?query=branch%3Amain"><img src="https://img.shields.io/github/actions/workflow/status/exospherehost/exospherehost/integration-tests.yml?branch=main" alt="Integration Tests (main)"></a>
</p>

---

# Exosphere: Distributed AI Workflow Infrastructure

**Exosphere** is an open-source, Kubernetes-native infrastructure platform designed to run distributed AI workflows and autonomous agents at scale. Built with Python and based on a flexible node-based architecture, Exosphere enables developers to create, deploy, and manage robust AI workflows that can handle large-scale data processing and long-running operations.

![Example Workflow Run](/assets/workflow-run.png)

## 🚀 What Exosphere Can Do

Exosphere provides a powerful foundation for building and orchestrating AI applications with these key capabilities:

### **Reliable AI Workflows at Scale**
- **Infinite Parallel Agents**: Run multiple AI agents simultaneously across distributed infrastructure
- **Dynamic State Management**: Create and manage state at runtime with persistent storage
- **Fault Tolerance**: Built-in failure handling and recovery mechanisms for production reliability
- **Core Concepts**: Fanout, Unite, Signals, Retry Policy, Store

### **Smooth Developer Experience**
- **Plug-and-Play Nodes**: Create reusable, atomic workflow components that can be mixed and matched
- **Python-First**: Native Python support with Pydantic models for type-safe inputs/outputs
- **Interactive Dashboard**: Visual workflow management, monitoring, and debugging tools

### **Production Ready Infrastructure**
- **Kubernetes Native**: Deploy seamlessly on Kubernetes clusters for enterprise-grade scalability
- **State Persistence**: Maintain workflow state across restarts and failures
- **API Integration**: Connect to external services and APIs through configurable nodes

### **Built for AI Agents**
- **Autonomous Execution**: Build agents that can make decisions and execute complex workflows
- **Data Processing**: Handle large datasets with distributed processing capabilities
- **Long-Running Operations**: Support for workflows that run for hours, days, or indefinitely

Whether you're building data pipelines, AI agents, or complex workflow orchestrations, Exosphere provides the infrastructure backbone to make your AI applications production-ready and scalable.

## 🎯 Use Cases & Applications

Exosphere is perfect for a wide range of AI and automation scenarios:

- **Data Processing & ETL Pipelines**
- **AI Agent Orchestration**
- **Content Generation & Analysis**
- **API Integration & Automation**

##  Architecture Overview

Exosphere is built on a flexible, node-based architecture that makes it easy to create complex workflows:

![Exosphere Architecture](assets/exosphere-concepts.png)

### **Core Components**

- **Nodes**: Atomic, reusable units of work that can be AI agents, API calls, data processors, or any custom logic
- **Runtime**: The execution environment that manages and orchestrates your nodes
- **State Manager**: Handles persistent state across workflow executions
- **Dashboard**: Visual interface for monitoring and managing workflows
- **Graphs**: Define the flow and dependencies between nodes

### **Key Concepts**

![Building blocks of Exosphere](assets/exosphere-components.png)

- **Fanout**: Distribute work across multiple parallel instances of a node
- **Unite**: Combine results from multiple parallel executions
- **Signals**: Inter-node communication and event handling
- **Retry Policy**: Configurable failure handling and recovery
- **Store**: Persistent storage for workflow state and data

### **Deployment Options**

- **Local Development**: Run with Docker Compose for quick setup
- **Kubernetes**: Production-ready deployment on K8s clusters
- **Cloud**: Deploy on any cloud provider with Kubernetes support

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Step 1: Installation

```bash
uv add exospherehost
```

### Step 2: Create Your First Node
   
   Each node is an atomic, reusable unit in Exosphere. Once registered, you can plug it into any workflow. Nodes can be AI agents, API calls, data processors, or any custom logic you want to execute.
   
   ```python
   from exospherehost import BaseNode
   from pydantic import BaseModel

   class CityAnalyzerNode(BaseNode):
       """A node that analyzes and describes a city using AI"""
       
       class Inputs(BaseModel):
           city: str
           analysis_type: str = "general"  # general, tourism, business, etc.

       class Outputs(BaseModel):
           description: str
           key_features: str
           score: str

       class Secrets(BaseModel):
           openai_api_key: str  # Optional: for AI-powered analysis

       async def execute(self) -> Outputs:
           # Your custom logic here - could be:
           # - AI agent calls
           # - API requests
           # - Data processing
           # - Database queries
           # - Any Python code!
           
           description = f"Analysis of {self.inputs.city}"
           features = ["culture", "economy", "lifestyle"]
           score = 8.5
           
           return self.Outputs(
               description=description,
               key_features=json.dumps(features),
               score=str(score)
           )
   ```

 

### Step 3: Create and Start the Runtime

Create the runtime and register your nodes:
  ```python
  from exospherehost import Runtime

  # Initialize the runtime with your nodes
  runtime = Runtime(
      name="city-analysis-runtime",
      namespace="my-project",
      nodes=[CityAnalyzerNode]
  )

  # Start the runtime (this will block the main thread)
  runtime.start()
  ```

  **Run your application:**
  ```bash
  uv run main.py
  ```

  Your runtime is now running and ready to process workflows! 🎉

### Step 4: Define Your First Graph
  
  Graphs can be defined using JSON objects or with the new model-based Python SDK (beta) for better type safety and validation. See [Graph definitions](https://docs.exosphere.host/exosphere/create-graph/) for more examples.



  ```python
  from exospherehost import StateManager, GraphNodeModel, RetryPolicyModel, RetryStrategyEnum

  async def create_graph():
      state_manager = StateManager(namespace="hello-world")
      
      graph_nodes = [
          GraphNodeModel(
              node_name="MyFirstNode",
              namespace="hello-world", 
              identifier="describe_city",
              inputs={"city": "initial"},
              next_nodes=[]
          )
      ]
      
      # Optional: Define retry policy (beta)
      retry_policy = RetryPolicyModel(
          max_retries=3,
          strategy=RetryStrategyEnum.EXPONENTIAL,
          backoff_factor=2000
      )
      
      # Create graph with model-based approach (beta)
      result = await state_manager.upsert_graph(
          graph_name="my-first-graph",
          graph_nodes=graph_nodes,
          secrets={},
          retry_policy=retry_policy  # beta
      )
  ```

## Quick Start with Docker Compose

Get Exosphere running locally in under 2 minutes:

```bash
# Option 1: With cloud MongoDB (recommended)
echo "MONGO_URI=your-mongodb-connection-string" > .env
curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose.yml
docker compose up -d

# Option 2: With local MongoDB (development)
curl -O https://raw.githubusercontent.com/exospherehost/exospherehost/main/docker-compose/docker-compose-with-mongodb.yml
docker compose -f docker-compose-with-mongodb.yml up -d
```

**Environment Configuration:**
- Docker Compose automatically loads `.env` files from the working directory
- Create your `.env` file in the same directory as your docker-compose file

Access your services:

- **Dashboard**: `http://localhost:3000`
- **API**: `http://localhost:8000`

> **📝 Note**: This configuration is for **development and testing only**. For production deployments, environment variable customization, and advanced configuration options, please read the complete **[Docker Compose Setup Guide](https://docs.exosphere.host/docker-compose-setup)**.

## 📚 Documentation & Resources

### **Essential Guides**
- **[Getting Started Guide](https://docs.exosphere.host/getting-started)**: Complete walkthrough for new users
- **[Docker Compose Setup](https://docs.exosphere.host/docker-compose-setup)**: Run Exosphere locally in minutes
- **[Architecture Guide](https://docs.exosphere.host/exosphere/architecture)**: Understand core concepts like fanout and unite
- **[Youtube Walkthroughs](https://www.youtube.com/@exospherehost)**: Step by step demos on Exosphere and how to build reliable flows with sample code.
- **[Featured Exosphere Projects](https://github.com/exospherehost/exosphereprojects)**: Templates on common projects on Exosphere, pull and run!

### **Advanced Topics**
- **[State Manager Setup](https://docs.exosphere.host/exosphere/state-manager-setup)**: Production deployment guide
- **[Dashboard Guide](https://docs.exosphere.host/exosphere/dashboard)**: Visual workflow management
- **[Graph Definitions](https://docs.exosphere.host/exosphere/create-graph/)**: Building complex workflows

### **Community & Support**
- **[Official Documentation](https://docs.exosphere.host)**: Complete reference and tutorials
- **[Discord Community](https://discord.com/invite/zT92CAgvkj)**: Get help and connect with other developers
- **[GitHub Issues](https://github.com/exospherehost/exospherehost/issues)**: Report bugs and request features
- **[PyPI Package](https://pypi.org/project/exospherehost/)**: Latest stable releases




## 🌟 Open Source Commitment

We believe that open source is the foundation of innovation and progress. Exosphere is our contribution to this movement, and we're committed to supporting the community in multiple ways:

### **Our Promise to the Community**

1. **🔄 Open Source First**: The majority of our codebase is open source and available to everyone
2. **💰 Giving Back**: A portion of our profits goes directly to supporting open source projects and communities
3. **🎓 Mentorship**: We actively collaborate with student programs to mentor the next generation of developers
4. **🤝 Community Driven**: We welcome contributions, feedback, and collaboration from developers worldwide

### **Get Involved**

- **Contributors**: Help us build the future of AI infrastructure
- **Users**: Your feedback shapes our roadmap and priorities  
- **Students**: Join our mentorship programs and grow your skills
- **Organizations**: Partner with us to advance open source AI tools

**Ready to make a difference?** Reach out to us at [nivedit@exosphere.host](mailto:nivedit@exosphere.host) and let's push the boundaries of what's possible together! 🚀

## 🎯 Ready to Get Started?

Exosphere is designed to make AI workflow development accessible, scalable, and production-ready. Whether you're building your first AI agent or scaling to thousands of parallel workflows, Exosphere provides the infrastructure you need.

### **Next Steps:**
1. **⭐ Star this repository** to show your support
2. **🚀 Try the quick start** with our Docker Compose setup
3. **💬 Join our Discord** community for help and discussions
4. **📖 Read the docs** for comprehensive guides and examples
5. **🤝 Contribute** to help us build the future of AI infrastructure

---

## Contributing

We welcome community contributions. For guidelines, refer to our [CONTRIBUTING.md](https://github.com/exospherehost/exospherehost/blob/main/CONTRIBUTING.md).

![exosphere.host Contributors](https://contrib.rocks/image?repo=exospherehost/exospherehost)



