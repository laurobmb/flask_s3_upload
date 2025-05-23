import io
import pytest
import boto3
from moto import mock_aws
from bs4 import BeautifulSoup
from app import app, S3_BUCKET, S3_REGION


# 🏗️ Configura o mock do S3
@pytest.fixture(autouse=True)
def s3_mock():
    """Inicializa o mock do S3 para os testes."""
    with mock_aws():
        s3 = boto3.client(
            's3',
            region_name=S3_REGION,
        )
        s3.create_bucket(Bucket=S3_BUCKET)
        yield



# 🚀 Cliente de teste do Flask
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# 🔸 Teste da página inicial
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Upload' in response.get_data(as_text=True)


def test_debug(client):
    response = client.get('/debug')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    table = soup.find('table')
    assert table is not None
    assert S3_BUCKET in table.text


# 🔸 Upload bem-sucedido
def test_upload_sucesso(client):
    data = {
        'image': (io.BytesIO(b'meu-arquivo-de-imagem'), 'foto.png')
    }
    response = client.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert 'foto.png' in response.get_data(as_text=True)


# 🔸 Upload sem enviar arquivo
def test_upload_sem_arquivo(client):
    response = client.post('/upload', content_type='multipart/form-data', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Nenhum arquivo enviado' in response.get_data(as_text=True)


# 🔸 Upload com nome vazio
def test_upload_nome_vazio(client):
    data = {
        'image': (io.BytesIO(b'teste'), '')
    }
    response = client.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Nome do arquivo vazio' in response.get_data(as_text=True)


# 🔸 Upload com extensão inválida
def test_upload_extensao_invalida(client):
    data = {
        'image': (io.BytesIO(b'teste'), 'arquivo.txt')
    }
    response = client.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Formato de imagem não permitido' in response.get_data(as_text=True)


# 🔸 Upload usando /up (retorna JSON)
def test_up_endpoint(client):
    data = {
        'image': (io.BytesIO(b'meu-arquivo-de-imagem'), 'foto.png')
    }
    response = client.post('/up', content_type='multipart/form-data', data=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['return'] == 'Arquivo enviado'


# 🔸 Listagem de arquivos no bucket
def test_listar(client):
    s3 = boto3.client('s3', region_name=S3_REGION)
    s3.put_object(Bucket=S3_BUCKET, Key='foto.png', Body=b'conteudo')

    response = client.get('/listar')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'arquivos' in json_data
    assert 'foto.png' in json_data['arquivos']


# 🔸 Download gera URL assinada
def test_download(client):
    s3 = boto3.client('s3', region_name=S3_REGION)
    s3.put_object(Bucket=S3_BUCKET, Key='foto.png', Body=b'conteudo')

    response = client.get('/download/foto.png')
    assert response.status_code == 302  # Redirect para URL assinada
    assert 'https://' in response.location or 'http://' in response.location


# 🔸 Download de arquivo que não existe gera erro
def test_download_arquivo_inexistente(client):
    response = client.get('/download/inexistente.png')
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'erro' in json_data
    assert json_data['erro'] == 'Arquivo não encontrado'
