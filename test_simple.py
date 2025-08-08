#!/usr/bin/env python3
"""
Simple test to check if books are being found and passed correctly
"""

from app_local import app, mongo
from bson.objectid import ObjectId

def test_simple():
    print("🔍 Simple Test")
    print("=" * 30)
    
    # Test 1: Check if books exist in database
    try:
        books_count = mongo.db.books.count_documents({})
        print(f"✅ Total books in database: {books_count}")
        
        if books_count > 0:
            # Get first book
            first_book = mongo.db.books.find_one()
            print(f"✅ First book: {first_book.get('title', 'NO TITLE')}")
        else:
            print("❌ No books in database!")
            return
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Test 2: Simulate the index route query
    try:
        query = {}
        sort_field, sort_dir = ("upload_date", -1)
        books = list(mongo.db.books.find(query).sort(sort_field, sort_dir))
        print(f"✅ Found {len(books)} books with empty query")
        
        if books:
            print(f"✅ First book from query: {books[0].get('title', 'NO TITLE')}")
        else:
            print("❌ No books found with query!")
    except Exception as e:
        print(f"❌ Query error: {e}")
        return
    
    # Test 3: Check template rendering
    try:
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ Homepage response status: {response.status_code}")
            
            if response.status_code == 200:
                html = response.get_data(as_text=True)
                if "No books found" in html:
                    print("❌ Template shows 'No books found'")
                elif "DEBUG: Number of books: 0" in html:
                    print("❌ Template shows 0 books")
                else:
                    print("✅ Template rendered successfully")
                    # Look for book titles in HTML
                    if any(book.get('title', '').lower() in html.lower() for book in books[:3]):
                        print("✅ Book titles found in HTML")
                    else:
                        print("❌ No book titles found in HTML")
            else:
                print(f"❌ Homepage returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Template test error: {e}")

if __name__ == "__main__":
    test_simple() 