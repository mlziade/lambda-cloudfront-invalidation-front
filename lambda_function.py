import json
import boto3
import time
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function to check CloudFront distribution, create invalidation, and verify success
    
    Expected event format:
    {
        "distribution_id": "E1234567890ABC",
        "paths": ["/index.html", "/css/*", "/js/*"]
    }
    """
    
    # Initialize CloudFront client
    cloudfront = boto3.client('cloudfront')
    
    try:
        # Extract parameters from event
        distribution_id = event.get('distribution_id')
        paths = event.get('paths', ['/*'])  # Default to invalidate all paths
        
        if not distribution_id:
            print("Error: distribution_id is required in the event payload")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'distribution_id is required in the event payload'
                })
            }
        
        # Step 1: Check if CloudFront distribution exists
        print(f"Checking if distribution {distribution_id} exists...")
        distribution_exists = check_distribution_exists(cloudfront, distribution_id)
        
        if not distribution_exists:
            print(f"Distribution {distribution_id} not found or not enabled")
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': f'CloudFront distribution {distribution_id} not found'
                })
            }
        
        print(f"Distribution {distribution_id} exists and is active")
        
        # Step 2: Create invalidation
        print(f"Creating invalidation for paths: {paths}")
        invalidation_id = create_invalidation(cloudfront, distribution_id, paths)
        
        if not invalidation_id:
            print(f"Failed to create invalidation for the distribution {distribution_id} with paths: {paths}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Failed to create invalidation'
                })
            }
        
        print(f"Invalidation created with ID: {invalidation_id} for distribution {distribution_id} and paths: {paths}")
        
        # Return immediately after creating invalidation
        return {
            'statusCode': 200,
            'body': json.dumps({
            'message': 'CloudFront invalidation created successfully',
            'distribution_id': distribution_id,
            'invalidation_id': invalidation_id,
            'paths': paths,
            'success': True
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"AWS ClientError: {error_code} - {error_message}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
            'error': f'AWS Error: {error_code} - {error_message}',
            'success': False
            })
        }
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
            'error': f'Unexpected error: {str(e)}',
            'success': False
            })
        }

def check_distribution_exists(cloudfront, distribution_id):
    """
    Check if a CloudFront distribution exists and is enabled
    """
    try:
        response = cloudfront.get_distribution(Id=distribution_id)
        distribution = response['Distribution']
        
        # Check if distribution is enabled (don't wait for deployment status)
        status = distribution['Status']
        enabled = distribution['DistributionConfig']['Enabled']
        
        print(f"Distribution status: {status}, Enabled: {enabled}")
        
        # Return True if distribution exists and is enabled, regardless of deployment status
        return enabled
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchDistribution':
            print(f"Distribution {distribution_id} does not exist")
            return False
        else:
            raise e

def create_invalidation(cloudfront, distribution_id, paths):
    """
    Create a CloudFront invalidation for specified paths
    """
    try:
        caller_reference = f"lambda-invalidation-{int(time.time())}"
        
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': caller_reference
            }
        )
        
        return response['Invalidation']['Id']
        
    except ClientError as e:
        print(f"Failed to create invalidation: {e}")
        return None