import io
import os
import pytest
from app import app, S3_BUCKET, S3_REGION
import boto3
from moto import mock_aws


# Fixture que inicializa o mock do S3 e o cliente de testes do Flask
@pytest.fixture(autouse=True)
def s3_mock():
    with mock_aws():
        s3 = boto3.client(
            "s3",
            region_name=S3_REGION,
        )
        s3.create_bucket(Bucket=S3_BUCKET)
        yield


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Teste da página inicial
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Upload de Imagem' in response.get_data(as_text=True)


# Teste de upload bem-sucedido
def test_upload_sucesso(client):
    data = {
        'image': (io.BytesIO(b'teste de imagem'), 'imagem_teste.png')
    }
    response = client.post('/upload2', content_type='multipart/form-data', data=data, follow_redirects=True)

    assert response.status_code == 200
    assert 'Imagem "imagem_teste.png" enviada com sucesso!' in response.get_data(as_text=True)


# Teste de upload com extensão não permitida
def test_upload_extensao_invalida(client):
    data = {
        'image': (io.BytesIO(b'teste de imagem'), 'arquivo.txt')
    }
    response = client.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)

    assert response.status_code == 200
    assert 'Formato de imagem não permitido' in response.get_data(as_text=True)


# Teste de upload sem arquivo enviado
def test_upload_sem_arquivo(client):
    response = client.post('/upload', content_type='multipart/form-data', data={}, follow_redirects=True)

    assert response.status_code == 200
    assert 'Nenhum arquivo enviado' in response.get_data(as_text=True)


# Teste de listagem de arquivos no bucket
def test_listar_arquivos(client):
    # Faz upload de um arquivo antes
    s3 = boto3.client('s3', region_name=S3_REGION)
    s3.put_object(Bucket=S3_BUCKET, Key='imagem1.png', Body=b'abc')

    response = client.get('/listar')

    assert response.status_code == 200
    json_data = response.get_json()
    assert 'arquivos' in json_data
    assert 'imagem1.png' in json_data['arquivos']


# Teste de download gera uma URL assinada
def test_download(client):
    s3 = boto3.client('s3', region_name=S3_REGION)
    s3.put_object(Bucket=S3_BUCKET, Key='imagem1.png', Body=b'abc')

    response = client.get('/download/imagem1.png')
    assert response.status_code == 302  # Redirect para a URL assinada
    assert 'https://' in response.location or 'http://' in response.location
