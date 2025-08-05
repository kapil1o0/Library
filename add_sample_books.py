#!/usr/bin/env python3
"""
Sample Books Generator for Library Management System
This script adds sample books to the database for testing.
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random

def add_sample_books():
    """Add sample books to the database."""
    
    # Connect to local MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client.library
    
    # Sample book data
    sample_books = [
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "subject": "Fiction",
            "description": "A story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.",
            "isbn": "978-0743273565",
            "publisher": "Scribner",
            "language": "English",
            "year": 1925,
            "tags": ["classic", "romance", "drama"],
            "filename": "the_great_gatsby.pdf",
            "cover_filename": "gatsby_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 150)
        },
        {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "subject": "Fiction",
            "description": "The story of young Scout Finch and her father Atticus in a racially divided Alabama town.",
            "isbn": "978-0446310789",
            "publisher": "Grand Central Publishing",
            "language": "English",
            "year": 1960,
            "tags": ["classic", "drama", "social-issues"],
            "filename": "to_kill_a_mockingbird.pdf",
            "cover_filename": "mockingbird_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 200)
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "subject": "Science Fiction",
            "description": "A dystopian novel about totalitarianism and surveillance society.",
            "isbn": "978-0451524935",
            "publisher": "Signet Classic",
            "language": "English",
            "year": 1949,
            "tags": ["dystopian", "political", "classic"],
            "filename": "1984.pdf",
            "cover_filename": "1984_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 300)
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "subject": "Romance",
            "description": "The story of Elizabeth Bennet and Mr. Darcy in Georgian-era England.",
            "isbn": "978-0141439518",
            "publisher": "Penguin Classics",
            "language": "English",
            "year": 1813,
            "tags": ["romance", "classic", "historical"],
            "filename": "pride_and_prejudice.pdf",
            "cover_filename": "pride_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 180)
        },
        {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "subject": "Fantasy",
            "description": "The adventure of Bilbo Baggins, a hobbit who embarks on a quest with thirteen dwarves.",
            "isbn": "978-0547928241",
            "publisher": "Houghton Mifflin Harcourt",
            "language": "English",
            "year": 1937,
            "tags": ["fantasy", "adventure", "classic"],
            "filename": "the_hobbit.pdf",
            "cover_filename": "hobbit_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 250)
        },
        {
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "subject": "Fiction",
            "description": "The story of Holden Caulfield, a teenager navigating the complexities of growing up.",
            "isbn": "978-0316769488",
            "publisher": "Little, Brown and Company",
            "language": "English",
            "year": 1951,
            "tags": ["coming-of-age", "classic", "drama"],
            "filename": "catcher_in_the_rye.pdf",
            "cover_filename": "catcher_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 120)
        },
        {
            "title": "Lord of the Flies",
            "author": "William Golding",
            "subject": "Fiction",
            "description": "A group of British boys stranded on an uninhabited island and their attempt to govern themselves.",
            "isbn": "978-0399501487",
            "publisher": "Penguin Books",
            "language": "English",
            "year": 1954,
            "tags": ["drama", "survival", "classic"],
            "filename": "lord_of_the_flies.pdf",
            "cover_filename": "flies_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 90)
        },
        {
            "title": "Animal Farm",
            "author": "George Orwell",
            "subject": "Political Fiction",
            "description": "An allegorical novella about farm animals who rebel against their human farmer.",
            "isbn": "978-0451526342",
            "publisher": "Signet",
            "language": "English",
            "year": 1945,
            "tags": ["political", "allegory", "classic"],
            "filename": "animal_farm.pdf",
            "cover_filename": "animal_farm_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 160)
        },
        {
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "subject": "Philosophy",
            "description": "A novel about a young Andalusian shepherd who dreams of finding a worldly treasure.",
            "isbn": "978-0062315007",
            "publisher": "HarperOne",
            "language": "English",
            "year": 1988,
            "tags": ["philosophy", "adventure", "inspirational"],
            "filename": "the_alchemist.pdf",
            "cover_filename": "alchemist_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 220)
        },
        {
            "title": "The Little Prince",
            "author": "Antoine de Saint-Exupéry",
            "subject": "Children's Literature",
            "description": "A poetic tale about a young prince who visits various planets in space.",
            "isbn": "978-0156013987",
            "publisher": "Mariner Books",
            "language": "English",
            "year": 1943,
            "tags": ["children", "philosophy", "classic"],
            "filename": "the_little_prince.pdf",
            "cover_filename": "prince_cover.jpg",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 140)
        }
    ]
    
    try:
        print("📚 Adding sample books to the database...")
        
        # Clear existing books (optional - comment out if you want to keep existing books)
        # db.books.delete_many({})
        # print("🗑️ Cleared existing books")
        
        # Insert sample books
        result = db.books.insert_many(sample_books)
        print(f"✅ Successfully added {len(result.inserted_ids)} sample books!")
        
        # Show added books
        print("\n📋 Added books:")
        for book in sample_books:
            print(f"  📖 {book['title']} by {book['author']} ({book['year']})")
            print(f"     Subject: {book['subject']} | Downloads: {book['downloads']}")
            print()
        
        # Show database stats
        total_books = db.books.count_documents({})
        print(f"📊 Total books in database: {total_books}")
        
        # Show subjects breakdown
        subjects = db.books.aggregate([
            {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        
        print("\n📈 Books by subject:")
        for subject in subjects:
            print(f"  {subject['_id']}: {subject['count']} books")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding sample books: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Sample Books Generator")
    print("=" * 40)
    success = add_sample_books()
    if success:
        print("\n✅ Sample books added successfully!")
        print("🎉 You can now test all the library features!")
    else:
        print("\n❌ Failed to add sample books!") 