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

# Full Featured Dashboard Embedded App
@app.route('/')
def serve_index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Library Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background: #343a40; color: white; }
        .sidebar .nav-link { color: rgba(255,255,255,.75); }
        .sidebar .nav-link.active, .sidebar .nav-link:hover { color: #fff; background: rgba(255,255,255,.1); }
    </style>
</head>
<body class="bg-light">

    <!-- Auth Section -->
    <div class="container mt-5" id="authSection">
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="card shadow p-4">
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
            </div>
        </div>
    </div>

    <!-- Dashboard Section -->
    <div id="dashboardSection" class="d-none">
        <div class="container-fluid">
            <div class="row">
                <!-- Sidebar -->
                <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse p-3">
                    <h4 class="text-white mb-4">Library Panel</h4>
                    <ul class="nav flex-column">
                        <li class="nav-item mb-2"><a href="#" class="nav-link active" data-bs-target="#booksTab">Books Management</a></li>
                        <li class="nav-item mb-2"><a href="#" class="nav-link" data-bs-target="#studentsTab">Students Directory</a></li>
                        <li class="nav-item mb-2"><a href="#" class="nav-link" data-bs-target="#issuesTab">Issued Books</a></li>
                    </ul>
                </nav>

                <!-- Main Content -->
                <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
                    <div class="d-flex justify-content-between align-items-center pb-3 mb-3 border-bottom">
                        <h4>Welcome, <span id="loggedInUserDisplay"></span></h4>
                        <button id="logoutBtn" class="btn btn-danger btn-sm">Logout</button>
                    </div>

                    <!-- Books Tab -->
                    <div id="booksTab" class="tab-pane-content">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h3>Books Inventory</h3>
                            <button class="btn btn-success btn-sm admin-only" data-bs-toggle="modal" data-bs-target="#addBookModal">+ Add Book</button>
                        </div>
                        <table class="table table-striped table-bordered bg-white">
                            <thead>
                                <tr><th>ID</th><th>Title</th><th>Author</th><th>Category</th><th class="admin-only">Actions</th></tr>
                            </thead>
                            <tbody id="bookList"></tbody>
                        </table>
                    </div>

                    <!-- Students Tab -->
                    <div id="studentsTab" class="tab-pane-content d-none">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h3>Students Directory</h3>
                            <button class="btn btn-success btn-sm admin-only" data-bs-toggle="modal" data-bs-target="#addStudentModal">+ Add Student</button>
                        </div>
                        <table class="table table-striped table-bordered bg-white">
                            <thead>
                                <tr><th>UID</th><th>Name</th><th>Department</th><th>Actions</th></tr>
                            </thead>
                            <tbody id="studentList"></tbody>
                        </table>
                    </div>

                    <!-- Issues Tab -->
                    <div id="issuesTab" class="tab-pane-content d-none">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h3>Issued Books Records</h3>
                            <button class="btn btn-success btn-sm admin-only" data-bs-toggle="modal" data-bs-target="#addIssueModal">+ Issue Book</button>
                        </div>
                        <table class="table table-striped table-bordered bg-white">
                            <thead>
                                <tr><th>Issue ID</th><th>Book ID</th><th>Student UID</th><th>Issue Date</th><th>Due Date</th><th>Actions</th></tr>
                            </thead>
                            <tbody id="issueList"></tbody>
                        </table>
                    </div>
                </main>
            </div>
        </div>
    </div>

    <!-- Modals for Admin -->
    <div class="modal fade" id="addBookModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><form id="bookForm">
        <div class="modal-header"><h5 class="modal-title">Add New Book</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
            <div class="mb-3"><label>Title</label><input type="text" id="bookTitle" class="form-control" required></div>
            <div class="mb-3"><label>Author</label><input type="text" id="bookAuthor" class="form-control" required></div>
            <div class="mb-3"><label>Category</label><input type="text" id="bookCategory" class="form-control" required></div>
        </div>
        <div class="modal-footer"><button type="submit" class="btn btn-primary">Save Book</button></div>
    </form></div></div></div>

    <div class="modal fade" id="addStudentModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><form id="studentForm">
        <div class="modal-header"><h5 class="modal-title">Add Student</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
            <div class="mb-3"><label>UID</label><input type="text" id="studentUid" class="form-control" required></div>
            <div class="mb-3"><label>Name</label><input type="text" id="studentName" class="form-control" required></div>
            <div class="mb-3"><label>Department</label><input type="text" id="studentDept" class="form-control" required></div>
        </div>
        <div class="modal-footer"><button type="submit" class="btn btn-primary">Save Student</button></div>
    </form></div></div></div>

    <div class="modal fade" id="addIssueModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><form id="issueForm">
        <div class="modal-header"><h5 class="modal-title">Issue Book</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
            <div class="mb-3"><label>Book ID</label><input type="number" id="issueBookId" class="form-control" required></div>
            <div class="mb-3"><label>Student UID</label><input type="text" id="issueStudentUid" class="form-control" required></div>
            <div class="mb-3"><label>Issue Date</label><input type="date" id="issueDate" class="form-control" required></div>
            <div class="mb-3"><label>Due Date</label><input type="date" id="dueDate" class="form-control" required></div>
        </div>
        <div class="modal-footer"><button type="submit" class="btn btn-primary">Issue Book</button></div>
    </form></div></div></div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
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
                } catch (err) { alert('Server connection error.'); }
            });

            document.getElementById('logoutBtn')?.addEventListener('click', () => {
                localStorage.removeItem('user');
                location.reload();
            });

            document.querySelectorAll('.sidebar .nav-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    document.querySelectorAll('.sidebar .nav-link').forEach(l => l.classList.remove('active'));
                    document.querySelectorAll('.tab-pane-content').forEach(t => t.classList.add('d-none'));
                    link.classList.add('active');
                    const target = link.getAttribute('data-bs-target');
                    if (target) document.querySelector(target)?.classList.remove('d-none');
                });
            });

            setupDataForms();
        });

        function checkAuthState() {
            const userStr = localStorage.getItem('user');
            if (userStr) {
                const user = JSON.parse(userStr);
                document.getElementById('authSection').classList.add('d-none');
                document.getElementById('dashboardSection').classList.remove('d-none');
                document.getElementById('loggedInUserDisplay').innerText = `${user.username} (${user.role})`;
                if (user.role !== 'admin') {
                    document.querySelectorAll('.admin-only').forEach(el => el.classList.add('d-none'));
                }
                loadBooks(); loadStudents(); loadIssues();
            } else {
                document.getElementById('authSection').classList.remove('d-none');
                document.getElementById('dashboardSection').classList.add('d-none');
            }
        }

        function setupDataForms() {
            document.getElementById('bookForm')?.addEventListener('submit', async (e) => {
                e.preventDefault();
                await fetch(`${API_BASE}/books`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: document.getElementById('bookTitle').value,
                        author: document.getElementById('bookAuthor').value,
                        category: document.getElementById('bookCategory').value
                    })
                });
                bootstrap.Modal.getInstance(document.getElementById('addBookModal'))?.hide();
                loadBooks();
            });

            document.getElementById('studentForm')?.addEventListener('submit', async (e) => {
                e.preventDefault();
                await fetch(`${API_BASE}/students`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        uid: document.getElementById('studentUid').value,
                        name: document.getElementById('studentName').value,
                        dept: document.getElementById('studentDept').value
                    })
                });
                bootstrap.Modal.getInstance(document.getElementById('addStudentModal'))?.hide();
                loadStudents();
            });

            document.getElementById('issueForm')?.addEventListener('submit', async (e) => {
                e.preventDefault();
                await fetch(`${API_BASE}/issues`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        bookId: document.getElementById('issueBookId').value,
                        studentUid: document.getElementById('issueStudentUid').value,
                        issueDate: document.getElementById('issueDate').value,
                        dueDate: document.getElementById('dueDate').value
                    })
                });
                bootstrap.Modal.getInstance(document.getElementById('addIssueModal'))?.hide();
                loadIssues();
            });
        }

        async function loadBooks() {
            const res = await fetch(`${API_BASE}/books`);
            const books = await res.json();
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            const list = document.getElementById('bookList');
            list.innerHTML = '';
            books.forEach(b => {
                let actionBtn = user?.role === 'admin' ? `<td><button onclick="deleteBook(${b.id})" class="btn btn-danger btn-sm">Delete</button></td>` : '';
                list.innerHTML += `<tr><td>${b.id}</td><td>${b.title}</td><td>${b.author}</td><td>${b.category}</td>${actionBtn}</tr>`;
            });
        }

        async function deleteBook(id) {
            await fetch(`${API_BASE}/books/${id}`, { method: 'DELETE' });
            loadBooks();
        }

        async function loadStudents() {
            const res = await fetch(`${API_BASE}/students`);
            const students = await res.json();
            const list = document.getElementById('studentList');
            list.innerHTML = '';
            students.forEach(s => {
                list.innerHTML += `<tr><td>${s.uid}</td><td>${s.name}</td><td>${s.dept}</td><td><button onclick="deleteStudent('${s.uid}')" class="btn btn-danger btn-sm">Delete</button></td></tr>`;
            });
        }

        async function deleteStudent(uid) {
            await fetch(`${API_BASE}/students/${uid}`, { method: 'DELETE' });
            loadStudents();
        }

        async function loadIssues() {
            const res = await fetch(`${API_BASE}/issues`);
            const issues = await res.json();
            const list = document.getElementById('issueList');
            list.innerHTML = '';
            issues.forEach(i => {
                list.innerHTML += `<tr><td>${i.issueId}</td><td>${i.bookId}</td><td>${i.studentUid}</td><td>${i.issueDate}</td><td>${i.dueDate}</td><td><button onclick="deleteIssue(${i.issueId})" class="btn btn-danger btn-sm">Return</button></td></tr>`;
            });
        }

        async function deleteIssue(issueId) {
            await fetch(`${API_BASE}/issues/${issueId}`, { method: 'DELETE' });
            loadIssues();
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
        return jsonify({"status": "success", "message": "Login successful", "role": user['role'], "username": user['username']})
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

@app.route('/api/books', methods=['GET', 'POST'])
def handle_books():
    conn = get_db_connection()
    if request.method == 'POST':
        data = request.json or {}
        conn.execute('INSERT INTO books (title, author, category) VALUES (?, ?, ?)', (data.get('title'), data.get('author'), data.get('category')))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return jsonify([dict(row) for row in books])

@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/students', methods=['GET', 'POST'])
def handle_students():
    conn = get_db_connection()
    if request.method == 'POST':
        data = request.json or {}
        try:
            conn.execute('INSERT INTO students (uid, name, dept) VALUES (?, ?, ?)', (data.get('uid'), data.get('name'), data.get('dept')))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"status": "error", "message": "Student already exists"}), 400
        conn.close()
        return jsonify({"status": "success"})
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

@app.route('/api/students/<string:uid>', methods=['DELETE'])
def delete_student(uid):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE uid = ?', (uid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/issues', methods=['GET', 'POST'])
def handle_issues():
    conn = get_db_connection()
    if request.method == 'POST':
        data = request.json or {}
        conn.execute('INSERT INTO issues (bookId, studentUid, issueDate, dueDate) VALUES (?, ?, ?, ?)', (data.get('bookId'), data.get('studentUid'), data.get('issueDate'), data.get('dueDate')))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    issues = conn.execute('SELECT * FROM issues').fetchall()
    conn.close()
    return jsonify([dict(row) for row in issues])

@app.route('/api/issues/<int:issueId>', methods=['DELETE'])
def delete_issue(issueId):
    conn = get_db_connection()
    conn.execute('DELETE FROM issues WHERE issueId = ?', (issueId,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)