import boto3
import os

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
        aws_access_key_id: str = os.getenv("S3_ACCESS_KEY_ID")
        aws_secret_access_key: str = os.getenv("S3_SECRET_ACCESS_KEY")
        aws_region: str = os.getenv("S3_REGION")

    async def execute(self) -> List[Outputs]:
        print(self.inputs)

        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
            region_name=os.getenv("S3_REGION")
        )
        response = s3_client.list_objects_v2(Bucket=self.inputs.bucket_name, Prefix=self.inputs.prefix)

        return [
            self.Outputs(key=data['Key'])
            for data in response['Contents']
        ]
