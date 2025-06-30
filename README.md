# CloudFront Invalidation Lambda

Simple AWS Lambda function that invalidates CloudFront cache for specified paths.

## Usage

Send an event with your CloudFront distribution ID and paths to invalidate:

```json
{
  "distribution_id": "E1234567890ABC",
  "paths": ["/index.html", "/css/*", "/js/*"]
}
```

- `distribution_id`: Your CloudFront distribution ID (required)
- `paths`: Paths to invalidate (optional, defaults to `["/*"]`)

## Response

Success:
```json
{
  "statusCode": 200,
  "body": {
    "message": "CloudFront invalidation process completed",
    "distribution_id": "E1234567890ABC",
    "invalidation_id": "I1234567890ABC",
    "success": true
  }
}
```

Error:
```json
{
  "statusCode": 404,
  "body": {
    "error": "CloudFront distribution not found"
  }
}
```

## Setup

1. Deploy the Lambda function
2. Add these IAM permissions to your Lambda role:
   - `cloudfront:GetDistribution`
   - `cloudfront:CreateInvalidation`
   - `cloudfront:GetInvalidation`

## Local Development

```bash
pip install -r requirements.txt
```
