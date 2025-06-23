# `exospherehost/get-files`
Simply gets files from various cloud storage services to exospherehost for further processing. Currently supported services are:

- AWS S3
- Google Cloud Storage
- Azure Blob Storage
- Dropbox
- Google Drive
- OneDrive
- SFTP
- FTP

```yaml
# avilable in namespace `exospherehost/get-files`
uses: exospherehost/get-files

# define the sla of the satellite (6h, 12h, 24h)
# higher the sla, higher the discount on the cost
sla: 6h

# optional: name for human readable identifier
identifier: get-files

# retries: number of times to retry the satellite if it fails
# default: 3
retries: 5

# configuration for the satellite
config:
    # provider: provider of the file
    # required: true
    provider: aws-s3

    # root-path: root path of the file or folder to get
    folder-path: s3://my-bucket/my-folder

    # file-path: file path of the file to get
    file-path: s3://my-bucket/my-file.txt

    # recursive: whether to get the files recursively
    # default: false
    recursive: true

    # exclude-files: files to exclude from the get
    # default: []
    exclude-files:
        - s3://my-bucket/my-folder/my-file.txt
        - s3://my-bucket/my-folder/my-file2.txt

    # exclude-folders: folders to exclude from the get
    # default: []
    exclude-folders:
        - s3://my-bucket/my-folder/my-folder2

    # allowed extensions: extensions to include from the get
    # default: []
    allowed-extensions:
        - .txt
        - .pdf
        - .docx
        - .doc
        - .xls
        - .xlsx
        - .csv

    # blocked-extensions: extensions to exclude from the get
    # default: []
    blocked-extensions:
        - .exe
        - .dll
        - .so
        - .dylib
        - .lib
        
    # secrets: secrets to use for the satellite
    # depends on the provider of the file
    # required: true
    secrets:
        - AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
        - AWS_SECRET_KEY: ${{ secrets.AWS_SECRET_KEY }}
```