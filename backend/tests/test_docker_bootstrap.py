from app.config import settings
from conftest import register


def test_first_registration_admin_only_in_local_bootstrap(client, monkeypatch):
    monkeypatch.setattr(settings, 'app_env', 'development')
    monkeypatch.setattr(settings, 'bootstrap_first_user_admin', True)
    first = register(client, 'first-local@example.com')
    assert client.get('/api/auth/me', headers=first).json()['role'] == 'ADMIN'
    second = register(client, 'second-local@example.com')
    assert client.get('/api/auth/me', headers=second).json()['role'] == 'USER'


def test_bootstrap_does_not_grant_admin_in_production(client, monkeypatch):
    monkeypatch.setattr(settings, 'app_env', 'production')
    monkeypatch.setattr(settings, 'bootstrap_first_user_admin', True)
    headers = register(client, 'production-user@example.com')
    assert client.get('/api/auth/me', headers=headers).json()['role'] == 'USER'
