import pytest 

@pytest.mark.health
def test_health(client): 
    response = client.get('/health')
    assert response.json()  == {'status': 'success', 'version': '1.0', 'releaseId': '0.1'}
    assert response.status_code == 200
