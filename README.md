# Text Classification Service on AWS Lambda

A production-ready serverless text classification API using AWS Lambda, API Gateway, and DynamoDB.

## Architecture

- **AWS Lambda**: Serverless compute for text classification
- **API Gateway**: REST API endpoint
- **S3**: Model artifact storage
- **DynamoDB**: Asynchronous logging of classifications
- **scikit-learn**: Pre-trained text classification model
  <img width="1536" height="1024" alt="ChatGPT Image Dec 26, 2025, 10_34_55 PM" src="https://github.com/user-attachments/assets/1c351346-919c-4e26-8a40-6b0bf177c91b" />


## Folder Structure

```
text-classification-service/
├── src/
│   ├── lambda_handler.py       # Main Lambda handler
│   ├── model_loader.py         # S3 model loading with caching
│   └── logger.py               # DynamoDB logging helper
├── scripts/
│   └── train_model.py          # Model training script
├── model/
│   └── text_classifier.pkl     # Pre-trained model (generated)
├── tests/
│   └── test_handler.py         # Unit tests
├── template.yaml               # AWS SAM template
├── requirements.txt            # Python dependencies
├── swagger.yaml                # OpenAPI documentation
└── README.md                   # This file
```

## Setup and Deployment


### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install aws-sam-cli
```

### 2. Train the Model

```bash
cd scripts
python train_model.py
cd ..
```

This generates `model/text_classifier.pkl`

### 3. Create S3 Bucket and Upload Model

```bash
BUCKET_NAME="text-classifier-model-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME
aws s3 cp model/text_classifier.pkl s3://$BUCKET_NAME/model/text_classifier.pkl
echo "Bucket: $BUCKET_NAME"
```

### 4. Deploy with SAM

```bash
sam build
sam deploy --guided \
  --parameter-overrides ModelBucketName=$BUCKET_NAME
```

Note your API endpoint from the CloudFormation outputs.

## API Usage

### Classify Text Request

```bash
API_URL="https://YOUR_API_ID.execute-api.REGION.amazonaws.com/Prod/classify"

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This team played an amazing baseball game yesterday and everyone cheered"
  }'
```

### Success Response (200)

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "category": "rec.sport.baseball",
  "confidence": 0.9234,
  "input_length": 60
}
```

### Error Responses

**Invalid Request (400)**
```json
{"error": "Text must be at least 10 characters"}
```

**Server Error (500)**
```json
{"error": "Failed to load model: S3 access denied"}
```

## Features

✅ **Request Validation**: Validates text input (min 10 characters)  
✅ **Model Caching**: Caches loaded models across Lambda invocations  
✅ **Async Logging**: Non-blocking DynamoDB writes  
✅ **Error Handling**: Comprehensive error responses  
✅ **Scalable**: Serverless architecture auto-scales  
✅ **Cost-Effective**: Pay per request, no idle costs  

## Configuration

Set via environment variables:

- `MODEL_BUCKET`: S3 bucket name (default: text-classifier-model-bucket)
- `MODEL_KEY`: S3 object key (default: model/text_classifier.pkl)
- `LOG_TABLE_NAME`: DynamoDB table name (auto-created)

## Monitoring

View Lambda logs:
```bash
aws logs tail /aws/lambda/text-classification-service --follow
```

Query DynamoDB logs:
```bash
aws dynamodb scan --table-name ClassificationLogsTable
```

## Testing

```bash
python -m pytest tests/
```

## Cleanup

```bash
sam delete
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3 rb s3://$BUCKET_NAME
```

## License

Apache 2.0
