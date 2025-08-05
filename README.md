# Library Management System

A Flask-based library management system with MongoDB Atlas integration for storing and managing digital books.

## Features

- 📚 Book upload and management
- 🔍 Search functionality (title, author, subject)
- 📥 Download tracking
- 🖼️ Cover image support
- 🏷️ Tag-based organization
- 📊 Download statistics

## Database Connection

The application is connected to **MongoDB Atlas** using the following configuration:

- **Database**: MongoDB Atlas cluster
- **Connection**: `mongodb+srv://mkapilnaths:GlSw7u5AaF6pC0W3@clustercoolie.epjib32.mongodb.net/`
- **Collection**: `books`

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python init_db.py
```

This will:
- Create necessary database indexes for better performance
- Check the current state of the database
- Verify the connection

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Database Schema

### Books Collection

Each book document contains:

```json
{
  "title": "Book Title",
  "author": "Author Name",
  "subject": "Subject Category",
  "description": "Book description",
  "isbn": "ISBN number",
  "publisher": "Publisher name",
  "language": "Language",
  "year": 2023,
  "tags": ["tag1", "tag2"],
  "filename": "book.pdf",
  "cover_filename": "cover.jpg",
  "upload_date": "2023-12-01T10:00:00Z",
  "downloads": 0
}
```

## API Endpoints

- `GET /` - Home page with search functionality
- `POST /` - Search books
- `GET /upload` - Upload page
- `POST /upload` - Upload new book
- `GET /download/<filename>` - Download book file
- `GET /test-db` - Test database connection

## Database Indexes

The following indexes are created for optimal performance:

- `title` - For title-based searches
- `author` - For author-based searches  
- `subject` - For subject-based searches
- `tags` - For tag-based searches
- `upload_date` - For sorting by upload date

## Error Handling

The application includes comprehensive error handling for:

- Database connection failures
- File upload errors
- Search query errors
- Download tracking errors

## Security Features

- Secure filename handling using `secure_filename()`
- Input validation for file uploads
- Error messages that don't expose sensitive information

## Testing the Database Connection

Visit `http://localhost:5000/test-db` to test the database connection and see available collections.

## Troubleshooting

### Database Connection Issues

1. Check your internet connection
2. Verify the MongoDB Atlas URI is correct
3. Ensure the MongoDB Atlas cluster is running
4. Check if the database user has proper permissions

### File Upload Issues

1. Ensure the `static/books` directory exists
2. Check file permissions
3. Verify the uploaded file is a valid PDF

## Environment Variables (Optional)

For production deployment, consider using environment variables:

```bash
export MONGO_URI="your_mongodb_atlas_uri"
export FLASK_ENV="production"
```

Then update `app.py` to use:

```python
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "default_uri")
``` 