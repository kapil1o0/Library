#!/usr/bin/env python3
"""
Simple MongoDB connection test script.
This script tests the MongoDB Atlas connection independently.
"""

from pymongo import MongoClient
import sys
import ssl

def test_mongodb_connection():
    """Test MongoDB Atlas connection directly."""
    
    # MongoDB Atlas URI - Updated with correct credentials
    uri = "mongodb+srv://mkapilnaths:1534mNSuGkRkri01@clustercoolie.pui72w6.mongodb.net/library?retryWrites=true&w=majority"
    
    try:
        print("🔍 Testing MongoDB Atlas connection...")
        
        # Create client with SSL configuration
        client = MongoClient(uri, tlsAllowInvalidCertificates=True)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # List databases
        databases = client.list_database_names()
        print(f"📊 Available databases: {databases}")
        
        # Test library database
        db = client.library
        collections = db.list_collection_names()
        print(f"📚 Collections in 'library' database: {collections}")
        
        # Test books collection
        if 'books' in collections:
            book_count = db.books.count_documents({})
            print(f"📖 Found {book_count} books in the collection")
        else:
            print("📝 No 'books' collection found (this is normal for a new database)")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        print("\n🔧 Possible solutions:")
        print("   1. Check your internet connection")
        print("   2. Verify the MongoDB Atlas credentials")
        print("   3. Ensure the cluster is running")
        print("   4. Check if your IP is whitelisted in MongoDB Atlas")
        print("   5. Verify the database user has proper permissions")
        return False

if __name__ == "__main__":
    print("🚀 MongoDB Connection Test")
    print("=" * 40)
    success = test_mongodb_connection()
    if success:
        print("\n✅ Connection test completed successfully!")
    else:
        print("\n❌ Connection test failed!")
        sys.exit(1) 