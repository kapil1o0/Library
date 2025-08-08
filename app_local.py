import sys
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify, session, abort, flash
from flask_pymongo import PyMongo
import os
import secrets
import traceback
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Set secret key for sessions from environment variable
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Local MongoDB URI with fallback
app.config["MONGO_URI"] = os.getenv('MONGO_URI_LOCAL', 'mongodb://localhost:27017/library')

print(f"🔧 MongoDB URI: {app.config['MONGO_URI']}")

try:
    mongo = PyMongo(app)
    print("✅ PyMongo initialized successfully")
except Exception as e:
    print(f"❌ PyMongo initialization failed: {e}")

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Helper function to get user name from user_id
def get_user_name(user_id):
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return user.get('name', 'Unknown User') if user else 'Unknown User'
    except:
        return 'Unknown User'

# Register get_user_name with Jinja
app.jinja_env.globals.update(get_user_name=get_user_name)

# Test database connection
@app.route("/test-db")
def test_db():
    try:
        print("🔍 Testing database connection...")
        db_list = mongo.db.list_collection_names()
        print(f"✅ Database connected! Collections: {db_list}")
        
        books_count = mongo.db.books.count_documents({})
        users_count = mongo.db.users.count_documents({})
        
        sample_book = mongo.db.books.find_one()
        
        return jsonify({
            "status": "success",
            "message": "Database connected successfully",
            "collections": db_list,
            "books_count": books_count,
            "users_count": users_count,
            "sample_book": sample_book
        })
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }), 500

# Debug route to check what's in the database
@app.route("/debug-data")
def debug_data():
    try:
        print("🐛 Debug data route called")
        
        books = list(mongo.db.books.find().limit(5))
        users = list(mongo.db.users.find().limit(5))
        
        for book in books:
            book['_id'] = str(book['_id'])
            if 'upload_date' in book:
                book['upload_date'] = str(book['upload_date'])
            if 'uploaded_by' in book:
                book['uploaded_by_name'] = get_user_name(book['uploaded_by'])
                
        for user in users:
            user['_id'] = str(user['_id'])
            
        print(f"🐛 Found {len(books)} books and {len(users)} users")
        
        return jsonify({
            "books": books,
            "users": users,
            "total_books": mongo.db.books.count_documents({}),
            "total_users": mongo.db.users.count_documents({})
        })
    except Exception as e:
        print(f"❌ Debug data error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Folder to store uploaded books
UPLOAD_FOLDER = os.path.join('static', 'books')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("🚀 Flask server has started...")
print(f"📁 Upload folder: {UPLOAD_FOLDER}")

@app.route("/", methods=["GET", "POST"])
def index():
    print("🏠 Index route called")
    sys.stdout.flush()
    try:
        if request.method == "POST":
            search_term = request.form.get("search", "").strip()
            args = request.args.to_dict()
            print(f"📝 POST request with search term: '{search_term}'")
        else:
            search_term = request.args.get("search", "").strip()
            args = request.args.to_dict()
            print(f"🔍 GET request with search term: '{search_term}'")
        
        print(f"📋 Request args: {args}")

        author = request.args.get("author", "")
        year = request.args.get("year", "")
        subject = request.args.get("subject", "")
        language = request.args.get("language", "")
        sort = request.args.get("sort", "")

        print(f"🔧 Filters - Author: '{author}', Year: '{year}', Subject: '{subject}', Language: '{language}', Sort: '{sort}'")

        query = {}
        if search_term:
            query["$or"] = [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"author": {"$regex": search_term, "$options": "i"}},
                {"subject": {"$regex": search_term, "$options": "i"}},
                {"tags": {"$regex": search_term, "$options": "i"}},
            ]
        if author:
            query["author"] = author
        if year:
            try:
                query["year"] = int(year)
            except:
                pass
        if subject:
            query["subject"] = subject
        if language:
            query["language"] = language

        print(f"🔍 MongoDB Query: {query}")

        sort_map = {
            "title": ("title", 1),
            "year": ("year", -1),
            "downloads": ("downloads", -1),
            "": ("upload_date", -1),
        }
        sort_field, sort_dir = sort_map.get(sort, ("upload_date", -1))
        print(f"📊 Sorting by: {sort_field} ({sort_dir})")

        print("📡 Connecting to MongoDB...")
        try:
            db = mongo.cx['library']
            books_collection = db['books']
            print(f"✅ Connected to database: {db.name}")
            
            total_books = books_collection.count_documents({})
            print(f"📚 Total books in collection: {total_books}")
            
            if total_books == 0:
                print("⚠️ No books found in the collection!")
                collections = db.list_collection_names()
                print(f"📋 Available collections: {collections}")
            
            books_cursor = books_collection.find(query).sort(sort_field, sort_dir)
            books = list(books_cursor)
            for book in books:
                book['_id'] = str(book['_id'])  # Convert ObjectId to string
            
            print(f"🎯 Number of books found with query: {len(books)}")
            
            for i, book in enumerate(books[:3]):
                print(f"📖 Book {i+1}: {book.get('title', 'No title')} by {book.get('author', 'Unknown author')}")

        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
            print(f"📊 Error details: {traceback.format_exc()}")
            return render_template("index.html", books=[], error=f"Database error: {str(db_error)}")

        try:
            print("📋 Getting filter dropdown values...")
            authors = sorted(db.books.distinct("author"))
            years = sorted(set([b.get("year") for b in db.books.find({}, {"year": 1}) if b.get("year")]))
            subjects = sorted(db.books.distinct("subject"))
            languages = sorted(db.books.distinct("language"))
            
            print(f"👥 Authors: {len(authors)} found")
            print(f"📅 Years: {len(years)} found")
            print(f"📚 Subjects: {len(subjects)} found")
            print(f"🌐 Languages: {len(languages)} found")
            
        except Exception as filter_error:
            print(f"❌ Error getting filter values: {filter_error}")
            authors = years = subjects = languages = []

        print("🎨 Rendering template...")
        return render_template(
            "index.html",
            books=books,
            authors=authors,
            years=years,
            subjects=subjects,
            languages=languages,
            selected_author=author,
            selected_year=year,
            selected_subject=subject,
            selected_language=language,
            search_term=search_term,
            sort=sort,
            logged_in='logged_in' in session,
            is_admin=(session.get('role') == 'admin')
        )
        
    except Exception as e:
        error_msg = f"Error in index(): {str(e)}"
        print(f"❌ {error_msg}")
        print(f"📊 Full traceback: {traceback.format_exc()}")
        return render_template("index.html", books=[], error=f"Database error: {str(e)}")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    print("📤 Upload route called")
    if 'role' not in session:
        print("❌ User not logged in, redirecting to login")
        return redirect(url_for('login'))
    
    if session['role'] == 'admin':
        print("⚠️ Admin tried to access upload page")
        return render_template("upload.html", error="Admins cannot upload books. Use the admin panel to manage books.")
    
    if request.method == "POST":
        print("📝 Processing upload POST request")
        try:
            form = request.form
            file = request.files["file"]
            cover = request.files.get("cover")

            print(f"📄 File: {file.filename if file else 'None'}")
            print(f"🖼️ Cover: {cover.filename if cover and cover.filename else 'None'}")

            if file and file.filename.endswith(".pdf"):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                print(f"💾 File saved to: {filepath}")

                cover_filename = None
                if cover and cover.filename != '':
                    cover_filename = secure_filename(cover.filename)
                    cover_folder = os.path.join('static', 'covers')
                    os.makedirs(cover_folder, exist_ok=True)
                    cover_path = os.path.join(cover_folder, cover_filename)
                    cover.save(cover_path)
                    print(f"🖼️ Cover saved to: {cover_path}")

                book_data = {
                    "title": form["title"],
                    "author": form["author"],
                    "subject": form["subject"],
                    "description": form.get("description", ""),
                    "isbn": form.get("isbn", ""),
                    "publisher": form.get("publisher", ""),
                    "language": form.get("language", ""),
                    "year": int(form.get("year", 0)) if form.get("year") else 0,
                    "tags": [tag.strip() for tag in form.get("tags", "").split(",") if tag.strip()],
                    "filename": filename,
                    "cover_filename": cover_filename,
                    "upload_date": datetime.now(),
                    "downloads": 0,
                    "uploaded_by": session.get('user_id', 'unknown')
                }
                
                print(f"📊 Book data to insert: {book_data}")
                result = mongo.db.books.insert_one(book_data)
                
                print(f"✅ Book uploaded successfully! ID: {result.inserted_id}")
                return redirect(url_for('index'))
            else:
                print("❌ Invalid file type")
                return render_template("upload.html", error="Please upload a valid PDF file")
        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            print(f"📊 Upload error traceback: {traceback.format_exc()}")
            return render_template("upload.html", error=f"Upload failed: {str(e)}")

    return render_template("upload.html")

@app.route("/download/<book_id>")
def download(book_id):
    print(f"⬇️ Download requested for book ID: {book_id}")
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    if not book:
        print("❌ Book not found")
        abort(404)

    user_id = session.get('user_id')
    can_download = False
    
    if session.get('role') == 'admin':
        can_download = True
        print("✅ Admin can download")
    elif user_id and user_id in book.get('allowed_users', []):
        can_download = True
        print("✅ User has download permission")
    
    if can_download:
        mongo.db.books.update_one({"_id": ObjectId(book_id)}, {"$inc": {"downloads": 1}})
        print(f"📥 Download count incremented for: {book.get('title')}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], book['filename'], as_attachment=True)
    else:
        print("❌ Download not allowed for user")
        return render_template("access_denied.html", message="Download not allowed. You can only preview this book online.")

@app.route("/preview/<book_id>")
def preview(book_id):
    print(f"👁️ Preview requested for book ID: {book_id}")
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    if not book:
        print("❌ Book not found for preview")
        abort(404)

    if not book.get("filename"):
        print("❌ No file available for preview")
        return "No file to preview.", 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], book['filename'])
    if not os.path.exists(file_path):
        print(f"❌ File not found at: {file_path}")
        return "File not found or inaccessible.", 404

    file_url = url_for('static', filename=f"books/{book['filename']}")
    print(f"🔗 Preview URL: {file_url}")
    return render_template("preview.html", book=book, file_url=file_url)

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("👤 Register route called")
    if request.method == 'POST':
        print("📝 Processing registration")
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm = request.form['confirm_password']
        role = request.form['role']
        
        print(f"👤 Registration attempt: {name} ({email}) as {role}")
        
        if not name:
            print("❌ Name is required")
            return render_template('register.html', error='Name is required')
        if password != confirm:
            print("❌ Passwords do not match")
            return render_template('register.html', error='Passwords do not match')
        if mongo.db.users.find_one({'email': email}):
            print("❌ Email already registered")
            return render_template('register.html', error='Email already registered')
        
        hash_pw = generate_password_hash(password)
        result = mongo.db.users.insert_one({
            'name': name,
            'email': email, 
            'password': hash_pw, 
            'role': role
        })
        print(f"✅ User registered successfully with ID: {result.inserted_id}")
        return redirect(url_for('login'))
    return render_template('register.html', error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("🔐 Login route called")
    if request.method == 'POST':
        print("📝 Processing login")
        email = request.form['email'].strip().lower()
        password = request.form['password']
        
        print(f"🔍 Login attempt for: {email}")
        user = mongo.db.users.find_one({'email': email})
        
        if user:
            print(f"👤 User found: {user.get('name')} ({user.get('role')})")
            if check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['name'] = user.get('name', 'Unknown User')
                session['email'] = user['email']
                session['role'] = user['role']
                session['logged_in'] = True
                print(f"✅ Login successful for {user.get('name')}")
                return redirect(url_for('index'))
            else:
                print("❌ Invalid password")
        else:
            print("❌ User not found")
            
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    print(f"👋 Logout for user: {session.get('name', 'Unknown')}")
    session.clear()
    return redirect(url_for('index'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            print("❌ Admin access required, redirecting to login")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/allow_download/<book_id>/<user_id>")
@admin_required
def allow_download(book_id, user_id):
    print(f"✅ Admin allowing download for user {user_id} on book {book_id}")
    mongo.db.books.update_one({"_id": ObjectId(book_id)}, {"$addToSet": {"allowed_users": user_id}})
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route("/admin/disallow_download/<book_id>/<user_id>")
@admin_required
def disallow_download(book_id, user_id):
    print(f"❌ Admin removing download permission for user {user_id} on book {book_id}")
    mongo.db.books.update_one({"_id": ObjectId(book_id)}, {"$pull": {"allowed_users": user_id}})
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    print("🔧 Admin dashboard accessed")
    books = list(mongo.db.books.find())
    for book in books:
        book['_id'] = str(book['_id'])
    users = list(mongo.db.users.find())
    print(f"📚 Admin dashboard: {len(books)} books, {len(users)} users")
    return render_template("admin.html", books=books, users=users)

@app.route("/admin/add", methods=["GET", "POST"])
@admin_required
def admin_add():
    print("➕ Admin add book route")
    if request.method == "POST":
        print("📝 Admin adding new book")
        form = request.form
        file = request.files.get("file")
        cover = request.files.get("cover")
        filename = None
        cover_filename = None
        external_link = form.get("external_link", "")
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"💾 Admin uploaded file: {filename}")
            
        if cover and cover.filename:
            cover_filename = secure_filename(cover.filename)
            cover_folder = os.path.join('static', 'covers')
            os.makedirs(cover_folder, exist_ok=True)
            cover.save(os.path.join(cover_folder, cover_filename))
            print(f"🖼️ Admin uploaded cover: {cover_filename}")
            
        book_data = {
            "title": form["title"],
            "author": form["author"],
            "subject": form["subject"],
            "description": form.get("description", ""),
            "isbn": form.get("isbn", ""),
            "publisher": form.get("publisher", ""),
            "edition": form.get("edition", ""),
            "language": form.get("language", ""),
            "year": int(form.get("year", 0)) if form.get("year") else 0,
            "tags": [tag.strip() for tag in form.get("tags", "").split(",") if tag.strip()],
            "keywords": [kw.strip() for kw in form.get("keywords", "").split(",") if kw.strip()],
            "filename": filename,
            "external_link": external_link,
            "cover_filename": cover_filename,
            "upload_date": datetime.now(),
            "downloads": 0,
            "uploaded_by": session.get('user_id', 'unknown')
        }
        
        result = mongo.db.books.insert_one(book_data)
        print(f"✅ Admin added book successfully! ID: {result.inserted_id}")
        return redirect(url_for('admin_dashboard'))
    return render_template("admin_book_form.html", book=None)

@app.route("/admin/edit/<book_id>", methods=["GET", "POST"])
@admin_required
def admin_edit(book_id):
    print(f"✏️ Admin editing book: {book_id}")
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    if request.method == "POST":
        print("📝 Admin updating book")
        form = request.form
        file = request.files.get("file")
        cover = request.files.get("cover")
        filename = book.get("filename")
        cover_filename = book.get("cover_filename")
        external_link = form.get("external_link", book.get("external_link", ""))
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"💾 Admin updated file: {filename}")
            
        if cover and cover.filename:
            cover_filename = secure_filename(cover.filename)
            cover_folder = os.path.join('static', 'covers')
            os.makedirs(cover_folder, exist_ok=True)
            cover.save(os.path.join(cover_folder, cover_filename))
            print(f"🖼️ Admin updated cover: {cover_filename}")
            
        mongo.db.books.update_one({"_id": ObjectId(book_id)}, {"$set": {
            "title": form["title"],
            "author": form["author"],
            "subject": form["subject"],
            "description": form.get("description", ""),
            "isbn": form.get("isbn", ""),
            "publisher": form.get("publisher", ""),
            "edition": form.get("edition", ""),
            "language": form.get("language", ""),
            "year": int(form.get("year", 0)) if form.get("year") else 0,
            "tags": [tag.strip() for tag in form.get("tags", "").split(",") if tag.strip()],
            "keywords": [kw.strip() for kw in form.get("keywords", "").split(",") if kw.strip()],
            "filename": filename,
            "external_link": external_link,
            "cover_filename": cover_filename
        }})
        print(f"✅ Admin updated book successfully!")
        return redirect(url_for('admin_dashboard'))
    return render_template("admin_book_form.html", book=book)

@app.route("/admin/delete/<book_id>")
@admin_required
def admin_delete(book_id):
    print(f"🗑️ Admin deleting book: {book_id}")
    result = mongo.db.books.delete_one({"_id": ObjectId(book_id)})
    print(f"✅ Deleted {result.deleted_count} book(s)")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/users")
@admin_required
def admin_users():
    print("👥 Admin users page accessed")
    users = list(mongo.db.users.find())
    print(f"👥 Found {len(users)} users")
    return render_template("admin_users.html", users=users)

@app.route('/admin/access', methods=['GET', 'POST'])
@admin_required
def manage_access():
    print("🔐 Admin access management")
    users = list(mongo.db.users.find({'role': 'user'}))
    books = list(mongo.db.books.find())
    for book in books:
        book['_id'] = str(book['_id'])
    print(f"🔐 Managing access for {len(users)} users and {len(books)} books")

    if request.method == 'POST':
        user_id = request.form['user_id']
        selected_books = request.form.getlist('books')
        print(f"🔐 Updating access for user {user_id} with books: {selected_books}")

        try:
            if not ObjectId.is_valid(user_id):
                flash("Invalid user ID.", "error")
                return redirect(url_for('manage_access'))

            mongo.db.books.update_many(
                {"allowed_users": user_id},
                {"$pull": {"allowed_users": user_id}}
            )

            for book_id in selected_books:
                if ObjectId.is_valid(book_id):
                    mongo.db.books.update_one(
                        {'_id': ObjectId(book_id)},
                        {'$addToSet': {'allowed_users': user_id}}
                    )
                else:
                    print(f"❌ Invalid book ID: {book_id}")
            
            flash("Access updated successfully.", "success")
        except Exception as e:
            print(f"❌ Error updating access: {str(e)}")
            flash(f"Error updating access: {str(e)}", "error")
        
        return redirect(url_for('manage_access'))

    return render_template('admin_manage_access.html', users=users, books=books)

@app.route("/admin/user/<user_id>")
@admin_required
def admin_user_detail(user_id):
    print(f"👤 Admin viewing user details: {user_id}")
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        print("❌ User not found")
        return redirect(url_for('admin_users'))
    
    user_books = list(mongo.db.books.find({"uploaded_by": user_id}))
    for book in user_books:
        book['_id'] = str(book['_id'])
    print(f"📚 User {user.get('name')} has uploaded {len(user_books)} books")
    return render_template("admin_user_detail.html", user=user, books=user_books, is_admin=(session.get('role') == 'admin'))

@app.route("/admin/user/delete/<user_id>")
@admin_required
def admin_delete_user(user_id):
    print(f"🗑️ Admin deleting user: {user_id}")
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user and user.get('role') != 'admin':
        result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        print(f"✅ Deleted {result.deleted_count} user(s)")
    else:
        print("❌ Cannot delete admin user")
    return redirect(url_for('admin_users'))

@app.route("/admin/user/toggle_role/<user_id>")
@admin_required
def admin_toggle_user_role(user_id):
    print(f"🔄 Admin toggling user role: {user_id}")
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        new_role = 'admin' if user.get('role') == 'user' else 'user'
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)}, 
            {"$set": {"role": new_role}}
        )
        print(f"✅ Changed user role to: {new_role}")
    return redirect(url_for('admin_users'))

@app.route('/book/<book_id>')
def book_detail(book_id):
    print(f"📖 Book detail requested: {book_id}")
    book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    if not book:
        print("❌ Book not found for detail view")
        return render_template('book_detail.html', error='Book not found', book=None, is_admin=(session.get('role') == 'admin'))
    
    book['_id'] = str(book['_id'])  # Convert ObjectId to string
    can_download = session.get('role') == 'admin'
    print(f"⬇️ Can download: {can_download}")
    
    file_size = None
    if book.get('filename'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], book['filename'])
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"📁 File size: {file_size} bytes")
    
    return render_template('book_detail.html', book=book, file_size=file_size, can_download=can_download, is_admin=(session.get('role') == 'admin'))

if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    print(f"🔧 Debug mode: True")
    print(f"📡 MongoDB URI: {app.config['MONGO_URI']}")
    app.run(debug=True, host='0.0.0.0', port=5000)