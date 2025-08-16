# Getting Started

Welcome to ExosphereHost! This guide will help you get started with building and deploying AI workflows using our open-source infrastructure platform.

## 🚀 Quick Overview

ExosphereHost is an infrastructure layer that simplifies building background AI workflows and agents. You can:

- **🛰️ Use Pre-built Satellites**: Access optimized AI functions with 50-75% cost savings
- **🌌 Create Clusters**: Combine satellites into powerful workflows
- **🐍 Build with Python SDK**: Create custom distributed applications
- **📊 Monitor Everything**: Real-time tracking and observability

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.12+** installed on your system
- **Basic understanding** of AI/ML workflows
- **API access** (currently in private beta)

## 🎯 Choose Your Path

Select the approach that best fits your needs:

### 🚀 Quick Start (5 minutes)
Perfect for trying out the platform with pre-built examples.

### 🛠️ SDK Development (15 minutes)
Build custom nodes and distributed applications.

### 🌌 Cluster Workflows (30 minutes)
Create complex multi-step AI workflows.

---

## 🚀 Quick Start

### Step 1: Get API Access

Currently, ExosphereHost is in **private beta**. To get access:

1. **Join our Discord**: [https://discord.gg/JzCT6HRN](https://discord.gg/JzCT6HRN)
2. **Request Beta Access**: Email us at [nivedit@exosphere.host](mailto:nivedit@exosphere.host)
3. **Follow us** for updates:
   - [Twitter: @exospherehost](https://x.com/exospherehost)
   - [LinkedIn: exospherehost](https://www.linkedin.com/in/nivedit-jain/)

### Step 2: Install the Python SDK

```bash
pip install exospherehost
```

### Step 3: Set Up Environment

```bash
export EXOSPHERE_STATE_MANAGER_URI="your-state-manager-uri"
export EXOSPHERE_API_KEY="your-api-key"
```

### Step 4: Run Your First Node

Create a file called `hello_exosphere.py`:

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel

class HelloNode(BaseNode):
    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        greeting: str

    async def execute(self) -> Outputs:
        return self.Outputs(greeting=f"Hello, {self.inputs.name}!")

# Start the runtime
Runtime(
    namespace="QuickStart",
    name="HelloWorld",
    nodes=[HelloNode]
).start()
```

Run it:
```bash
python hello_exosphere.py
```

🎉 **Congratulations!** You've created your first ExosphereHost node.

---

## 🛠️ SDK Development

### Creating Custom Nodes

Nodes are the building blocks of your distributed applications. Here's a more advanced example:

```python
from exospherehost import Runtime, BaseNode
from pydantic import BaseModel
import httpx
import json

class APIProcessorNode(BaseNode):
    class Inputs(BaseModel):
        api_url: str
        query: str

    class Outputs(BaseModel):
        response: str
        status: str

    class Secrets(BaseModel):
        api_key: str

    async def execute(self) -> Outputs:
        headers = {"Authorization": f"Bearer {self.secrets.api_key}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.inputs.api_url,
                headers=headers,
                json={"query": self.inputs.query}
            )
        
        return self.Outputs(
            response=json.dumps(response.json()),
            status="success" if response.status_code == 200 else "error"
        )

Runtime(
    namespace="MyProject",
    name="APIProcessor",
    nodes=[APIProcessorNode]
).start()
```

### Key Concepts

- **Inputs**: Define what data your node receives
- **Outputs**: Define what data your node returns
- **Secrets**: Securely manage API keys and credentials
- **Execute Method**: Contains your node's logic

### Best Practices

1. **Keep nodes stateless**: Each execution should be independent
2. **Handle errors gracefully**: Use try-catch blocks and return meaningful errors
3. **Use type hints**: Leverage Pydantic for data validation
4. **Serialize complex data**: All fields must be strings in v1

---

## 🌌 Cluster Workflows

Clusters combine multiple satellites into powerful workflows. Here's how to create one:

### Step 1: Create a Cluster YAML

Create `my-workflow.yml`:

```yaml
version: 0.0.1b

cluster:
  sla: 6h
  title: Document Processing Workflow
  description: Extract and analyze text from PDF documents
  identifier: my-project/document-processor
  
  trigger:
    api-call: true
  
  secrets:
    - AWS_ACCESS_KEY: "your-aws-access-key"
    - AWS_SECRET_KEY: "your-aws-secret-key"
    - OPENAI_API_KEY: "your-openai-api-key"
  
  satellites:
    - name: Get PDF Files
      uses: satellite/exospherehost/get-files-from-s3
      identifier: get-files
      config:
        bucket: my-documents
        prefix: pdfs/
        extension: pdf
        secrets:
          - AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
          - AWS_SECRET_KEY: ${{ secrets.AWS_SECRET_KEY }}
    
    - name: Extract Text
      uses: satellite/exospherehost/parse-pdf-with-docling
      identifier: extract-text
      config:
        language: en
        output-format: markdown-string
        extract-images: false
    
    - name: Analyze Content
      uses: satellite/exospherehost/deepseek-r1-distrill-llama-70b
      identifier: analyze-content
      config:
        temperature: 0.3
        max-tokens: 2000
        output-format: json
        output-schema: |
          {
            "summary": "string",
            "key_points": ["string"],
            "sentiment": "positive|negative|neutral",
            "topics": ["string"]
          }
      input:
        prompt: |
          Analyze the following document and provide a structured summary:
          ${{satellites.extract-text.output}}
    
    - name: Save Results
      uses: satellite/exospherehost/call-webhook
      identifier: save-results
      config:
        url: https://my-api.com/documents/analysis
        method: POST
        headers:
          - Content-Type: application/json
        body:
          - analysis: ${{satellites.analyze-content.output}}
            file_path: ${{satellites.get-files.output.file-path}}

  logs:
    satellites:
      - name: Forward Logs
        uses: satellite/exospherehost/forward-logs
        identifier: forward-logs
        config:
          destination: console
          log-level: info

  failure:
    from: extract-text
    satellites:
      - name: Send Alert
        uses: satellite/exospherehost/send-alert
        identifier: failure-alert
        config:
          type: email
          recipient: admin@mycompany.com
          subject: Document Processing Failed
        input:
          message: |
            Cluster ${{cluster.identifier}} failed at satellite ${{failure.satellite}}
            Error: ${{failure.error}}
```

### Step 2: Deploy the Cluster

```bash
# Using the API (when available)
curl -X POST https://api.exosphere.host/v1/clusters \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/yaml" \
  --data-binary @my-workflow.yml

# Using the Python SDK (coming soon)
from exospherehost import ClusterClient

client = ClusterClient(api_key="your-api-key")
cluster_id = await client.deploy_from_yaml("my-workflow.yml")
```

### Step 3: Monitor Execution

```bash
# Check cluster status
curl -X GET https://api.exosphere.host/v1/clusters/{cluster_id} \
  -H "Authorization: Bearer your-api-key"

# Trigger execution
curl -X POST https://api.exosphere.host/v1/clusters/{cluster_id}/trigger \
  -H "Authorization: Bearer your-api-key"
```

---

## 🛰️ Available Satellites

Here are some popular satellites you can use in your workflows:

### AI/ML Satellites
- `satellite/exospherehost/deepseek-r1-distrill-llama-70b` - Large language model inference
- `satellite/exospherehost/parse-pdf-with-docling` - PDF text extraction
- `satellite/exospherehost/image-classification` - Image analysis (coming soon)

### Data Satellites
- `satellite/exospherehost/get-files-from-s3` - Fetch files from S3
- `satellite/exospherehost/move-file` - Move files between storage systems
- `satellite/exospherehost/database-query` - Execute database queries (coming soon)

### Integration Satellites
- `satellite/exospherehost/call-webhook` - HTTP API calls
- `satellite/exospherehost/send-email` - Email notifications
- `satellite/exospherehost/send-alert` - Slack/Discord alerts

### Monitoring Satellites
- `satellite/exospherehost/forward-logs` - Log forwarding
- `satellite/exospherehost/collect-metrics` - Metrics collection (coming soon)

[View all available satellites →](satellites/index.md)

---

## 💡 Example Use Cases

### Document Processing Pipeline
Extract and analyze content from PDF documents with automatic categorization and storage.

### Data Ingestion Workflow
Fetch data from multiple sources, transform it, and load it into your data warehouse.

### AI Content Generation
Generate blog posts, social media content, or documentation using AI models.

### Automated Reporting
Create daily/weekly reports by aggregating data from various APIs and databases.

### Image Processing Pipeline
Batch process images with AI models for classification, object detection, or enhancement.

---

## 📚 Next Steps

Now that you've got the basics, explore these advanced topics:

1. **[Architecture Overview](architecture.md)** - Understand how ExosphereHost works
2. **[Satellite Documentation](satellites/index.md)** - Explore all available satellites
3. **[API Reference](api-server/swagger.md)** - Complete API documentation
4. **[Python SDK Guide](https://docs.exosphere.host/python-sdk)** - Advanced SDK usage
5. **[Best Practices](best-practices.md)** - Production deployment tips (coming soon)

## 🤝 Community & Support

- **💬 Discord**: [Join our community](https://discord.gg/JzCT6HRN)
- **📧 Email**: [nivedit@exosphere.host](mailto:nivedit@exosphere.host)
- **🐛 Issues**: [GitHub Issues](https://github.com/exospherehost/exospherehost/issues)
- **📖 Docs**: [Full Documentation](https://docs.exosphere.host)

## 🎯 Beta Program

We're actively looking for early adopters and design partners! If you're interested in:

- **Building AI workflows** at scale
- **Contributing** to open source infrastructure
- **Providing feedback** on the platform
- **Collaborating** on new features

Please reach out to us! We'd love to work with you.

---

**Ready to build the future of AI infrastructure? Let's get started! 🚀**