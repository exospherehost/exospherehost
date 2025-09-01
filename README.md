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
</p>

---

Exosphere is open source infrastructure to run AI agents at scale for large data and long running flows.

Exosphere lets you define plug and playable nodes that can then be run on a reliable backbone in the form of a workflow, with:
- Dynamic State Creation at runtime
- Infinite parallel agents 
- Persistent state management
- Failure handling

This allows developers to deploy production agents that can scale beautifully to build robust autonomous AI workflows.



## Getting Started

- ### Installation
  ```bash
  uv add exospherehost
  ```

- ### Define your first node
   Each node is an atomic reusable unit on Exosphere. Once registered, you can plug it into any workflow going forward. This could be an agent, an api call, or existing code, anything you want to be a unit of your workflow. 
  ```python
    from exospherehost import BaseNode
    from pydantic import BaseModel

    class MyFirstNode(BaseNode):

        class Inputs(BaseModel):
            city:str
            #Define inputs taken by node

        class Outputs(BaseModel):
            description:str
            #Output fields from this node            

        async def execute(self) -> Outputs:    
            return Outputs(descriptor_agent(self.inputs.city))        
            #Execution function:
            # >>Agent
            # >>Existing Code
            # >>Anything else you want to do!
  ```

 

  Create the node and add it to a runtime to enable execution:
  ```python
  from exospherehost import Runtime

  Runtime(
    name="my-first-runtime",
    namespace="hello-world",
    nodes=[
       MyFirstNode
    ]
   ).start()
  ```

- ### Define your first graph
  
  Graphs are then described connecting nodes with relationships in json objects. Exosphere runs graph as per defined trigger conditions. See [Graph definitions](https://docs.exosphere.host/exosphere/create-graph/) to see more examples.
  ```json
  {
    "secrets": {},
    "nodes": [
        {
            "node_name": "MyFirstNode",
            "namespace": "hello-world",
            "identifier": "describe_city",
            "inputs": {
                "bucket_name": "initial",
                "prefix": "initial",
                "files_only": "true",
                "recursive": "false"
            },
            "next_nodes": []
        }
    ]
  }
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

> **⚠️ Security Note**: Variables prefixed with `NEXT_PUBLIC_` are embedded in client bundles and visible to browsers. Never store real secrets in `NEXT_PUBLIC_` variables - use server-side environment variables instead.

Access your services:

- **Dashboard**: `http://localhost:3000`
- **API**: `http://localhost:8000`

> **📝 Note**: This configuration is for **development and testing only**. For production deployments, environment variable customization, and advanced configuration options, please read the complete **[Docker Compose Setup Guide](https://docs.exosphere.host/docker-compose-setup)**.

## Documentation

For comprehensive documentation and guides, check out:

- **[Docker Compose Setup](https://docs.exosphere.host/docker-compose-setup)**: Complete guide for running Exosphere locally with Docker Compose.
- **[Getting Started Guide](https://docs.exosphere.host/getting-started)**
- **[State Manager Setup Guide](https://docs.exosphere.host/exosphere/state-manager-setup)**: Step-by-step instructions for running the Exosphere backend locally or in production.
- **[Dashboard Guide](https://docs.exosphere.host/exosphere/dashboard)**: Learn how to set up and use the Exosphere web dashboard.
- **[Architecture](https://docs.exosphere.host/exosphere/architecture)**: Understand core ideas on building graphs like fanout and unite.

You can also visit the [official documentation site](https://docs.exosphere.host) for the latest updates and more resources.




## Open Source Commitment

We believe that humanity would not have been able to achieve the level of innovation and progress we have today without the support of open source and community, we want to be a part of this movement and support the open source community. In following ways: 

1. We will be open sourcing majority of our codebase for exosphere.host and making it available to the community. We welcome all sort of contributions and feedback from the community and will be happy to collaborate with you.
2. For whatever the profits which we generate from exosphere.host, we will be donating a portion of it to open source projects and communities. If you have any questions, suggestions or ideas.
3. We would be further collaborating with various open source student programs to provide with the support and encourage and mentor the next generation of open source contributors.

Please feel free to reach out to us at [nivedit@exosphere.host](mailto:nivedit@exosphere.host). Lets push the boundaries of possibilities for humanity together!


## Contributing

We welcome community contributions. For guidelines, refer to our [CONTRIBUTING.md](https://github.com/exospherehost/exospherehost/blob/main/CONTRIBUTING.md).

![exosphere.host Contributors](https://contrib.rocks/image?repo=exospherehost/exospherehost)



