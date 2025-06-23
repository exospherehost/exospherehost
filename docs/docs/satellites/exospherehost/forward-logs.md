# `exospherehost/forward-logs`
Simply forward logs to your favorite logging service, currently supported services are:

- New Relic
- Datadog
- Sentry 
- Logz.io
- Kusto 
- CloudWatch

```yaml
# avilable in namespace `exospherehost/forward-logs`
uses: exospherehost/forward-logs

# define the sla of the satellite (6h, 12h, 24h)
# higher the sla, higher the discount on the cost
sla: 6h

# optional: name for human readable identifier
identifier: forward-logs

# optional: Identifier for the satellite
# think of this like a variable name
identifier: forward-logs

# retries: number of times to retry the satellite if it fails
# default: 3
retries: 5

# configuration for the satellite
config:
    # log-level: level of the log to forward
    # default: info
    log-level: info

    # provider: provider of the log
    # required: true
    provider: new-relic

    # account-id: account id for the provider
    # required: true
    account-id: ${{ secrets.NEW_RELIC_ACCOUNT_ID }}

    # api-key: api key for the provider
    # required: true
    api-key: ${{ secrets.NEW_RELIC_API_KEY }}

    # application-id: application id for the provider
    # required: true
    application-id: ${{ secrets.NEW_RELIC_APPLICATION_ID }}
```

Secrets can varry depending on the provider of your choice.