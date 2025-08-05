#!/usr/bin/env python3
"""
Test Flask application database connection.
This script tests the database connection through the Flask app.
"""

import requests
import time

def test_flask_db():
    """Test the Flask application database connection."""
    
    try:
        print("🔍 Testing Flask application database connection...")
        
        # Wait a moment for the Flask app to start
        time.sleep(2)
        
        # Test the database connection endpoint
        response = requests.get("http://localhost:5000/test-db")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Flask DB Test: {data['message']}")
            print(f"📊 Collections: {data['collections']}")
            return True
        else:
            print(f"❌ Flask DB Test failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask application. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Flask DB Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Flask Database Connection Test")
    print("=" * 40)
    success = test_flask_db()
    if success:
        print("\n✅ Flask database connection test completed successfully!")
    else:
        print("\n❌ Flask database connection test failed!") 