#!/usr/bin/env python3
"""
Simple test script for the new Jewelry Auction System endpoints
Run this after starting the Flask server to test the new endpoints
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000/api/v1"
headers = {"Content-Type": "application/json"}

def test_auth():
    """Test authentication endpoints"""
    print("=== Testing Authentication ===")
    
    # Test register
    register_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "MEMBER"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data, headers=headers)
        print(f"Register: {response.status_code} - {response.json()}")
        
        if response.status_code == 201:
            # Test login
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=headers)
            print(f"Login: {response.status_code} - {response.json()}")
            
            if response.status_code == 200:
                token = response.json()['data']['access_token']
                return token
    except Exception as e:
        print(f"Auth test error: {e}")
    
    return None

def test_jewelry_endpoints(token):
    """Test jewelry endpoints"""
    print("\n=== Testing Jewelry Endpoints ===")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test create jewelry item (need STAFF role)
    jewelry_data = {
        "title": "Test Diamond Ring",
        "description": "A beautiful test diamond ring",
        "photos": ["photo1.jpg", "photo2.jpg"],
        "attributes": {"material": "gold", "weight": "5.2g"},
        "weight": 5.2,
        "estimated_price": 1500.00,
        "reserve_price": 1200.00
    }
    
    try:
        response = requests.post(f"{BASE_URL}/jewelry", json=jewelry_data, headers=auth_headers)
        print(f"Create Jewelry: {response.status_code} - {response.json()}")
        
        # Test list jewelry items
        response = requests.get(f"{BASE_URL}/jewelry/items", headers=headers)
        print(f"List Jewelry: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"Jewelry test error: {e}")

def test_sell_request_endpoints(token):
    """Test sell request endpoints"""
    print("\n=== Testing Sell Request Endpoints ===")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test create sell request
    sell_request_data = {
        "title": "My Diamond Ring",
        "description": "Family heirloom diamond ring",
        "photos": ["ring1.jpg", "ring2.jpg"],
        "attributes": {"material": "platinum", "weight": "4.5g"},
        "weight": 4.5,
        "seller_notes": "Inherited from grandmother"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/sell-requests", json=sell_request_data, headers=auth_headers)
        print(f"Create Sell Request: {response.status_code} - {response.json()}")
        
        # Test list sell requests (need STAFF role)
        response = requests.get(f"{BASE_URL}/sell-requests", headers=auth_headers)
        print(f"List Sell Requests: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"Sell request test error: {e}")

def test_auction_endpoints(token):
    """Test auction endpoints"""
    print("\n=== Testing Auction Endpoints ===")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test create session (need MANAGER role)
    session_data = {
        "name": "Weekly Jewelry Auction #1",
        "description": "Weekly auction featuring premium jewelry items",
        "start_at": (datetime.now() + timedelta(hours=1)).isoformat() + "Z",
        "end_at": (datetime.now() + timedelta(hours=5)).isoformat() + "Z"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auctions/sessions", json=session_data, headers=auth_headers)
        print(f"Create Session: {response.status_code} - {response.json()}")
        
        # Test list sessions
        response = requests.get(f"{BASE_URL}/auctions", headers=headers)
        print(f"List Sessions: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"Auction test error: {e}")

def test_bid_endpoints(token):
    """Test bidding endpoints"""
    print("\n=== Testing Bid Endpoints ===")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test get bids for session item (using dummy IDs)
    session_id = "dummy-session-id"
    item_id = "dummy-item-id"
    
    try:
        response = requests.get(f"{BASE_URL}/bids/sessions/{session_id}/items/{item_id}/bids", headers=headers)
        print(f"Get Session Item Bids: {response.status_code} - {response.json()}")
        
        # Test place bid
        bid_data = {
            "amount": 150.00
        }
        
        response = requests.post(f"{BASE_URL}/bids/sessions/{session_id}/items/{item_id}/bids", 
                               json=bid_data, headers=auth_headers)
        print(f"Place Bid: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"Bid test error: {e}")

def main():
    """Main test function"""
    print("Starting Jewelry Auction System API Tests")
    print("=" * 50)
    
    # Test authentication first
    token = test_auth()
    
    if token:
        print(f"Got auth token: {token[:20]}...")
        
        # Test other endpoints
        test_jewelry_endpoints(token)
        test_sell_request_endpoints(token)
        test_auction_endpoints(token)
        test_bid_endpoints(token)
    else:
        print("Failed to get auth token, skipping other tests")
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == "__main__":
    main()
