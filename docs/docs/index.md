# Introduction

## Vision
> Our vision is a world where creators and innovators can fully dedicate themselves to crafting extraordinary products and services, unburdened by the complexities of the underlying infrastructure. We foresee a future where intelligent systems seamlessly operate behind the scenes, tackling intricate, high-scale challenges with immense computational demands and vast data movements.

To realize this, we are pioneering an open-source infrastructure layer for background AI workflows and agents that is robust, affordable, and effortless to use, empowering the scalable solutions and transformative tasks of today, tomorrow, and beyond.

## Core Concepts

To have an intution of the first version of the platform, we would highly recommend watching the video below, this explains using our cluster apis with YML input, we are working on more modalities like pythonic control systems.

<a href="https://www.youtube.com/watch?v=tfVYXpjyGqQ" target="_blank">
  <img src="assets/cluster-api-yt.png" alt="Cluster API YT">
</a>

### Satellite

Satellites are the core building blocks for exosphere.They are lego blocks designed for a specific purpose: you can connect them together to create complex systems in a matter of minutes without worrying about the underlying infrastructure.

They are pre-implemented serverless functions highly optimized for workflows and high volume batch processing, optimized for cost, reliability, developer velocity and ease of use.

Our inhouse optimization for workflowss and batch processing can lead to significant cost savings, for example you can expect a cost per token saving of about 50-75% on LLMs like DeepSeek R1 70B, Gemma 3 27B, etc.

Each of these satellites must satisfy the following properties:

1. Should be idempotent and stateless.
2. Should have a unique identifier of the format `satellite/unique-project-name/satellite-name`, example: `satellite/exospherehost/deepseek-r1-distrill-llama-70b`
3. Should take a `config` parameter as an `object` to control or modify the behaviour.
4. Should be totally independent of any other satellite.
5. Should return a `list` of `objects`.
6. Should have following necessary fields: `parents`, `children`, `identifier`, `status`, `retries`, `delay`. Most of these fields are optional are set by the platform itself.
7. Should provide a clean interface for the user to check the status of the satellite and get output data.

Further work is being done to allow users to bring their own satellites and use our core infrastructure to manage their lifecycle.

### Cluster

A Cluster is a collection of satellites connected together to form a complete workflow: a series of satellities working togehter to achieve a common goal.

Each of these clusters must satisfy the following properties:

1. Should be a collection of satellites that are connected together to form a system.
2. Should have a unique identifier of the format `cluster/unique-project-name/cluster-name`, example: `cluster/aikin/structured-json`
3. Should define a necessary parameter of `SLA` denoating the maximum time to complete the cluster, **higher the SLA, lower the cost** as systems have more time to optimize for the task (currently supported: `6h`, `12h`, `24h`)
4. Should have a necessary `trigger` parameter to start the cluster, this can be a `cron` expression, or an `api-call` or other possible events.
5. Each cluster can also define `logs` parameter to configure log forwarding to a specific destination like `NewRelic`, `Kusto`, `CloudWatch` or any other logging service.
6. Each cluster can also define `failure` steps to handle the cluster in case of failure, this could again be a set of satellites to run in case of failure.

Developers can define their own clusters using our cluster api, which supports cluster creation, deletion, status, logs and other operations. Currently we are supporting cluster creation through `YML` files or our APIs and SDKs.

### Orbit

Orbit is the core compute platfrom capable of managing the lifecycle of satellites and clusters optimally across multiple computes including GPUs, CPUs, and other hardware. Further allowing developers to write their own satellites and plug-in with our core exosphere platform.

## Example

Here is an example of using our cluster api to create a satellite cluster to get structured json from PDF files of quaterly financial reports. The workflow in the image could be represented as the `YML` file below.

![Example Workflow](assets/example-workflow.png)
```yaml title="structured-json-deepseek.yml"
# define the version of the exosphere apis
version: 0.0.1b

# using cluster api to create the cluster
cluster: 
  # maximum allowed to compute the cluster
  # define the sla of the cluster (6h, 12h, 24h)
  sla: 6h 

  # define the name and description of the cluster for better understanding (optional)
  title: Structured JSON from Quarterly Financial Reports
  description: This cluster will take a list of PDF files from S3 and return a structured JSON output.

  # define the identifier of the cluster (project-name/cluster-name)
  identifier: aikin/strucutred-pdfs

  # trigger for the cluster
  trigger: 
    cron: "0 0 * * *"

  # define retries for each satellite, default is 5
  retries: 3

  # define the secrets for the cluster, these are stored in a secure vault and only excessible by allowed satellites in this cluster
  # still be sure to have minimum required permissions for each secret to avoid any security issues
  secrets:
    - AWS_ACCESS_KEY: "your-aws-access-key"
    - AWS_SECRET_KEY: "your-aws-secret-key"
    - API_BEARER_TOKEN: "your-api-bearer-token"
    - NEW_RELIC_ACCOUNT_ID: "your-new-relic-account-id"
    - NEW_RELIC_API_KEY: "your-new-relic-api-key"
    - NEW_RELIC_APPLICATION_ID: "your-new-relic-application-id"
    - FAILURE_S3_AWS_ACCESS_KEY: "your-failure-s3-aws-access-key"
    - FAILURE_S3_AWS_SECRET_KEY: "your-failure-s3-aws-secret-key"
  
  # satellites in order to execute, each satellite returns a list of objects hence computational graph is formed and is executed in parallel.
  satellites:
    - name: Get files from S3
      uses: satellite/exospherehost/get-files-from-s3
      identifier: get-files-from-s3
      config:
        bucket: aikin-financial-reports
        prefix: sec
        recursive: true
        extension: pdf
        secrets:
          - AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
          - AWS_SECRET_KEY: ${{ secrets.AWS_SECRET_KEY }}

    - name: Extract text from PDF
      uses: satellite/exospherehost/parse-pdf-with-docling
      identifier: parse-pdf-with-docling
      config: 
        language: en
        output-format: markdown-string
        extract-images: false

    - name: Get structured json from markdown using DeepSeek
      uses: satellite/exospherehost/deepseek-r1-distrill-llama-70b
      identifier: deepseek-r1-distrill-llama-70b
      retries: 5
      config:
        temperature: 0.5
        max-tokens: 1024
        output-format: json
        output-schema: |
            {
                "company": string, 
                "quarter": string,
                "year": string,
                "revenue": number,
                "net-income": number,
                "gross-profit": number,
                "operating-income": number,
                "net-income-margin": number,
                "gross-profit-margin": number,
                "operating-income-margin": number,
            }
      input:
        prompt: |
            Parse the following quarterly financial report and returnt a structured json output as defined in the output-schema, report text is provided below:
            ${{satellites.parse-pdf-with-docling.output}}

    - name: Call Webhook to send the structured json to aikin api
      uses: satellite/exospherehost/call-webhook
      identifier: call-webhook
      config:
        url: https://api.aikin.com/v1/financial-reports
        method: POST
        headers:
          - Authorization: Bearer ${{ secrets.API_BEARER_TOKEN }}
        body:
          - data: ${{satellites.deepseek-r1-distrill-llama-70b.output}}
            file-path: $${{satellites.get-files-from-s3.output.file-path}}

    - name: Delete success file from S3
      uses: satellite/exospherehost/delete-file-from-s3
      identifier: delete-file-from-s3
      config:
        bucket: aikin-financial-reports
        file-path: $${{satellites.get-files-from-s3.output.file-path}}
        secrets:
            - AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
            - AWS_SECRET_KEY: ${{ secrets.AWS_SECRET_KEY }}


  # define steps to handle logs for this cluster
  logs:
    satellites:
        - name: Send logs to NewRelic
          uses: satellite/exospherehost/send-logs-to-new-relic
          identifier: send-logs-to-new-relic
          config:
            account-id: ${{ secrets.NEW_RELIC_ACCOUNT_ID }}
            api-key: ${{ secrets.NEW_RELIC_API_KEY }}
            application-id: ${{ secrets.NEW_RELIC_APPLICATION_ID }}
            log-level: info

  # define steps to handle failure for this cluster
  failure:
    # run from failured steps from this satellite
    from: parse-pdf-with-docling
    
    satellites:
         - name: Move to failure bucket
            uses: satellite/exospherehost/move-file
            identifier: move-to-failure-bucket
            config:
              origin-source: s3
              origin-bucket: aikin-financial-reports-failure
              origin-file-path: $${{satellites.get-files-from-s3.output.file-path}}
              destination-source: s3
              destination-bucket: aikin-financial-reports-failure
              destination-file-path: failed/quaterly-financial-reports/$${{satellites.get-files-from-s3.output.file-name}}
              secrets:
                  - ORIGIN_AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
                  - ORIGIN_AWS_SECRET_KEY: ${{ secrets.AWS_SECRET_KEY }}
                  - DESTINATION_AWS_ACCESS_KEY: ${{ secrets.FAILURE_S3_AWS_ACCESS_KEY }}
                  - DESTINATION_AWS_SECRET_KEY: ${{ secrets.FAILURE_S3_AWS_SECRET_KEY }}
        - name: Send failure notification on PagerDuty
          uses: satellite/exospherehost/send-pagerduty-alert
          identifier: send-pagerduty-alert
          config:
            pagerduty-api-key: ${{ secrets.PAGERDUTY_API_KEY }}
            pagerduty-service-id: ${{ secrets.PAGERDUTY_SERVICE_ID }}
          input:
              message: |
                Cluster ${{cluster.identifier}} failed at ${{cluster.trigger}} for file $${{satellites.get-files-from-s3.output.file-path}}  with error ${{satellites.get-files-from-s3.output.error}}, file has been moved to failure bucket with path $${{satellites.move-to-failure-bucket.output.file-uri}}
```

This could also be represented as a pythonic control using our SDK/APIs, checkout [documentation](https://docs.exosphere.host) for more details.

## Open Source Commitment

We believe that humanity would not have been able to achieve the level of innovation and progress we have today without the support of open source and community, we want to be a part of this movement and support the open source community. In following ways: 

1. We will be open sourcing majority of our codebase for exosphere.host and making it available to the community. We welcome all sort of contributions and feedback from the community and will be happy to collaborate with you.
2. For whatever the profits which we generate from exosphere.host, we will be donating a portion of it to open source projects and communities. If you have any questions, suggestions or ideas.
3. We would be further collaborating with various open source student programs to provide with the support and encourage and mentor the next generation of open source contributors.

Please feel free to reach out to us at [nivedit@exosphere.host](mailto:nivedit@exosphere.host). Lets push the boundaries of possibilities for humanity together!

## Contributing

We welcome community contributions. For guidelines, refer to our [CONTRIBUTING.md](https://github.com/exospherehost/exospherehost/blob/main/CONTRIBUTING.md).

![exosphere.host Contributors](https://contrib.rocks/image?repo=exospherehost/exospherehost)

## Star History

<a href="https://www.star-history.com/#exospherehost/exospherehost&Date" target="_blank">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=exospherehost/exospherehost&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=exospherehost/exospherehost&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=exospherehost/exospherehost&type=Date" />
 </picture>
</a>
