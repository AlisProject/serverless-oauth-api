#!/bin/bash
echo "Moving the deployment package to S3 Bucket"
npx serverless package --s3-bucket ${DEPLOYMENT_BUCKET} --s3-key ${CIRCLE_TAG} --stage production
aws s3 sync .serverless/ s3://${DEPLOYMENT_BUCKET}/${CIRCLE_TAG}
