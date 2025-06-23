# Satellite

Satellite is the core building blocks for exosphere. They are lego blocks designed for a specific purpose: you can connect them together to create complex systems in a matter of minutes without worrying about the underlying infrastructure.

They are pre-implemented serverless functions highly optimized for workflows and high volume batch processing, optimized for cost, reliability, developer velocity and ease of use. Our inhouse optimization for workflowss and batch processing can lead to significant cost savings, for example you can expect a cost per token saving of about 50-75% on LLMs like DeepSeek R1 70B, Gemma 3 27B, etc.

## How to use
There are multiple ways to use satellites and depends upon the interface provided by the satellite. Usually you can either use the satellite as a standalone function or you can use it as a part of a cluster (think a group or workflow of satellites for a specific purpose).

### Cluster based execution
Our model of satellite based execution delivers the best value when grouped together with multiple other satellites for a specific purpose. For example you can create a cluster of satellites to parse a resume, understand financial reports, generating synthetic data, and more.

To use with cluster you need pass satellite parameter to cluster `YML` file, API or SDK. For example to use `satellite/exospherhost/deepseek-r1-distrill-llama-70b` in a cluster you would need to pass the following to the cluster `YML` file:

```yaml
sla: "6h"
cluster:
    satellites:
      - name: DeepSeek R1 Distrill Llama 70B
        uses: satellite/exospherhost/deepseek-r1-distrill-llama-70b
        identifier: deepseek-r1-distrill-llama-70b
        config:
          max_tokens: 1000
          temperature: 0.5
        input:
          prompt: Hello, how are you?
```

Check cluster documentation for more details on how to use satellites in a cluster, further APIs and SDKs would be available soon.

### API based execution
Usually API based satellite singature would be something like this:
```curl
curl -X POST https://api.exosphere.host/v1/satellites/<unique-project-name>/<unique-satellite-name>/ \
-H "Authorization: <your-api-key>" \
-H "Content-Type: application/json" \
-d '{
  "input": {
    "prompt": "Hello, how are you?"
  },
  "config": {
    "max_tokens": 1000,
    "temperature": 0.5
  },
  "sla": "6h"
}'
```

This will return a JSON response with output schema as follows:
```json
{
    "execution_id": "<uuid-execution-id>",
    "sla": "6h",
    "status": "pending",
    "created_at": "<timestamp-creation>",
    "updated_at": "<timestamp-last-update>",
    "output": null,
    "error": null,
    "retries": 0
}
```

Further you can poll the status and result of the execution using API execution similar to this:

```curl
curl -X GET https://api.exosphere.host/v1/satellites/<unique-project-name>/<unique-satellite-name>/<uuid-execution-id>/ \
-H "Authorization: <your-api-key>"
-H "Content-Type: application/json"
```
this should return a JSON response with status and result of the execution, similar to this:
```json
{
    "execution_id": "<uuid-execution-id>",
    "sla": "6h",
    "status": "completed",
    "created_at": "<timestamp-creation>",
    "updated_at": "<timestamp-last-update>",
    "output": {
        "response": "Hello, how are you?"
    },
    "error": null,
    "retries": 0
}
```

### SDK based execution
We are working on SDKs for different programming languages to make it easier to use satellite like Python, JavaScript, Go, etc. These would be avilable soon on our [github](https://github.com/exospherehost) further on various package managers like `pip`, `npm`, `go get`, etc.

## Avilable Exosphere Satellites 
Following are the list of satellites which are currently avilable to `private-beta` developers.

| Satellite Name | Description | Documentation |
|----------------|-------------|---------------|
| `exospherehost/deepseek-r1-distrill-llama-70b` | Batch inference for DeepSeek R1 Distrill Llama 70B (upto 75% cost savings) | [Read more](./exospherehost/deepseek-r1-distrill-llama-70b.md) |
| `exospherehost/get-files` | Get files from cloud storages | [Read more](./exospherehost/get-files.md) |
| `exospherehost/parse-with-docling` | Parse documents with Docling (PDFs, Word, Images, etc) | [Read more](./exospherehost/parse-with-docling.md) |
| `exospherehost/call-webhook` | Call Webhook (POST, PUT, PATCH, GET, DELETE, etc) | [Read more](./exospherehost/call-webhook.md) |
| `exospherehost/forward-logs` | Forward logs to NewRelic, LogZ, Dynatrace etc. | [Read more](./exospherehost/forward-logs.md) |
| `exospherehost/move-file` | Move files within cloud storages (S3, GCS, etc) | [Read more](./exospherehost/move-file.md) |
| `exospherehost/send-alert ` | Send alert to Slack, PagerDuty, etc. | [Read more](./exospherehost/send-alert.md) |
| `exospherehost/send-email` | Send email (SMTP, SendGrid, SES, SendInBlue, etc) | [Read more](./exospherehost/send-email.md) |

## Types of Satellites
We are working on following broad types of satellites (Currently `exosphere-satellites` are only available to the `private-beta` users, we are working on making other categories of satellites available to the community):

#### `exosphere-satellites` 
These are the satellites which are built by exosphere team and are available to the community. Initially we will be focusing on building satellites for AI workflows and agents. These would be avilable under the namespace `satellite/exospherhost/<unique-satellite-name>` for example `satellite/exospherhost/deepseek-r1-distrill-llama-70b`.

#### `community-satellites`
These are the satellites which are built by the community and are available to the community. There would be avilable under the namespace `satellite/<unique-project-name>/<unique-satellite-name>` for example `satellite/aikinclub/parse-resume`. Developers would be able to create them using our ongoing work on `orbit` SDK, once verified and approved they would be avilable for the community to use. More details on `orbit` SDK, how to create these satellites and how to add to exosphere ecosystem would be available soon.

#### `custom-satellites`
These are the satellites which are built by the user and is avilable as per the permission boundry set by the user. These would also follow naming convention of `satellite/<unique-project-name>/<unique-satellite-name>` for example `satellite/aikinclub/send-whatsapp-message`, however only cluster/satellite running in the same namespace would be able to access these satellites. Similar to `community-satellites` developers would be able to create them using our ongoing work on `orbit` SDK, however they would be avilable within the project namespace and would not require any approval.

#### `configured-satellites`
These are the satellites with additional configuration added to the existing pre-implemented satellites or custom satellites. These would also follow naming convention of `satellite/<unique-project-name>/<unique-satellite-name>` for example `satellite/aikinclub/send-whatsapp-message`, however only cluster/satellite running in the same namespace would be able to access these satellites. Creating these would be much easier, essentially you would be able to create a new satellite by configuring an existing satellite through a simple UI or API call, details on how to do this would be available soon.