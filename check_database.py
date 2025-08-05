#!/usr/bin/env python3
"""
Database checker script to verify what's in the database.
"""

from pymongo import MongoClient
import json

def check_atlas_database():
    """Check MongoDB Atlas database."""
    print("🔍 Checking MongoDB Atlas Database...")
    
    uri = "mongodb+srv://mkapilnaths:1534mNSuGkRkri01@clustercoolie.pui72w6.mongodb.net/library?retryWrites=true&w=majority"
    
    try:
        client = MongoClient(uri, tlsAllowInvalidCertificates=True)
        db = client.library
        
        # Check collections
        collections = db.list_collection_names()
        print(f"📚 Collections found: {collections}")
        
        if 'books' in collections:
            # Count books
            book_count = db.books.count_documents({})
            print(f"📖 Total books in database: {book_count}")
            
            if book_count > 0:
                # Show recent books
                recent_books = db.books.find().sort("upload_date", -1).limit(5)
                print("\n📋 Recent books:")
                for book in recent_books:
                    print(f"  - {book.get('title', 'No title')} by {book.get('author', 'Unknown')}")
                    print(f"    Uploaded: {book.get('upload_date', 'Unknown')}")
                    print(f"    Downloads: {book.get('downloads', 0)}")
                    print()
            else:
                print("📝 No books found in database")
        else:
            print("📝 No 'books' collection found")
            
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Atlas connection failed: {str(e)}")
        return False

def check_local_database():
    """Check local MongoDB database."""
    print("\n🔍 Checking Local MongoDB Database...")
    
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client.library
        
        # Check collections
        collections = db.list_collection_names()
        print(f"📚 Collections found: {collections}")
        
        if 'books' in collections:
            # Count books
            book_count = db.books.count_documents({})
            print(f"📖 Total books in database: {book_count}")
            
            if book_count > 0:
                # Show recent books
                recent_books = db.books.find().sort("upload_date", -1).limit(5)
                print("\n📋 Recent books:")
                for book in recent_books:
                    print(f"  - {book.get('title', 'No title')} by {book.get('author', 'Unknown')}")
                    print(f"    Uploaded: {book.get('upload_date', 'Unknown')}")
                    print(f"    Downloads: {book.get('downloads', 0)}")
                    print()
            else:
                print("📝 No books found in database")
        else:
            print("📝 No 'books' collection found")
            
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Local connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Database Status Checker")
    print("=" * 50)
    
    # Check Atlas
    atlas_ok = check_atlas_database()
    
    # Check Local
    local_ok = check_local_database()
    
    print("\n📊 Summary:")
    if atlas_ok:
        print("✅ MongoDB Atlas: Connected")
    else:
        print("❌ MongoDB Atlas: Connection failed")
        
    if local_ok:
        print("✅ Local MongoDB: Connected")
    else:
        print("❌ Local MongoDB: Not available") 