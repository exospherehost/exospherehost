import boto3
from exospherehost import BaseNode
from typing import List
from pydantic import BaseModel


class ListS3FilesNode(BaseNode):

    class Inputs(BaseModel):
        bucket_name: str
        prefix: str = ''
        files_only: bool = False
        recursive: bool = False

    class Outputs(BaseModel):
        key: str

    class Secrets(BaseModel):
        aws_access_key_id: str
        aws_secret_access_key: str
        aws_region: str

    async def execute(self) -> List[Outputs]:

        s3_client = boto3.client(
            's3',
            aws_access_key_id=self.secrets.aws_access_key_id,
            aws_secret_access_key=self.secrets.aws_secret_access_key,
            region_name=self.secrets.aws_region
        )
        response = s3_client.list_objects_v2(Bucket=self.inputs.bucket_name, Prefix=self.inputs.prefix)

        return [
            self.Outputs(key=data['Key'])
            for data in response['Contents']
        ]
