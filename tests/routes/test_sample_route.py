import pytest 


@pytest.mark.sample
def test_get_sample(client):
    response = client.get('/sample')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.sample
def test_create_sample(client):
    response = client.post('/sample', json={"name": "sample", "description": "sample"})
    assert response.status_code == 200
