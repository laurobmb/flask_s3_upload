# Deploy
* oc apply -k k8s/overlays/flask/

oc create secret generic flask-secret \
  --from-literal=S3_BUCKET=flask-xxxxxxxxxxxxx \
  --from-literal=S3_ACCESS_KEY=xxxxxxxxxxxxxxxxx \
  --from-literal=S3_SECRET_KEY=xxxxxxxxxxxxxxxxx \
  --from-literal=S3_ENDPOINT_URL=https://ocs-storagecluster-cephobjectstore-secure-openshift-storage.apps.br \
  --from-literal=S3_REGION=us-east-1 \
  --from-literal=S3_VERIFY_SSL=false
