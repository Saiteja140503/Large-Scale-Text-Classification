import pickle
from io import BytesIO
from typing import Any
import boto3

_s3 = boto3.client('s3')
_model_cache = {}

def get_model(bucket: str, key: str):
    """
    Load model from S3 with caching.
    Avoids re-downloading on warm Lambda invocations.
    """
    cache_key = (bucket, key)
    if cache_key in _model_cache:
        print(f"Model loaded from cache")
        return _model_cache[cache_key]
    
    print(f"Loading model from S3: s3://{bucket}/{key}")
    obj = _s3.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read()
    model = pickle.loads(data)
    _model_cache[cache_key] = model
    return model
