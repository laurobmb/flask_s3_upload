"""Aplicação Flask para upload de imagens em um bucket S3."""

import logging
import logging.config
import os

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from botocore.exceptions import BotoCoreError, ClientError
from werkzeug.utils import secure_filename
import boto3

LOG_FORMAT = '%(asctime)s: %(threadName)s: %(name)s: %(levelname)s: %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger('flask_upload')

app = Flask(__name__)
app.secret_key = 'minha_chave_secreta'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
S3_BUCKET = os.environ.get('S3_BUCKET', 'meu-bucket-de-imagens')
S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', 'minha_access_key_default')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY', 'minha_secret_key_default')
S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
S3_VERIFY_SSL = os.environ.get('S3_VERIFY_SSL', 'true').lower() in ['1', 'true', 'yes']

def create_s3_client():
    return boto3.client(
        's3',
        region_name=S3_REGION,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        endpoint_url=S3_ENDPOINT_URL,
        verify=S3_VERIFY_SSL
    )


def is_allowed_file(filename):
    """Aplicação Flask para upload de imagens em um bucket S3."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/debug')
def debug():
    """Aplicação Flask para upload de imagens em um bucket S3."""
    return render_template('debug.html',
        s3_bucket=os.environ.get('S3_BUCKET', 'meu-bucket-de-imagens'),
        s3_region=os.environ.get('S3_REGION', 'us-east-1'),
        s3_access_key=os.environ.get('S3_ACCESS_KEY', 'minha_access_key_default'),
        s3_secret_key=os.environ.get('S3_SECRET_KEY', 'minha_secret_key_default'),
        s3_endpoint_url=os.environ.get('S3_ENDPOINT_URL', 'None'),
        s3_verify_ssl=os.environ.get('S3_VERIFY_SSL', 'true').lower() in ['1', 'true', 'yes']
        )

@app.route('/')
def index():
    """Aplicação Flask para upload de imagens em um bucket S3."""
    logger.info("FLASK_UPLOAD: Inicial")
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Aplicação Flask para upload de imagens em um bucket S3."""
    s3 = create_s3_client()
    if 'image' not in request.files:
        logger.error("FLASK_UPLOAD: Nenhum arquivo enviado")
        flash('Nenhum arquivo enviado.')
        return redirect(url_for('index'))

    file = request.files['image']

    if file.filename == '':
        logger.error("FLASK_UPLOAD: Nome do arquivo vazio.")
        flash('Nome do arquivo vazio.')
        return redirect(url_for('index'))

    if file and is_allowed_file(file.filename):
        filename = secure_filename(file.filename)

        try:
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                filename,
                ExtraArgs={'ContentType': file.content_type}
            )
            logger.info("FLASK_UPLOAD: enviada com sucesso!")
            flash(f'Imagem "{filename}" enviada com sucesso!')
            return redirect(url_for('index'))

        except (ClientError, BotoCoreError) as e:
            logger.error("FLASK_UPLOAD: Erro ao enviar.")
            flash(f"Erro ao enviar: {str(e)}")
            return redirect(url_for('index'))

    else:
        logger.error("FLASK_UPLOAD: Formato de imagem não permitido.")
        flash('Formato de imagem não permitido.')
        return redirect(url_for('index'))


@app.route('/up', methods=['POST'])
def up():
    """Aplicação Flask para upload de imagens em um bucket S3."""
    s3 = create_s3_client()
    file = request.files['image']
    filename = secure_filename(file.filename)
    s3.upload_fileobj(file, S3_BUCKET, filename, ExtraArgs={'ContentType': file.content_type})
    logger.info("FLASK_UPLOAD: enviada com sucesso!")
    return jsonify({"return": "Arquivo enviado"})


@app.route('/listar')
def listar():
    """Aplicação Flask para upload de imagens em um bucket S3."""
    s3 = create_s3_client()
    try:
        objetos = s3.list_objects_v2(Bucket=S3_BUCKET)
        nomes_arquivos = [obj['Key'] for obj in objetos.get('Contents', [])]
        logger.info("FLASK_UPLOAD: Bucket listado com sucesso.")
        return jsonify({'arquivos': nomes_arquivos})
    except (ClientError, BotoCoreError) as e:
        logger.error("FLASK_UPLOAD: Erro no acesso ao bucket.")
        return jsonify({'erro': str(e)}), 500


@app.route('/download/<path:filename>')
def download(filename):
    """Download de arquivo com verificação de existência."""
    s3 = create_s3_client()
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=filename)
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': filename},
            ExpiresIn=3600
        )
        return redirect(url)

    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            logger.error("FLASK_UPLOAD: Arquivo não encontrado: %s", filename)
            return jsonify({'erro': 'Arquivo não encontrado'}), 404
        logger.error("FLASK_UPLOAD: Erro ao gerar URL para %s: %s", filename, e)
        return jsonify({'erro': str(e)}), 500


if __name__ == '__main__':
    app.run( debug=True, host='0.0.0.0', port=5000 )
