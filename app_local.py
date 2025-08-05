from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify, session
from flask_pymongo import PyMongo
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Set secret key for sessions
app.secret_key = 'supersecretkey'  # Change this in production

# Local MongoDB URI (for testing when Atlas is down)
app.config["MONGO_URI"] ="mongodb://localhost:27017/library"

mongo = PyMongo(app)

# Test database connection
@app.route("/test-db")
def test_db():
    try:
        # Test the connection by trying to access the database
        db_list = mongo.db.list_collection_names()
        return jsonify({
            "status": "success",
            "message": "Database connected successfully",
            "collections": db_list
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }), 500

# Folder to store uploaded books
UPLOAD_FOLDER = os.path.join('static', 'books')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home + Search + Filtering + Sorting
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        # --- Collect filter/sort/search params ---
        if request.method == "POST":
            # For search bar (POST)
            search_term = request.form.get("search", "").strip()
            args = request.args.to_dict()
        else:
            search_term = request.args.get("search", "").strip()
            args = request.args.to_dict()
        
        # Filters
        author = request.args.get("author", "")
        year = request.args.get("year", "")
        subject = request.args.get("subject", "")
        language = request.args.get("language", "")
        sort = request.args.get("sort", "")

        # --- Build MongoDB query ---
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

        # --- Sorting ---
        sort_map = {
            "title": ("title", 1),
            "year": ("year", -1),
            "downloads": ("downloads", -1),
            "": ("upload_date", -1),  # default: newest first
        }
        sort_field, sort_dir = sort_map.get(sort, ("upload_date", -1))

        books = mongo.db.books.find(query).sort(sort_field, sort_dir)

        # --- Get filter options ---
        authors = sorted(mongo.db.books.distinct("author"))
        years = sorted(set([b.get("year") for b in mongo.db.books.find({}, {"year": 1}) if b.get("year")]))
        subjects = sorted(mongo.db.books.distinct("subject"))
        languages = sorted(mongo.db.books.distinct("language"))

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
        return render_template("index.html", books=[], error=f"Database error: {str(e)}")

# Upload Page - Only for regular users (not admins)
@app.route("/upload", methods=["GET", "POST"])
def upload():
    # Check if user is logged in and is a regular user (not admin)
    if 'role' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'admin':
        return render_template("upload.html", error="Admins cannot upload books. Use the admin panel to manage books.")
    
    if request.method == "POST":
        try:
            form = request.form
            file = request.files["file"]
            cover = request.files.get("cover")

            if file and file.filename.endswith(".pdf"):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Save cover image if provided
                cover_filename = None
                if cover and cover.filename != '':
                    cover_filename = secure_filename(cover.filename)
                    cover_folder = os.path.join('static', 'covers')
                    os.makedirs(cover_folder, exist_ok=True)
                    cover_path = os.path.join(cover_folder, cover_filename)
                    cover.save(cover_path)

                # Insert into MongoDB
                result = mongo.db.books.insert_one({
                    "title": form["title"],
                    "author": form["author"],
                    "subject": form["subject"],
                    "description": form.get("description", ""),
                    "isbn": form.get("isbn", ""),
                    "publisher": form.get("publisher", ""),
                    "language": form.get("language", ""),
                    "year": int(form.get("year", 0)),
                    "tags": [tag.strip() for tag in form.get("tags", "").split(",") if tag.strip()],
                    "filename": filename,
                    "cover_filename": cover_filename,
                    "upload_date": datetime.now(),
                    "downloads": 0,
                    "uploaded_by": session.get('name', 'Unknown User')  # Track who uploaded
                })
                
                print(f"✅ Book uploaded successfully! ID: {result.inserted_id}")
                return redirect(url_for('index'))
            else:
                return render_template("upload.html", error="Please upload a valid PDF file")
        except Exception as e:
            print(f"❌ Upload failed: {str(e)}")
            return render_template("upload.html", error=f"Upload failed: {str(e)}")

    return render_template("upload.html")

# Download Route
@app.route("/download/<filename>")
def download(filename):
    try:
        # Increment download count in database
        mongo.db.books.update_one(
            {"filename": filename},
            {"$inc": {"downloads": 1}}
        )
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        # Still allow download even if database update fails
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm = request.form['confirm_password']
        role = request.form['role']
        
        if not name:
            return render_template('register.html', error='Name is required')
        if password != confirm:
            return render_template('register.html', error='Passwords do not match')
        if mongo.db.users.find_one({'email': email}):
            return render_template('register.html', error='Email already registered')
        
        hash_pw = generate_password_hash(password)
        mongo.db.users.insert_one({
            'name': name,
            'email': email, 
            'password': hash_pw, 
            'role': role
        })
        return redirect(url_for('login'))
    return render_template('register.html', error=None)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['name'] = user.get('name', 'Unknown User')
            session['email'] = user['email']
            session['role'] = user['role']
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=None)

# User logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Decorator for admin-only routes
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin login (simple password for now)
@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    books = list(mongo.db.books.find())
    return render_template("admin.html", books=books)

# Admin dashboard (after login)
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    books = list(mongo.db.books.find())
    users = list(mongo.db.users.find())
    return render_template("admin.html", books=books, users=users)

# Add new book (admin)
@app.route("/admin/add", methods=["GET", "POST"])
@admin_required
def admin_add():
    if request.method == "POST":
        form = request.form
        file = request.files.get("file")
        cover = request.files.get("cover")
        filename = None
        cover_filename = None
        external_link = form.get("external_link", "")
        # Save PDF if uploaded
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Save cover if uploaded
        if cover and cover.filename:
            cover_filename = secure_filename(cover.filename)
            cover_folder = os.path.join('static', 'covers')
            os.makedirs(cover_folder, exist_ok=True)
            cover.save(os.path.join(cover_folder, cover_filename))
        # Insert into DB
        mongo.db.books.insert_one({
            "title": form["title"],
            "author": form["author"],
            "subject": form["subject"],
            "description": form.get("description", ""),
            "isbn": form.get("isbn", ""),
            "publisher": form.get("publisher", ""),
            "edition": form.get("edition", ""),
            "language": form.get("language", ""),
            "year": int(form.get("year", 0)),
            "tags": [tag.strip() for tag in form.get("tags", "").split(",") if tag.strip()],
            "keywords": [kw.strip() for kw in form.get("keywords", "").split(",") if kw.strip()],
            "filename": filename,
            "external_link": external_link,
            "cover_filename": cover_filename,
            "upload_date": datetime.now(),
            "downloads": 0
        })
        return redirect(url_for('admin_dashboard'))
    return render_template("admin_book_form.html", book=None)

# Edit book (admin)
@app.route("/admin/edit/<book_id>", methods=["GET", "POST"])
@admin_required
def admin_edit(book_id):
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    if request.method == "POST":
        form = request.form
        file = request.files.get("file")
        cover = request.files.get("cover")
        filename = book.get("filename")
        cover_filename = book.get("cover_filename")
        external_link = form.get("external_link", book.get("external_link", ""))
        # Update PDF if uploaded
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Update cover if uploaded
        if cover and cover.filename:
            cover_filename = secure_filename(cover.filename)
            cover_folder = os.path.join('static', 'covers')
            os.makedirs(cover_folder, exist_ok=True)
            cover.save(os.path.join(cover_folder, cover_filename))
        # Update DB
        mongo.db.books.update_one({"_id": ObjectId(book_id)}, {"$set": {
            "title": form["title"],
            "author": form["author"],
            "subject": form["subject"],
            "description": form.get("description", ""),
            "isbn": form.get("isbn", ""),
            "publisher": form.get("publisher", ""),
            "edition": form.get("edition", ""),
            "language": form.get("language", ""),
            "year": int(form.get("year", 0)),
            "tags": [tag.strip() for tag in form.get("tags", "").split(",") if tag.strip()],
            "keywords": [kw.strip() for kw in form.get("keywords", "").split(",") if kw.strip()],
            "filename": filename,
            "external_link": external_link,
            "cover_filename": cover_filename
        }})
        return redirect(url_for('admin_dashboard'))
    return render_template("admin_book_form.html", book=book)

# Delete book (admin)
@app.route("/admin/delete/<book_id>")
@admin_required
def admin_delete(book_id):
    mongo.db.books.delete_one({"_id": ObjectId(book_id)})
    return redirect(url_for('admin_dashboard'))

# User management routes (admin only)
@app.route("/admin/users")
@admin_required
def admin_users():
    users = list(mongo.db.users.find())
    return render_template("admin_users.html", users=users)

@app.route("/admin/user/<user_id>")
@admin_required
def admin_user_detail(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return redirect(url_for('admin_users'))
    
    # Get books uploaded by this user
    user_books = list(mongo.db.books.find({"uploaded_by": user.get('name', 'Unknown User')}))
    return render_template("admin_user_detail.html", user=user, books=user_books)

@app.route("/admin/user/delete/<user_id>")
@admin_required
def admin_delete_user(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user and user.get('role') != 'admin':  # Prevent deleting other admins
        mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    return redirect(url_for('admin_users'))

@app.route("/admin/user/toggle_role/<user_id>")
@admin_required
def admin_toggle_user_role(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        new_role = 'admin' if user.get('role') == 'user' else 'user'
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)}, 
            {"$set": {"role": new_role}}
        )
    return redirect(url_for('admin_users'))

# Book Detail Page
@app.route('/book/<book_id>')
def book_detail(book_id):
    from bson.objectid import ObjectId
    book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    if not book:
        return render_template('book_detail.html', error='Book not found', book=None)
    # Get file size if local file exists
    file_size = None
    if book.get('filename'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], book['filename'])
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
    return render_template('book_detail.html', book=book, file_size=file_size)

if __name__ == "__main__":
    app.run(debug=True) 