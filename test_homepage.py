#!/usr/bin/env python3
"""
Test script to check homepage functionality
"""

from app_local import app, mongo
from bson.objectid import ObjectId

def test_homepage():
    print("🔍 Testing Homepage Functionality")
    print("=" * 50)
    
    # Test database connection
    try:
        books_count = mongo.db.books.count_documents({})
        print(f"✅ Database connected. Total books: {books_count}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test simple query (no filters)
    try:
        books = list(mongo.db.books.find({}).sort("upload_date", -1))
        print(f"✅ Found {len(books)} books with empty query")
        
        if books:
            print(f"📖 First book: {books[0]['title']} by {books[0]['author']}")
            print(f"📖 Last book: {books[-1]['title']} by {books[-1]['author']}")
        else:
            print("⚠️  No books found!")
            
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    # Test with app context
    with app.test_client() as client:
        try:
            response = client.get('/')
            print(f"✅ Homepage response status: {response.status_code}")
            
            if response.status_code == 200:
                html = response.get_data(as_text=True)
                if "DEBUG: Number of books:" in html:
                    print("✅ Debug comments found in HTML")
                else:
                    print("⚠️  Debug comments not found in HTML")
                    
                # Check if any book titles are in the HTML
                sample_books = list(mongo.db.books.find().limit(3))
                for book in sample_books:
                    if book['title'] in html:
                        print(f"✅ Found book '{book['title']}' in HTML")
                    else:
                        print(f"❌ Book '{book['title']}' not found in HTML")
            else:
                print(f"❌ Homepage returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test client failed: {e}")

if __name__ == "__main__":
    test_homepage() 