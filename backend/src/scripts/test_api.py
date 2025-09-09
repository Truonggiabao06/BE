#!/usr/bin/env python3
"""
API Testing Script for Jewelry Auction System
Tests all main endpoints and authentication
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.user_id = None
        self.session = requests.Session()
        
    def print_result(self, test_name, success, message="", data=None):
        """Print test result with formatting"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        if data and isinstance(data, dict):
            print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
        print()
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            success = response.status_code == 200
            self.print_result("Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_result("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_login(self):
        """Test login endpoint"""
        try:
            login_data = {
                "email": "admin@example.com",
                "password": "Admin@123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/auth",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('access_token'):
                    self.access_token = data['data']['access_token']
                    self.user_id = data['data']['user']['id']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    self.print_result("Login", True, "Token obtained successfully")
                    return True
            
            self.print_result("Login", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
            
        except Exception as e:
            self.print_result("Login", False, f"Error: {str(e)}")
            return False
    
    def test_jewelry_endpoints(self):
        """Test jewelry management endpoints"""
        results = []
        
        # Test GET all jewelry
        try:
            response = self.session.get(f"{self.base_url}/api/v1/jewelry")
            success = response.status_code == 200
            self.print_result("Get All Jewelry", success, f"Status: {response.status_code}")
            results.append(success)
        except Exception as e:
            self.print_result("Get All Jewelry", False, f"Error: {str(e)}")
            results.append(False)
        
        # Test POST create jewelry (requires auth)
        if self.access_token:
            try:
                jewelry_data = {
                    "title": "Test Diamond Ring",
                    "description": "Test jewelry item",
                    "weight": 10.5,
                    "estimated_price": 2000.00,
                    "attributes": {
                        "material": "GOLD",
                        "condition": "EXCELLENT",
                        "category": "RING"
                    }
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/jewelry",
                    json=jewelry_data,
                    headers={"Content-Type": "application/json"}
                )
                success = response.status_code in [200, 201]
                self.print_result("Create Jewelry", success, f"Status: {response.status_code}")
                results.append(success)
            except Exception as e:
                self.print_result("Create Jewelry", False, f"Error: {str(e)}")
                results.append(False)
        
        return all(results)
    
    def test_sell_requests(self):
        """Test sell request endpoints"""
        if not self.access_token:
            self.print_result("Sell Requests", False, "No access token available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/sell-requests")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                count = len(data.get('data', {}).get('items', []))
                self.print_result("Get Sell Requests", True, f"Found {count} sell requests")
            else:
                self.print_result("Get Sell Requests", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Get Sell Requests", False, f"Error: {str(e)}")
            return False
    
    def test_auctions(self):
        """Test auction endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auctions")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                count = len(data.get('auctions', []))
                self.print_result("Get Auctions", True, f"Found {count} auctions")
            else:
                self.print_result("Get Auctions", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Get Auctions", False, f"Error: {str(e)}")
            return False
    
    def test_swagger_docs(self):
        """Test Swagger documentation"""
        try:
            response = self.session.get(f"{self.base_url}/api/docs")
            success = response.status_code == 200
            self.print_result("Swagger Documentation", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_result("Swagger Documentation", False, f"Error: {str(e)}")
            return False

    def test_bidding_endpoints(self):
        """Test bidding endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/bids/sessions/1")
            success = response.status_code == 200

            if success:
                data = response.json()
                count = len(data.get('data', {}).get('items', []))
                self.print_result("Get Session Bids", True, f"Found {count} bids")
            else:
                self.print_result("Get Session Bids", False, f"Status: {response.status_code}")

            return success
        except Exception as e:
            self.print_result("Get Session Bids", False, f"Error: {str(e)}")
            return False

    def test_upload_endpoints(self):
        """Test file upload endpoints"""
        if not self.access_token:
            self.print_result("File Upload", False, "No access token available")
            return False

        try:
            # Create a test file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test document content")
                temp_file_path = f.name

            # Test document upload
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                data = {'document_type': 'test'}

                response = self.session.post(
                    f"{self.base_url}/api/v1/upload/documents",
                    files=files,
                    data=data
                )

            # Clean up
            import os
            os.unlink(temp_file_path)

            success = response.status_code == 200
            if success:
                result = response.json()
                filename = result.get('data', {}).get('filename', 'unknown')
                self.print_result("Document Upload", True, f"Uploaded: {filename}")
            else:
                self.print_result("Document Upload", False, f"Status: {response.status_code}")

            return success
        except Exception as e:
            self.print_result("Document Upload", False, f"Error: {str(e)}")
            return False

    def test_login_endpoints(self):
        """Test both login endpoints"""
        results = []

        # Test /auth endpoint (working)
        try:
            login_data = {
                "email": "admin@example.com",
                "password": "Admin@123"
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/auth/auth",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )

            success = response.status_code == 200
            self.print_result("Login (/auth)", success, f"Status: {response.status_code}")
            results.append(success)
        except Exception as e:
            self.print_result("Login (/auth)", False, f"Error: {str(e)}")
            results.append(False)

        # Test /login endpoint (should work now)
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )

            success = response.status_code == 200
            self.print_result("Login (/login)", success, f"Status: {response.status_code}")
            results.append(success)
        except Exception as e:
            self.print_result("Login (/login)", False, f"Error: {str(e)}")
            results.append(False)

        return all(results)
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Starting Jewelry Auction API Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Login Endpoints", self.test_login_endpoints),
            ("Authentication", self.test_login),
            ("Jewelry Endpoints", self.test_jewelry_endpoints),
            ("Sell Requests", self.test_sell_requests),
            ("Auctions", self.test_auctions),
            ("Bidding", self.test_bidding_endpoints),
            ("File Upload", self.test_upload_endpoints),
            ("Swagger Docs", self.test_swagger_docs),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"🔍 Testing {test_name}...")
            result = test_func()
            results.append((test_name, result))
            print("-" * 30)
        
        # Summary
        print("📊 TEST SUMMARY")
        print("=" * 50)
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API is working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Check the details above.")
            return False


def main():
    """Main function"""
    print(f"🚀 Testing Jewelry Auction API at {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = APITester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
