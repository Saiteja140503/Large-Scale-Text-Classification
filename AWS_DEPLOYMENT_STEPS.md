# AWS DEPLOYMENT - Complete Guide

## Overview
Deploy the Text Classification Service to AWS using SAM (Serverless Application Model)

## Prerequisites Checklist

- [x] AWS Account with billing enabled
- [x] AWS CLI installed (v2+)
- [x] AWS SAM CLI installed
- [x] Python 3.9+
- [x] Git (recommended)
- [x] AWS credentials configured: `aws configure`

## Phase 1: Local Preparation (5 min)

### Step 1a: Download Project from Colab
1. Open Google Colab file browser (left sidebar)
2. Right-click `text-classification-service/` folder
3. Click "Download"
4. Extract the ZIP file on your machine

### Step 1b: Verify Project Structure
```bash
cd text-classification-service
ls -la
# Should see: src/ scripts/ model/ tests/ template.yaml requirements.txt swagger.yaml README.md
```

### Step 1c: Install Python Dependencies
```bash
pip install -r requirements.txt
pip install aws-sam-cli
```

## Phase 2: Train the ML Model (10-15 min)

### Step 2a: Train Model Locally
```bash
cd scripts
python train_model.py
cd ..
```

**Expected output:**
```
Fetching 20newsgroups dataset...
Training samples: 2257
Building ML pipeline...
Training model...
Saving model to ../model/text_classifier.pkl
Model saved successfully!
Model size: 2345.67 KB
```

### Step 2b: Verify Model File
```bash
ls -lh model/
# Should show: text_classifier.pkl (~2-5 MB)
```

## Phase 3: AWS Setup (5 min)

### Step 3a: Configure AWS CLI
If not already configured:
```bash
aws configure
# Enter:
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: us-east-1  (or your preference)
# Default output format: json
```

### Step 3b: Verify AWS Access
```bash
aws sts get-caller-identity
# Output should show your AWS account info
```

## Phase 4: Create S3 Bucket for Model (3 min)

### Step 4a: Create Unique Bucket Name
```bash
BUCKET_NAME="text-classifier-model-$(date +%s)"
echo "Bucket: $BUCKET_NAME"
# Save this value - you'll need it for deployment
```

### Step 4b: Create S3 Bucket
```bash
aws s3 mb s3://$BUCKET_NAME --region us-east-1
```

### Step 4c: Upload Model to S3
```bash
aws s3 cp model/text_classifier.pkl s3://$BUCKET_NAME/model/text_classifier.pkl
```

### Step 4d: Verify Upload
```bash
aws s3 ls s3://$BUCKET_NAME/model/
# Should show: text_classifier.pkl
```

## Phase 5: Deploy with AWS SAM (10 min)

### Step 5a: Build Lambda Function
```bash
sam build
# Output: Successfully packaged artifacts and wrote output template to .aws-sam/build/template.yaml
```

### Step 5b: Guided Deployment
```bash
sam deploy --guided \
  --parameter-overrides ModelBucketName=$BUCKET_NAME \
  --region us-east-1
```

**When prompted:**
```
Stack Name: text-classification-service
Region: us-east-1
Setting default parameter ModelBucketName: YOUR_BUCKET_NAME

Confirm changes before deploy [y/N]: y
Allow SAM CLI IAM role creation [Y/n]: Y
TextClassifierFunction may not have authorization defined. Allow anyway? [y/N]: y
Save parameters to samconfig.toml? [Y/n]: Y
Save environment variables to .env? [Y/n]: N
```

### Step 5c: Wait for Deployment
⏳ **Duration: 3-5 minutes**

Monitor CloudFormation:
```bash
aws cloudformation describe-stacks --stack-name text-classification-service --query 'Stacks[0].StackStatus'
```

## Phase 6: Test Deployment (5 min)

### Step 6a: Get API Endpoint
```bash
aws cloudformation describe-stacks \
  --stack-name text-classification-service \
  --query 'Stacks[0].Outputs' \
  --region us-east-1
```

**Output will show:**
```json
[
  {
    "OutputKey": "TextClassificationAPI",
    "OutputValue": "https://abc123def456.execute-api.us-east-1.amazonaws.com/Prod/classify"
  }
]
```

### Step 6b: Save API Endpoint
```bash
API_URL="https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/Prod/classify"
echo $API_URL  # Test variable
```

### Step 6c: Test with Valid Request
```bash
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This team played an amazing baseball game yesterday and everyone cheered"
  }' | jq .
```

**Expected Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "rec.sport.baseball",
  "confidence": 0.8234,
  "input_length": 84
}
```

### Step 6d: Test Invalid Request (Validation)
```bash
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"text": "short"}' | jq .
```

**Expected Response (400):**
```json
{"error": "Text must be at least 10 characters"}
```

### Step 6e: Test Missing Field
```bash
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
```

**Expected Response (400):**
```json
{"error": "Field 'text' (non-empty string) is required"}
```

## Phase 7: Monitor & Verify (Ongoing)

### View Lambda Logs
```bash
aws logs tail /aws/lambda/TextClassifierFunction --follow --region us-east-1
```

### Query DynamoDB Logs
```bash
aws dynamodb scan --table-name ClassificationLogsTable \
  --region us-east-1 \
  --max-items 5
```

### CloudWatch Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=TextClassifierFunction \
  --statistics Sum \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --region us-east-1
```

## Phase 8: Performance Testing (Optional)

### Test High Load (10 concurrent requests)
```bash
for i in {1..10}; do
  curl -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"text": "Testing concurrent requests with text about computer graphics and 3D rendering"}' &
done
wait
echo "All 10 requests completed"
```

### Test Different Categories
```bash
# Graphics
curl -X POST "$API_URL" -H "Content-Type: application/json" \
  -d '{"text": "How do I optimize 3D graphics rendering for real-time applications?"}' | jq .category

# Medical
curl -X POST "$API_URL" -H "Content-Type: application/json" \
  -d '{"text": "The patient presented with symptoms requiring immediate medical evaluation and treatment."}' | jq .category

# Politics
curl -X POST "$API_URL" -H "Content-Type: application/json" \
  -d '{"text": "Political discussions about Middle East policy and international relations."}' | jq .category
```

## Phase 9: Troubleshooting

### Issue: Model Not Found (S3 Error)
**Error:** `Failed to load model: S3 access denied`

**Solution:**
```bash
# 1. Verify bucket exists
aws s3 ls s3://$BUCKET_NAME/model/

# 2. Check Lambda IAM role has S3 permissions
aws iam get-role-policy --role-name text-classification-service-TextClassifierFunction* --policy-name S3ReadPolicy

# 3. Check bucket name in template matches deployment
echo $BUCKET_NAME
```

### Issue: API Gateway 502 Bad Gateway
**Error:** `HTTP 502 Bad Gateway`

**Solution:**
```bash
# 1. Check Lambda logs
aws logs tail /aws/lambda/TextClassifierFunction --region us-east-1

# 2. Increase Lambda timeout
# Edit template.yaml: change Timeout to 60
sam build && sam deploy

# 3. Check Lambda memory
# Lambda might be out of memory - increase MemorySize in template.yaml
```

### Issue: DynamoDB WriteThrottling
**Error:** `ProvisionedThroughputExceededException`

**Solution:**
DynamoDB is set to on-demand (PAY_PER_REQUEST), so this shouldn't occur. If it does:
```bash
aws dynamodb describe-table --table-name ClassificationLogsTable --region us-east-1 | grep BillingModeSummary
```

## Phase 10: Cleanup (If Needed)

### Delete CloudFormation Stack (Deletes Lambda, API Gateway, DynamoDB)
```bash
sam delete --region us-east-1
# Confirm: y
```

### Delete S3 Bucket (Manual - SAM won't delete it)
```bash
# Remove all objects
aws s3 rm s3://$BUCKET_NAME --recursive --region us-east-1

# Delete empty bucket
aws s3 rb s3://$BUCKET_NAME --region us-east-1
```

### Verify Cleanup
```bash
aws cloudformation list-stacks --query 'StackSummaries[?StackName==`text-classification-service`]'
aws s3 ls | grep text-classifier
```

## Cost Estimation

**Monthly costs (assuming 10,000 requests/month):**

| Service | Cost |
|---------|------|
| Lambda | $0.20 (1M = $0.20) |
| DynamoDB | $0.35 (on-demand) |
| API Gateway | $0.35 (1M = $0.35) |
| S3 | <$0.05 (model storage) |
| **Total** | **~$1.00/month** |

**Note:** AWS Free Tier covers first 1M Lambda invocations/month for 1 year

## Success Checklist

- [x] Model trained successfully
- [x] S3 bucket created with model uploaded
- [x] SAM deployment successful
- [x] API endpoint accessible
- [x] Valid text request returns 200
- [x] Invalid request returns 400
- [x] DynamoDB logging working
- [x] CloudWatch logs accessible
- [x] Cost under $10/month

## Next Steps

1. **Integrate with your app:**
   ```javascript
   fetch('YOUR_API_URL', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({text: 'Your text here'})
   })
   .then(r => r.json())
   .then(data => console.log(data.category, data.confidence))
   ```

2. **Set up CI/CD:** Use GitHub Actions or AWS CodePipeline

3. **Custom domain:** Configure custom domain name for API Gateway

4. **Authentication:** Add API keys or OAuth for API Gateway

5. **Auto-scaling:** Configure Lambda concurrency limits

## Support Resources

- AWS SAM Documentation: https://docs.aws.amazon.com/serverless-application-model/
- AWS Lambda: https://docs.aws.amazon.com/lambda/
- API Gateway: https://docs.aws.amazon.com/apigateway/
- DynamoDB: https://docs.aws.amazon.com/dynamodb/
- AWS Free Tier: https://aws.amazon.com/free/

