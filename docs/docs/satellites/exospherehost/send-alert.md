# `exospherehost/send-alert`
Sends alerts to your favorite alerting service, currently supported services are:
- PagerDuty
- Slack
- Discord

```yaml
# avilable in namespace `exospherehost/send-alert`
uses: exospherehost/send-alert

# define the sla of the satellite (6h, 12h, 24h)
# higher the sla, higher the discount on the cost
sla: 6h

# optional: name for human readable identifier
identifier: send-alert

# optional: Identifier for the satellite
# think of this like a variable name
config:
    # provider: provider of the alert
    # required: true
    provider: pagerduty

    secrets:
        # account-id: account id for the provider
        # required: true
        account-id: ${{ secrets.PAGERDUTY_ACCOUNT_ID }}

        # api-key: api key for the provider
        # required: true
        api-key: ${{ secrets.PAGERDUTY_API_KEY }}

        # service-key: service key for the provider
        # required: true
        service-key: ${{ secrets.PAGERDUTY_SERVICE_KEY }}
```