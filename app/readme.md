# Flask upload files on bucket

## Build
  podman build -t quay.io/lagomes/flask-s3-upload:v10 .
  podman push quay.io/lagomes/flask-s3-upload:v10

## Execute 
  export BUCKET_NAME=$(oc get obc -n flask-hml flask -o jsonpath='{.spec.bucketName}')
  export AWS_ACCESS_KEY_ID=$(oc get secret -n flask-hml flask -o yaml | grep -w  "AWS_ACCESS_KEY_ID:" | head -n1 | awk '{print $2}' | base64 --decode)
  export AWS_SECRET_ACCESS_KEY=$(oc get secret -n flask-hml flask -o yaml | grep -w "AWS_SECRET_ACCESS_KEY:" | head -n1 | awk '{print $2}' | base64 --decode)
  export ROUTE=$(oc -n flask-hml get route ocs-storagecluster-cephobjectstore-secure -o jsonpath='{.spec.host}')

  echo $BUCKET_NAME - $AWS_ACCESS_KEY_ID - $AWS_SECRET_ACCESS_KEY - $ROUTE

## Run Container
  podman run -p 5000:5000 \
    -e S3_BUCKET=$BUCKET_NAME \
    -e S3_REGION=us-east-1 \
    -e S3_ACCESS_KEY=$AWS_ACCESS_KEY_ID \
    -e S3_SECRET_KEY=$AWS_SECRET_ACCESS_KEY \
    -e S3_VERIFY_SSL=false \
    -e S3_ENDPOINT_URL=https://$ROUTE \
    quay.io/lagomes/flask-s3-upload:v7
