import boto3
from botocore.config import Config

# 替换为您的实际凭证和信息
access_key = '4a3ae5e34c62c43a19589a5be458b3f7'
secret_key = '6580fc09574ea39f490e8de1c14fbe25ddd5958242c7688aa1595fad79e2c29c'
account_id = '210969bd7f5c7272e953db8ceaa775a7'
bucket_name = 'epub'
endpoint_url = f'https://{account_id}.r2.cloudflarestorage.com'

api_key = '2XrP9lE6iGkbn6Y3xNMEucBTN7njZGwPYLmnMYFA'

# 配置 S3 客户端
s3_client = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    config=Config(signature_version='s3v4')
)
response = s3_client.list_objects_v2(Bucket=bucket_name)
print('yes')