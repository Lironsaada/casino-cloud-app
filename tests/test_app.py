import pytest
import json
import tempfile
import os
from app.app import app

@pytest.fixture
def client():
    # Create a temporary file for testing
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_login_page(client):
    """Test that login page loads"""
    rv = client.get('/')
    assert b'Login' in rv.data
    assert rv.status_code == 200

def test_metrics_endpoint(client):
    """Test that metrics endpoint works"""
    rv = client.get('/metrics')
    assert rv.status_code == 200
    assert b'casino_requests_total' in rv.data

def test_invalid_login(client):
    """Test login with invalid credentials"""
    rv = client.post('/', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_user_registration(client):
    """Test new user registration"""
    rv = client.post('/', data={
        'username': 'newuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    assert rv.status_code == 200

def test_menu_requires_login(client):
    """Test that menu requires authentication"""
    rv = client.get('/menu')
    assert rv.status_code == 302  # Redirect to login

def test_admin_requires_auth(client):
    """Test that admin panel requires authentication"""
    rv = client.get('/admin')
    assert rv.status_code == 302  # Redirect to admin auth 