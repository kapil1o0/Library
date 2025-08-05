#!/usr/bin/env python3
"""
Database initialization script for the library application.
This script sets up the database and creates necessary indexes.
"""

from pymongo import MongoClient
from datetime import datetime

def init_database():
    """Initialize the database with indexes and sample data if needed."""
    try:
        # MongoDB Atlas URI
        uri = "mongodb+srv://mkapilnaths:1534mNSuGkRkri01@clustercoolie.pui72w6.mongodb.net/library?retryWrites=true&w=majority"
        
        # Create client with SSL configuration
        client = MongoClient(uri, tlsAllowInvalidCertificates=True)
        db = client.library
        
        # First, test the connection
        print("🔍 Testing database connection...")
        db_list = db.list_collection_names()
        print(f"✅ Connection successful! Found collections: {db_list}")
        
        # Create indexes for better query performance
        print("📊 Creating database indexes...")
        db.books.create_index([("title", 1)])
        db.books.create_index([("author", 1)])
        db.books.create_index([("subject", 1)])
        db.books.create_index([("tags", 1)])
        db.books.create_index([("upload_date", -1)])
        
        print("✅ Database indexes created successfully!")
        
        # Check if we have any books in the database
        book_count = db.books.count_documents({})
        print(f"📚 Found {book_count} books in the database")
        
        if book_count == 0:
            print("📝 No books found. You can add books through the upload page.")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        print("🔧 Troubleshooting tips:")
        print("   1. Check your internet connection")
        print("   2. Verify the MongoDB Atlas URI is correct")
        print("   3. Ensure the MongoDB Atlas cluster is running")
        print("   4. Check if the database user has proper permissions")
        print("   5. Try running: python app.py and visit http://localhost:5000/test-db")
        return False

if __name__ == "__main__":
    print("🚀 Initializing database...")
    success = init_database()
    if success:
        print("✅ Database initialization completed successfully!")
    else:
        print("❌ Database initialization failed!") 