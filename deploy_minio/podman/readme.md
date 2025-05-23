# MINIO podman 

mkdir -p /home/lagomes/MEGA/minio/podman/minio/data

export DIRETORIO="/home/lagomes/MEGA/minio/podman/minio/data"

podman run -it --rm -p 9000:9000 -p 9090:9090 --name minio -v ${DIRETORIO}:/data:z -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" quay.io/minio/minio:latest server /data --console-address ":9090"