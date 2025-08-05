
# Test database connection
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from flask_pymongo import PyMongo
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# MongoDB Atlas URI - Updated with correct credentials
app.config["MONGO_URI"] ="mongodb+srv://mkapilnaths:1534mNSuGkRkri01@clustercoolie.pui72w6.mongodb.net/library?retryWrites=true&w=majority"

# Configure MongoDB with SSL settings
app.config["MONGO_URI_OPTIONS"] = {
    "tlsAllowInvalidCertificates": True,
    "ssl": True
}

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

# Home + Search
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        query = {}
        if request.method == "POST":
            search_term = request.form["search"]
            query = {"$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"author": {"$regex": search_term, "$options": "i"}},
                {"subject": {"$regex": search_term, "$options": "i"}}
            ]}
        books = mongo.db.books.find(query)
        return render_template("index.html", books=books)
    except Exception as e:
        return render_template("index.html", books=[], error=f"Database error: {str(e)}")

# Upload Page
@app.route("/upload", methods=["GET", "POST"])
def upload():
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
                mongo.db.books.insert_one({
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
                    "downloads": 0
                })

                return redirect(url_for('index'))
            else:
                return render_template("upload.html", error="Please upload a valid PDF file")
        except Exception as e:
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

if __name__ == "__main__":
    app.run(debug=True)
