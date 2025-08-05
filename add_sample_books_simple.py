#!/usr/bin/env python3
"""
Simple Sample Books Generator
This script adds sample books with basic files for testing.
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import os

def create_placeholder_pdf(filename, title, author):
    """Create a placeholder PDF file for the book."""
    try:
        # Create a simple text file as placeholder
        pdf_path = os.path.join('static', 'books', filename)
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Author: {author}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "="*50 + "\n")
            f.write("This is a placeholder file for testing purposes.\n")
            f.write("In a real application, this would be the actual book content.\n")
            f.write("="*50 + "\n")
        return True
    except Exception as e:
        print(f"❌ Error creating PDF for {title}: {str(e)}")
        return False

def create_simple_cover(filename, title, author):
    """Create a simple HTML cover file."""
    try:
        # Create a simple HTML file as cover
        cover_path = os.path.join('static', 'covers', filename.replace('.jpg', '.html'))
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-family: Arial, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}
        .cover {{
            background: rgba(0,0,0,0.3);
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        h2 {{
            font-size: 1.5em;
            margin-bottom: 30px;
            opacity: 0.9;
        }}
        .author {{
            font-size: 1.2em;
            font-style: italic;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="cover">
        <h1>{title}</h1>
        <h2>by</h2>
        <div class="author">{author}</div>
    </div>
</body>
</html>
"""
        with open(cover_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return True
    except Exception as e:
        print(f"❌ Error creating cover for {title}: {str(e)}")
        return False

def add_sample_books_simple():
    """Add sample books with simple files to the database."""
    
    # Connect to local MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client.library
    
    # Ensure directories exist
    os.makedirs(os.path.join('static', 'books'), exist_ok=True)
    os.makedirs(os.path.join('static', 'covers'), exist_ok=True)
    
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
            "cover_filename": "gatsby_cover.html",
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
            "cover_filename": "mockingbird_cover.html",
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
            "cover_filename": "1984_cover.html",
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
            "cover_filename": "pride_cover.html",
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
            "cover_filename": "hobbit_cover.html",
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
            "cover_filename": "catcher_cover.html",
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
            "cover_filename": "flies_cover.html",
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
            "cover_filename": "animal_farm_cover.html",
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
            "cover_filename": "alchemist_cover.html",
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
            "cover_filename": "prince_cover.html",
            "upload_date": datetime.now() - timedelta(days=random.randint(1, 30)),
            "downloads": random.randint(0, 140)
        }
    ]
    
    try:
        print("📚 Adding sample books with files...")
        
        # Clear existing books
        db.books.delete_many({})
        print("🗑️ Cleared existing books")
        
        # Create files for each book
        for book in sample_books:
            print(f"📖 Creating files for: {book['title']}")
            
            # Create PDF file
            if create_placeholder_pdf(book['filename'], book['title'], book['author']):
                print(f"  ✅ PDF created: {book['filename']}")
            
            # Create cover file
            if create_simple_cover(book['cover_filename'], book['title'], book['author']):
                print(f"  ✅ Cover created: {book['cover_filename']}")
        
        # Insert books into database
        result = db.books.insert_many(sample_books)
        print(f"\n✅ Successfully added {len(result.inserted_ids)} sample books!")
        
        # Show added books
        print("\n📋 Added books with files:")
        for book in sample_books:
            print(f"  📖 {book['title']} by {book['author']} ({book['year']})")
            print(f"     Subject: {book['subject']} | Downloads: {book['downloads']}")
            print(f"     Files: {book['filename']} | {book['cover_filename']}")
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
        
        # Check if files exist
        print("\n🔍 File verification:")
        for book in sample_books:
            pdf_exists = os.path.exists(os.path.join('static', 'books', book['filename']))
            cover_exists = os.path.exists(os.path.join('static', 'covers', book['cover_filename']))
            print(f"  {book['title']}: PDF {'✅' if pdf_exists else '❌'} | Cover {'✅' if cover_exists else '❌'}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding sample books: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Sample Books Generator")
    print("=" * 40)
    success = add_sample_books_simple()
    if success:
        print("\n✅ Sample books with files added successfully!")
        print("🎉 You can now test downloads and see cover images!")
    else:
        print("\n❌ Failed to add sample books!") 