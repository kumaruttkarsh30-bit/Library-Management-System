from flask import Flask, jsonify, request
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

# Direct Embedded HTML to completely avoid "Not Found" file path issues on Render
@app.route('/')
def serve_index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Library Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow p-4" id="authSection">
                    <h3 class="text-center mb-3" id="authTitle">Library Login</h3>
                    <form id="loginForm">
                        <div class="mb-3">
                            <label>Username</label>
                            <input type="text" id="loginUsername" class="form-control" required value="admin">
                        </div>
                        <div class="mb-3">
                            <label>Password</label>
                            <input type="password" id="loginPassword" class="form-control" required value="admin123">
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Login</button>
                    </form>
                </div>

                <div class="card shadow p-4 d-none" id="dashboardSection">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h4>Welcome, <span id="loggedInUserDisplay"></span></h4>
                        <button id="logoutBtn" class="btn btn-danger btn-sm">Logout</button>
                    </div>
                    <div class="alert alert-success">
                        <h5>System Connected Successfully! 🚀</h5>
                        <p>Backend API and Database are fully operational.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = '/api';

        document.addEventListener('DOMContentLoaded', () => {
            checkAuthState();

            document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('loginUsername').value;
                const password = document.getElementById('loginPassword').value;

                try {
                    const res = await fetch(`${API_BASE}/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    const data = await res.json();

                    if (res.ok) {
                        localStorage.setItem('user', JSON.stringify(data));
                        checkAuthState();
                    } else {
                        alert(data.message || 'Login failed');
                    }
                } catch (err) {
                    alert('Server connection error.');
                }
            });

            document.getElementById('logoutBtn')?.addEventListener('click', () => {
                localStorage.removeItem('user');
                location.reload();
            });
        });

        function checkAuthState() {
            const userStr = localStorage.getItem('user');
            if (userStr) {
                const user = JSON.parse(userStr);
                document.getElementById('authSection').classList.add('d-none');
                document.getElementById('dashboardSection').classList.remove('d-none');
                document.getElementById('loggedInUserDisplay').innerText = `${user.username} (${user.role})`;
            } else {
                document.getElementById('authSection').classList.remove('d-none');
                document.getElementById('dashboardSection').classList.add('d-none');
            }
        }
    </script>
</body>
</html>'''

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)