#!/bin/bash
echo "Moving the deployment package to S3 Bucket"
npx serverless package
aws s3 sync .serverless/ s3://oauth-deployment/0.1.0
