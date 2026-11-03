from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        category TEXT NOT NULL)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
                        uid TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        dept TEXT NOT NULL)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS issues (
                        issueId INTEGER PRIMARY KEY AUTOINCREMENT,
                        bookId INTEGER,
                        studentUid TEXT,
                        issueDate TEXT,
                        dueDate TEXT)''')

    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL)''')
    
    admin_check = conn.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_check:
        hashed_pw = generate_password_hash('admin123', method='pbkdf2:sha256')
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     ('admin', hashed_pw, 'admin'))
        conn.commit()

    conn.close()

init_db()

# Bulletproof routes to serve frontend files from any possible location
@app.route('/')
def serve_index():
    paths = ['index.html', 'backend/index.html', '../frontend/index.html', 'frontend/index.html']
    for p in paths:
        if os.path.exists(p):
            directory, filename = os.path.split(p)
            return send_from_directory(directory if directory else '.', filename)
    return "index.html not found", 404

@app.route('/script.js')
def serve_script():
    paths = ['script.js', 'backend/script.js', '../frontend/script.js', 'frontend/script.js']
    for p in paths:
        if os.path.exists(p):
            directory, filename = os.path.split(p)
            return send_from_directory(directory if directory else '.', filename)
    return "script.js not found", 404

@app.route('/style.css')
def serve_style():
    paths = ['style.css', 'backend/style.css', '../frontend/style.css', 'frontend/style.css', 'style.css']
    for p in paths:
        if os.path.exists(p):
            directory, filename = os.path.split(p)
            return send_from_directory(directory if directory else '.', filename)
    return "style.css not found", 404

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     (username, hashed_pw, role))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": "error", "message": "Username already exists"}), 400
    conn.close()
    return jsonify({"status": "success", "message": "User registered successfully"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if not user and username == 'admin':
        hashed_pw = generate_password_hash('admin123', method='pbkdf2:sha256')
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     ('admin', hashed_pw, 'admin'))
        conn.commit()
        user = conn.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()

    conn.close()

    if user and check_password_hash(user['password'], password):
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "role": user['role'],
            "username": user['username']
        })
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

@app.route('/api/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return jsonify([dict(row) for row in books])

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json or {}
    conn = get_db_connection()
    conn.execute('INSERT INTO books (title, author, category) VALUES (?, ?, ?)',
                 (data.get('title'), data.get('author'), data.get('category')))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json or {}
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO students (uid, name, dept) VALUES (?, ?, ?)',
                     (data.get('uid'), data.get('name'), data.get('dept')))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": "error", "message": "Student already exists"}), 400
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/students/<string:uid>', methods=['DELETE'])
def delete_student(uid):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE uid = ?', (uid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/issues', methods=['GET'])
def get_issues():
    conn = get_db_connection()
    issues = conn.execute('SELECT * FROM issues').fetchall()
    conn.close()
    return jsonify([dict(row) for row in issues])

@app.route('/api/issues', methods=['POST'])
def add_issue():
    data = request.json or {}
    conn = get_db_connection()
    conn.execute('INSERT INTO issues (bookId, studentUid, issueDate, dueDate) VALUES (?, ?, ?, ?)',
                 (data.get('bookId'), data.get('studentUid'), data.get('issueDate'), data.get('dueDate')))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/issues/<int:issueId>', methods=['DELETE'])
def delete_issue(issueId):
    conn = get_db_connection()
    conn.execute('DELETE FROM issues WHERE issueId = ?', (issueId,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)