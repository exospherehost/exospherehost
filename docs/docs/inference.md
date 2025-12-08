# Inference APIs

## Overview
Exosphere provides a single inference API that adapts to your volume, SLA, and cost constraints. Designed for reliable volume inference, it enables you to run inference on any number of tokens with automatic sharding, batching, rate limiting and cost management. All APIs are flexible SLA such that you can choose your SLA window and data volume to optimize cost and performance. Cost in percentage (calculated based on the combination of SLA and data volume) of base price could be up to 70% less.

## Infer APIs
You can use the following inference APIs to run inference on your data:

### `POST /v0/infer/`
This is the main API for running inference. This will send your data to the inference engine and start the inference process. Example request:
```bash
curl -X POST https://models.exosphere.host/v0/infer/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-api-key>" \
  -d '[
    {
        "sla": 60, // minutes
        "model": "deepseek:r1-32b", // model name
        "input": "Hello model, how are you?"
    },
    {
        "sla": 1440, // 1 day 
        "model": "openai:gpt-4o", // model name
        "input": "Hello OpenAI, how are you?"
    }
  ]'
```
Example response:
```json
{
    "status": "submitted",
    "task_id": "2f92fc35-07d6-4737-aefa-8ddffd32f3fc",
    "total_items": 2,
    "objects":[
        {
        "status": "submitted",
        "usage": {
            "input_tokens": 10,
            "price_factor": 0.3
        },
        "object_id": "63bb0b28-edfe-4f5b-9e05-9232f63d76ec"
        },
        {
            "status": "submitted",
            "usage": {
                "input_tokens": 10,
                "price_factor": 0.5
            },
            "object_id": "88d68bc3-643c-4251-a003-6c2c14f76649"
        }
    ]
}
```
You can track the complete task status using the `GET /v0/infer/task/{task_id}` API or you can track individual object status using the `GET /v0/infer/object/{object_id}` API.

### `GET /v0/infer/task/{task_id}/`
This API is used to track the complete task status. Example request:
```bash
curl -X GET https://models.exosphere.host/v0/infer/task/2f92fc35-07d6-4737-aefa-8ddffd32f3fc \
  -H "Authorization: Bearer <your-api-key>"
```
Example response:
```json
{
    "status": "submitted",
    "task_id": "2f92fc35-07d6-4737-aefa-8ddffd32f3fc",
    "total_items": 2,
    "objects": [
        {
            "object_id": "63bb0b28-edfe-4f5b-9e05-9232f63d76ec",
            "status": "completed",
            "usage": {
                "input_tokens": 10,
                "price_factor": 0.3,
                "output_tokens": 11
            },
            "output": {
                "type": "text",
                "text": "Hey user, I am doing great! How about you?"
            }
        },
        {
            "object_id": "88d68bc3-643c-4251-a003-6c2c14f76649",
            "status": "submitted",
            "usage": {
                "input_tokens": 10,
                "price_factor": 0.5
            }
        }
    ]
}
```

### `GET /v0/infer/object/{object_id}/`
This API is used to track the status of an individual object. Example request:
```bash
curl -X GET https://models.exosphere.host/v0/infer/object/63bb0b28-edfe-4f5b-9e05-9232f63d76ec \
  -H "Authorization: Bearer <your-api-key>"
```
Example response:
```json
{
    "object_id": "63bb0b28-edfe-4f5b-9e05-9232f63d76ec",
    "status": "completed",
    "usage": {
        "input_tokens": 10,
        "price_factor": 0.3,
        "output_tokens": 11
    },
    "error": null,
    "output": {
        "type": "text",
        "text": "Hey user, I am doing great! How about you?"
    }
}
```

- The output is only available when the item is completed. If no SLA is provided, the item will be completed immediately and the output will be available immediately. 

- The price factor is a multiplier for the base price of the model. It is used to calculate the cost of the item.

- The object_id is a unique identifier for the object. It is used to track the status of the object. In case of any failure individual object status will be available to track the failure. 

> **Note**: Auto retry policy will be triggered for transient failures without any additional cost.

Exosphere inference APIs also supports the standard batch inference API format used by OpenAI, Gemini, and other providers. You can upload a JSONL file containing multiple inference requests, similar to OpenAI's batch API format and pass the file to `/infer/` API.

### `PUT /v0/files/`
This API is used to upload a file to the server. Example request:
```bash
curl -X PUT https://models.exosphere.host/v0/files/mydata.jsonl \
  -H "Authorization: Bearer <your-api-key>" \
  -F file="@mydata.jsonl"
```
Example response:
```json
{
    "file_id": "ae0b977c-76a0-4d71-81a5-05a6d8844852",
    "file_name": "mydata.jsonl",
    "bytes": 1000,
    "mime_type": "application/jsonl"
}
```

expected file content should like:
```jsonl
{"key": "object-1", "request": {"contents": [{"parts": [{"text": "Describe the process of photosynthesis."}]}], "generation_config": {"temperature": 0.7}, "model": "deepseek:r1-32b"}}
{"key": "object-2", "request": {"contents": [{"parts": [{"text": "What are the main ingredients in a Margherita pizza?"}]}], "generation_config": {"temperature": 0.7}, "model": "openai:gpt-4o"}}
```

Now you can pass the file_id to the `/infer/` API to run inference on the file. Example request:
```bash
curl -X POST https://models.exosphere.host/v0/infer/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-api-key>" \
  -d '[
    {
        "file_id": "ae0b977c-76a0-4d71-81a5-05a6d8844852",
        "sla": 60
    }
  ]'
```

You can further request outputs as a file by pass the header `Output-Format: jsonl` to the API. Example request:
```bash
curl -X POST https://models.exosphere.host/v0/infer/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Output-Format: jsonl" \
  -d '[
    {
        "file_id": "ae0b977c-76a0-4d71-81a5-05a6d8844852",
        "sla": 60
    }
  ]'
```
Example response:
```json
{
    "status": "completed",
    "task_id": "2f92fc35-07d6-4737-aefa-8ddffd32f3fc",
    "total_items": 2,
    "output_url": "https://files.exosphere.host/v0/files/ae0b977c-76a0-4d71-81a5-05a6d8844852.jsonl"
}
```

You can download the output file from the `output_url` and the content should like:
```jsonl
{"key": "object-1", "output": {"type": "text", "text": "Photosynthesis is the process by which plants, algae, and some bacteria convert light energy into chemical energy."}}
{"key": "object-2", "output": {"type": "text", "text": "The main ingredients in a Margherita pizza are tomato sauce, mozzarella cheese, and basil."}}
```