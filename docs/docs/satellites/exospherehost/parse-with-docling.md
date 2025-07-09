# `exospherehost/parse-with-docling`
This satellite is designed to parse documents with Docling, a powerful document parsing library to get structured data from documents. 

```yaml
# available in namespace `exospherehost/parse-with-docling`
uses: exospherehost/parse-with-docling

# define the sla of the satellite (6h, 12h, 24h)
# higher the sla, higher the discount on the cost
sla: 6h

# optional: name for human readable identifier
identifier: parse-with-docling

# optional: Identifier for the satellite
# think of this like a variable name
identifier: parse-with-docling

# retries: number of times to retry the satellite if it fails
# default: 3
retries: 5

# configuration for the satellite
config:
    # file-path: file path of the file to parse
    # required: true
    file-path: s3://my-bucket/my-file.txt

    # output-format: format of the output
    # default: json
    output-format: markdown
```