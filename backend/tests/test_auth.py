"""
Tests for authentication functionality
"""
import pytest
import json
from flask import Flask
from src.create_app import create_app
from infrastructure.databases.mssql import db
from domain.enums import UserRole


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'SecurePass123!',
            'role': 'MEMBER'
        }
        
        response = client.post('/api/v1/auth/register', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'access_token' in response_data['data']
        assert 'refresh_token' in response_data['data']
        assert response_data['data']['user']['email'] == 'john@example.com'
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com'
            # Missing password
        }
        
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'MISSING_FIELDS' in response_data['code']
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': '123'  # Too weak
        }
        
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'VALIDATION_ERROR' in response_data['code']
    
    def test_login_success(self, client):
        """Test successful login"""
        # First register a user
        register_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'SecurePass123!'
        }
        client.post('/api/v1/auth/register',
                   data=json.dumps(register_data),
                   content_type='application/json')
        
        # Then login
        login_data = {
            'email': 'john@example.com',
            'password': 'SecurePass123!'
        }
        
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'access_token' in response_data['data']
        assert 'refresh_token' in response_data['data']
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword123!'
        }
        
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'INVALID_CREDENTIALS' in response_data['code']
    
    def test_get_profile_authenticated(self, client):
        """Test getting profile with authentication"""
        # Register and login to get token
        register_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'SecurePass123!'
        }
        register_response = client.post('/api/v1/auth/register',
                                      data=json.dumps(register_data),
                                      content_type='application/json')
        
        register_data = json.loads(register_response.data)
        token = register_data['data']['access_token']
        
        # Get profile
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/v1/auth/profile', headers=headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['email'] == 'john@example.com'
    
    def test_get_profile_unauthenticated(self, client):
        """Test getting profile without authentication"""
        response = client.get('/api/v1/auth/profile')
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert 'MISSING_TOKEN' in response_data['code']
    
    def test_update_profile(self, client):
        """Test updating user profile"""
        # Register and login to get token
        register_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'SecurePass123!'
        }
        register_response = client.post('/api/v1/auth/register',
                                      data=json.dumps(register_data),
                                      content_type='application/json')
        
        register_data = json.loads(register_response.data)
        token = register_data['data']['access_token']
        
        # Update profile
        update_data = {
            'name': 'John Smith',
            'phone': '+1234567890',
            'address': '123 Main St'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.put('/api/v1/auth/profile',
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['name'] == 'John Smith'
        assert response_data['data']['phone'] == '+1234567890'


class TestJewelryEndpoints:
    """Test jewelry endpoints"""
    
    def get_auth_token(self, client):
        """Helper to get authentication token"""
        register_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'SecurePass123!'
        }
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(register_data),
                             content_type='application/json')
        
        data = json.loads(response.data)
        return data['data']['access_token']
    
    def test_submit_sell_request(self, client):
        """Test submitting a sell request"""
        token = self.get_auth_token(client)
        
        sell_request_data = {
            'title': 'Diamond Ring',
            'description': 'Beautiful 2-carat diamond ring',
            'photos': ['photo1.jpg', 'photo2.jpg'],
            'attributes': {'material': 'gold', 'weight': '5.2g'},
            'weight': 5.2,
            'seller_notes': 'Inherited from grandmother'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.post('/api/v1/jewelry/sell-requests',
                             data=json.dumps(sell_request_data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'sell_request_id' in response_data['data']
        assert 'jewelry_code' in response_data['data']
    
    def test_list_jewelry_items(self, client):
        """Test listing jewelry items"""
        response = client.get('/api/v1/jewelry/items')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'items' in response_data['data']
        assert 'pagination' in response_data['data']
    
    def test_get_my_jewelry_items_authenticated(self, client):
        """Test getting user's jewelry items"""
        token = self.get_auth_token(client)
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/v1/jewelry/my-items', headers=headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'items' in response_data['data']
    
    def test_get_my_jewelry_items_unauthenticated(self, client):
        """Test getting user's jewelry items without authentication"""
        response = client.get('/api/v1/jewelry/my-items')
        
        assert response.status_code == 401
