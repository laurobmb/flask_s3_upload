#!/bin/bash

export BUCKET_NAME=$(oc get obc -n flask-hml flask-hml -o jsonpath='{.spec.bucketName}')
export AWS_ACCESS_KEY_ID=$(oc get secret -n flask-hml flask-hml -o yaml | grep -w  "AWS_ACCESS_KEY_ID:" | head -n1 | awk '{print $2}' | base64 --decode)
export AWS_SECRET_ACCESS_KEY=$(oc get secret -n flask-hml flask-hml -o yaml | grep -w "AWS_SECRET_ACCESS_KEY:" | head -n1 | awk '{print $2}' | base64 --decode)
export ROUTE=$(oc -n openshift-storage get route ocs-storagecluster-cephobjectstore-secure -o jsonpath='{.spec.host}')

echo -e "
oc -n flask-hml create secret generic flask-secret \
  --from-literal=S3_BUCKET=$BUCKET_NAME \
  --from-literal=S3_ACCESS_KEY=$AWS_ACCESS_KEY_ID \
  --from-literal=S3_SECRET_KEY=$AWS_SECRET_ACCESS_KEY \
  --from-literal=S3_ENDPOINT_URL=https://$ROUTE \
  --from-literal=S3_REGION=us-east-1 \
  --from-literal=S3_VERIFY_SSL=false
"
