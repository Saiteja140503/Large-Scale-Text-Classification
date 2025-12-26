import json
import os
import uuid
import time
from decimal import Decimal

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from model_loader import get_model
from logger import log_classification_async

MODEL_BUCKET = os.environ.get('MODEL_BUCKET', 'text-classifier-model-bucket')
MODEL_KEY = os.environ.get('MODEL_KEY', 'model/text_classifier.pkl')
LOG_TABLE_NAME = os.environ.get('LOG_TABLE_NAME', 'ClassificationLogsTable')

dynamodb = boto3.resource('dynamodb')

def _bad_request(message: str):
    return {
        'statusCode': 400,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': message}),
    }

def _server_error(message: str):
    return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': message}),
    }

def handler(event, context):
    """Lambda handler for text classification requests"""
    print(f"Event: {json.dumps(event)}")
    
    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError:
        return _bad_request('Request body must be valid JSON')
    
    text = body.get('text')
    if not isinstance(text, str) or not text.strip():
        return _bad_request("Field 'text' (non-empty string) is required")
    
    if len(text) < 10:
        return _bad_request('Text must be at least 10 characters')
    
    try:
        model = get_model(MODEL_BUCKET, MODEL_KEY)
    except (BotoCoreError, ClientError, OSError) as e:
        return _server_error(f'Failed to load model: {str(e)}')
    
    try:
        pred = model.predict([text])[0]
        if hasattr(model, 'predict_proba'):
            proba = float(max(model.predict_proba([text])[0]))
        else:
            proba = 1.0
    except Exception as e:
        return _server_error(f'Inference failed: {str(e)}')
    
    result = {
        'id': str(uuid.uuid4()),
        'category': str(pred),
        'confidence': round(proba, 4),
        'input_length': len(text),
    }
    
    try:
        log_table = dynamodb.Table(LOG_TABLE_NAME)
        log_classification_async(
            table=log_table,
            item={
                'id': result['id'],
                'timestamp': Decimal(str(time.time())),
                'text': text[:1000],
                'category': result['category'],
                'confidence': Decimal(str(result['confidence'])),
                'request_id': getattr(context, 'aws_request_id', 'unknown'),
            },
        )
    except Exception as e:
        print(f'Log error (non-blocking): {e}')
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(result),
    }
