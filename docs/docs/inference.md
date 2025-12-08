# Inference APIs

## Overview
Exosphere provides a single inference API that adapts to your volume, SLA, and cost constraints. Designed for reliable volume inference, it enables you to run inference on any number of tokens with automatic sharding, batching, rate limiting and cost management. All APIs are flexible SLA such that you can choose your SLA window and data volume to optimize cost and performance. Cost in percentage (calculated based on the combination of SLA and data volume) of base price could be up to 70% less.

## Infer APIs
You can use the following inference APIs to run inference on your data:

### `POST /v0/infer/`
This is the main API for running inference. This will send your data to the inference engine and start the inference process. Example request:
```json
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
        "price_factor": 0.3
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
