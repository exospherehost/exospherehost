# `exospherehost/deepseek-r1-distrill-llama-70b`
This satellite is designed for running DeepSeek R1 Distrill LLama 70B on ExosphereHost optimized for batch, high data throughput, and low cost (expect 50-75% cheaper inferencing as compared to platforms like Groq, TogetherAI).

Here are possible configurations available to you for this satellite:

```yaml
# available in namespace `exospherehost/deepseek-r1-distrill-llama-70b`
uses: exospherehost/deepseek-r1-distrill-llama-70b

# define the sla of the satellite (6h, 12h, 24h)
# higher the sla, higher the discount on the cost
sla: 6h

# optional: human readable name for the satellite
name: Say Hello World

# optional: unique identifier for the satellite
# think of this like a variable name
identifier: say-hello

# retries: number of times to retry the satellite if it fails
# default: 3
retries: 5

# configuration for the satellite
config:
    # temperature: temperature for the model
    # default: 0.5
    temperature: 0.5

    # max-tokens: maximum number of tokens to generate
    # default: 65,536
    max-tokens: 1024

    # output-format: format of the output, in built supported formats are:
    # - text
    # - json
    # default: text
    output-format: json

    # output-schema: schema for the output
    # default: null
    output-schema: |
        {
            "company": string, 
            "quarter": string,
            "year": string,
            "revenue": number,
            "net-income": number,
            "gross-profit": number,
            "operating-income": number,
        }

    input:
        prompt: Give me data in the format of the output-schema
        
        # alternatively, you can pass a chat history like this:
        messages:
            - role: user
              content: |
                What is the capital of France?
            - role: assistant
              content: |
                The capital of France is Paris.
            - role: user
              content: |
                What is the capital of Germany?
```