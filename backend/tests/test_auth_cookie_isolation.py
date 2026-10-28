from app.config import settings
from types import SimpleNamespace


def test_custom_refresh_cookie_preserves_application_cookie(client, monkeypatch):
    monkeypatch.setattr('app.main.settings', SimpleNamespace(**{
        **settings.model_dump(), 'refresh_cookie_name': 'utility_system_refresh',
    }))
    client.cookies.set('utility_refresh', 'application-session-untouched', path='/api/auth')
    response = client.post('/api/auth/register', json={
        'email': 'cookie-isolation@example.com', 'password': 'SystemTestOnly2026!', 'full_name': 'Cookie Test',
    })
    assert response.status_code == 201
    assert client.cookies.get('utility_system_refresh')
    assert client.cookies.get('utility_refresh') == 'application-session-untouched'
    refreshed = client.post('/api/auth/refresh')
    assert refreshed.status_code == 200
    logout = client.post('/api/auth/logout', headers={'Authorization': 'Bearer ' + refreshed.json()['access_token']})
    assert logout.status_code == 200
    assert client.cookies.get('utility_system_refresh') is None
    assert client.cookies.get('utility_refresh') == 'application-session-untouched'
    assert client.post('/api/auth/refresh').status_code == 401
