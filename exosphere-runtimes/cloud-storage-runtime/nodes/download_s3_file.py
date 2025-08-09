import boto3
from exospherehost import BaseNode
from pydantic import BaseModel


class DownloadS3FileNode(BaseNode):

    class Inputs(BaseModel):
        bucket_name: str
        key: str

    class Outputs(BaseModel):
        file_path: str

    class Secrets(BaseModel):
        aws_access_key_id: str
        aws_secret_access_key: str
        aws_region: str

    async def execute(self) -> Outputs:

        s3_client = boto3.client(
            's3',
            aws_access_key_id=self.secrets.aws_access_key_id,
            aws_secret_access_key=self.secrets.aws_secret_access_key,
            region_name=self.secrets.aws_region
        )

        file_name = self.inputs.key.split('/')[-1]

        s3_client.download_file(self.inputs.bucket_name, self.inputs.key, file_name)

        return self.Outputs(file_path=self.outputs.file_path)
