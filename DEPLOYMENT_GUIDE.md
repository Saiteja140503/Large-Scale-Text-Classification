# Deployment Guide

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- AWS SAM CLI installed
- Python 3.9+
- Git (optional)

## Step-by-Step Deployment

### Step 1: Prepare Environment

```bash
cd text-classification-service
pip install -r requirements.txt
pip install aws-sam-cli
```

### Step 2: Train the Model

```bash
cd scripts
python train_model.py
cd ..
```

This creates `model/text_classifier.pkl` (~2-5 MB)

### Step 3: Create S3 Bucket for Model

```bash
# Generate unique bucket name with timestamp
BUCKET_NAME="text-classifier-model-$(date +%s)"
echo $BUCKET_NAME

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Upload model
aws s3 cp model/text_classifier.pkl s3://$BUCKET_NAME/model/text_classifier.pkl

# Verify upload
aws s3 ls s3://$BUCKET_NAME/model/
```

### Step 4: Build and Deploy with SAM

```bash
# Build the Lambda function
sam build

# Deploy (guided mode for first deployment)
sam deploy --guided \
  --parameter-overrides ModelBucketName=$BUCKET_NAME \
  --region us-east-1
```

When prompted:
- Stack name: `text-classification-service` (or your choice)
- Region: `us-east-1` (or preferred region)
- Allow SAM to create IAM roles: **Y**
- Save parameters: **Y**

### Step 5: Retrieve Outputs

After deployment completes, CloudFormation will output:

```
Outputs:
Key                    Value
---------------------------------------------
TextClassificationAPI  https://xyz123.execute-api.us-east-1.amazonaws.com/Prod/classify
DynamoDBTable         ClassificationLogsTable-XXXXX
LambdaFunction        arn:aws:lambda:us-east-1:XXXXX:function:text-...
```

Save the **TextClassificationAPI** URL - you'll use it for testing.

### Step 6: Test the Deployment

```bash
# Set your API endpoint
API_URL="https://xyz123.execute-api.us-east-1.amazonaws.com/Prod/classify"

# Test with a valid request
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a sample text for classification with enough content to pass validation."
  }' | jq .
```

Expected response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "comp.graphics",
  "confidence": 0.92,
  "input_length": 78
}
```

## Subsequent Deployments

For code changes without model updates:

```bash
sam build
sam deploy --region us-east-1
```

## Monitoring

### View Lambda Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/TextClassifierFunction --follow

# Last 10 minutes
aws logs tail /aws/lambda/TextClassifierFunction --since 10m
```

### Query Classification Logs

```bash
# List all classifications
aws dynamodb scan --table-name ClassificationLogsTable-XXXXX

# Query specific category
aws dynamodb query \
  --table-name ClassificationLogsTable-XXXXX \
  --key-condition-expression "category = :cat" \
  --expression-attribute-values '{":cat":{"S":"comp.graphics"}}'
```

## Cleanup

### Delete CloudFormation Stack

```bash
sam delete --region us-east-1
```

This will delete:
- Lambda function
- API Gateway
- DynamoDB table
- CloudFormation stack

**Note:** It does NOT delete the S3 bucket (for safety)

### Delete S3 Bucket

```bash
# Remove all objects
aws s3 rm s3://$BUCKET_NAME --recursive

# Delete empty bucket
aws s3 rb s3://$BUCKET_NAME
```

## Troubleshooting

### Model Not Found (S3 Error)

Ensure:
- Model uploaded to S3: `aws s3 ls s3://$BUCKET_NAME/model/`
- Correct bucket name passed to CloudFormation
- Lambda has S3 read permissions (auto-configured by SAM)

### DynamoDB Permission Denied

Ensure:
- Table name matches environment variable
- Lambda has DynamoDBCrudPolicy attached
- Table exists and is in ACTIVE state

### API Gateway 502 Bad Gateway

Check:
- Lambda logs: `aws logs tail /aws/lambda/TextClassifierFunction`
- Lambda timeout (currently 30 seconds)
- Memory allocation (currently 1024 MB)

### Increase Lambda Resources

Edit `template.yaml`:

```yaml
Globals:
  Function:
    Timeout: 60        # Increase to 60 seconds
    MemorySize: 2048   # Increase to 2048 MB
```

Then redeploy:
```bash
sam build && sam deploy
```

## Cost Estimation

**Monthly (assumed 10,000 requests)**

- Lambda: $0.20 (1M requests = $0.20)
- DynamoDB: $0.35 (on-demand, ~1GB storage)
- S3: <$0.05 (model storage)
- API Gateway: $0.35 (1M requests = $0.35)

**Total: ~$1 per month** for small workloads

## Additional Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Limits](https://docs.aws.amazon.com/lambda/latest/dg/limits.html)
- [DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
