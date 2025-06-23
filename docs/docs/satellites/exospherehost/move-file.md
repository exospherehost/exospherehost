# `exospherehost/move-file`
Very similar to `exospherehost/get-files` but instead of getting files, it moves files from one location to another, all support for get-files is also supported for move-file.

```yaml
# avilable in namespace `exospherehost/move-file`
uses: exospherehost/move-file

# define the sla of the satellite (6h, 12h, 24h)
# higher the sla, higher the discount on the cost
sla: 6h

# optional: name for human readable identifier
identifier: move-file

# optional: Identifier for the satellite
# think of this like a variable name
identifier: move-file

# retries: number of times to retry the satellite if it fails
# default: 3
retries: 5

# configuration for the satellite
config:
    # source provider: provider of the file
    # required: true
    source-provider: aws-s3

    # source-file-path: file path of the file to move
    # required: true
    source-file-path: s3://my-bucket/my-file.txt

    # destination provider: provider of the file
    # required: true
    destination-provider: aws-s3

    # destination-file-path: file path of the file to move
    # required: true
    destination-file-path: s3://my-bucket/my-file.txt

    # secrets: secrets to use for the satellite
    # required: true
    secrets:
        - SOURCE_AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
        - SOURCE_AWS_SECRET_KEY: ${{ secrets.AWS_SECRET_KEY }}
        - DESTINATION_AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
        - DESTINATION_AWS_SECRET_KEY: ${{ secrets.AWS_SECRET_KEY }}
```