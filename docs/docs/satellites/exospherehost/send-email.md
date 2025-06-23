# `exospherehost/send-email`
Send emails using SMTP or any of the supported email providers, including:
- SMTP
- SES
- Mailgun

```yaml
# avilable in namespace `exospherehost/send-email`
uses: exospherehost/send-email

# define the sla of the satellite (6h, 12h, 24h)
# higher the sla, higher the discount on the cost
sla: 6h

# optional: name for human readable identifier
identifier: send-email

# optional: Identifier for the satellite
# think of this like a variable name
identifier: send-email

# retries: number of times to retry the satellite if it fails
# default: 3
retries: 5

# configuration for the satellite
config:
    # provider: provider of the email
    # required: true
    provider: smtp

    # secrets: secrets to use for the satellite
    # required: true
    secrets:
        - SMTP_HOST: ${{ secrets.SMTP_HOST }}
        - SMTP_PORT: ${{ secrets.SMTP_PORT }}
        - SMTP_USER: ${{ secrets.SMTP_USER }}
        - SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}

input:
    # to: email address to send the email to
    to: john.doe@example.com

    # subject: subject of the email
    # required: true
    subject: Hello, world!

    # body: body of the email
    # required: true
    body: This is a test email

    # attachments: attachments to send with the email
    # default: []
    attachments:
        - s3://my-bucket/my-file.txt
        - s3://my-bucket/my-file2.txt

    # cc: cc email addresses
    # default: []
    cc:
        - jane.doe@example.com

    # bcc: bcc email addresses
    # default: []
    bcc:
        - jane.doe@example.com

    # reply-to: reply to email address
    # default: null
    reply-to: john.doe@example.com
```