import time

import pytest
from rest_framework.test import APIClient

from secret.models import Secret


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_create_secret(client):
    count = Secret.objects.count()
    response_text = client.post('/generate/', data={'text': 'test text'})
    assert response_text.status_code == 201
    assert Secret.objects.count() == count + 1
    count += 1

    response_secret_phrase = client.post('/generate/', data={'text': 'test text', 'secret_phrase': 'test phrase'})
    assert response_secret_phrase.status_code == 201
    assert Secret.objects.count() == count + 1
    count += 1

    response_time_to_live = client.post('/generate/', data={'text': 'test text', 'time_to_live': '60'})
    assert response_time_to_live.status_code == 201
    assert Secret.objects.count() == count + 1
    count += 1

    response_no_text = client.post('/generate/', data={})
    assert response_no_text.status_code == 400
    assert Secret.objects.count() == count


@pytest.mark.django_db
def test_get_secret(client):
    secret = client.post('/generate/', data={'text': 'test text'})
    secret_key = secret.data['secret key']
    response_get = client.get(f'/secrets/{secret_key}/')
    assert response_get.status_code == 200

    response_get = client.get(f'/secrets/{secret_key}/')
    assert response_get.status_code == 404

    secret_with_phrase = client.post('/generate/', data={'text': 'test text', 'secret_phrase': 'test phrase'})
    secret_key = secret_with_phrase.data['secret key']
    response_get = client.get(f'/secrets/{secret_key}/')
    assert response_get.status_code == 403

    response_get = client.get(f'/secrets/{secret_key}/?secret_phrase=wrong+phrase')
    assert response_get.status_code == 403

    response_get = client.get(f'/secrets/{secret_key}/?secret_phrase=test+phrase')
    assert response_get.status_code == 200

    secret_with_ttl = client.post('/generate/', data={'text': 'test text', 'time_to_live': '1'})
    secret_key = secret_with_ttl.data['secret key']
    time.sleep(2)
    response_get = client.get(f'/secrets/{secret_key}/')
    assert response_get.status_code == 404

    secret_with_ttl = client.post('/generate/', data={'text': 'test text', 'time_to_live': '1'})
    secret_key = secret_with_ttl.data['secret key']
    response_get = client.get(f'/secrets/{secret_key}/')
    assert response_get.status_code == 200