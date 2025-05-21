# Flask: Upload de Arquivos para o Bucket

1. Acesse o diretório do projeto:

   ```bash
   cd /root/flask_upload_files_on_bucket
   ```

2. Aplique os manifests no cluster OpenShift:

   ```bash
   oc apply -k k8s/overlays/flask/
   ```

3. Após criar a aplicação, execute o script abaixo:

   ```bash
   k8s/get_infos_obc.sh
   ```

Esse script coleta as informações do **OBC** (Object Bucket Claim) e da rota do `ocs-storagecluster-ceph-rgw`. A saída será uma linha de comando para criar uma secret no mesmo namespace. Execute a linha mostrada e acompanhe o deploy dos pods no namespace.