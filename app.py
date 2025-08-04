from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_pymongo import PyMongo
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# MongoDB Atlas URI
app.config["MONGO_URI"] ="mongodb://localhost:27017/ebookdb"

mongo = PyMongo(app)

# Folder to store uploaded books
UPLOAD_FOLDER = os.path.join('static', 'books')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home + Search
@app.route("/", methods=["GET", "POST"])
def index():
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

# Upload Page
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        subject = request.form["subject"]
        file = request.files["file"]

        if file and file.filename.endswith(".pdf"):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            mongo.db.books.insert_one({
                "title": title,
                "author": author,
                "subject": subject,
                "filename": filename,
                "upload_date": datetime.now()
            })

            return redirect(url_for('index'))

    return render_template("upload.html")

# Download Route
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
