# `exospherehost/call-webhook`
Call webhooks using HTTP methods (GET, POST, PUT, PATCH, DELETE) to external APIs and services.

```yaml
# available in namespace `exospherehost/call-webhook`
uses: exospherehost/call-webhook

# define the sla of the satellite (6h, 12h, 24h)
# higher the sla, higher the discount on the cost
sla: 6h

# optional: human readable name for the satellite
name: Call External API

# optional: unique identifier for the satellite
# think of this like a variable name
identifier: call-webhook

# retries: number of times to retry the satellite if it fails
# default: 3
retries: 5

# configuration for the satellite
config:
    # url: the webhook URL to call
    # required: true
    url: https://api.example.com/webhook

    # method: HTTP method to use
    # default: POST
    # options: GET, POST, PUT, PATCH, DELETE
    method: POST

    # headers: HTTP headers to include in the request
    # default: {}
    headers:
        - Content-Type: application/json
        - Authorization: Bearer ${{ secrets.API_TOKEN }}

    # timeout: request timeout in seconds
    # default: 30
    timeout: 60

    # follow_redirects: whether to follow HTTP redirects
    # default: true
    follow_redirects: true

    # verify_ssl: whether to verify SSL certificates
    # default: true
    verify_ssl: true

input:
    # body: request body (for POST, PUT, PATCH methods)
    # default: null
    body:
        key: value
        data: ${{ satellites.previous-satellite.output }}

    # query_params: query parameters for GET requests
    # default: {}
    query_params:
        param1: value1
        param2: value2

    # form_data: form data for POST requests
    # default: {}
    form_data:
        field1: value1
        file: ${{ satellites.file-upload.output }}

```