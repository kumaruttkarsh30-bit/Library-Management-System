const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    checkAuthState();

    // Toggle Login / Signup forms
    document.getElementById('showSignup')?.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('loginForm')?.parentElement?.classList?.add('d-none');
        document.getElementById('signupForm')?.parentElement?.classList?.remove('d-none');
        const title = document.getElementById('authTitle');
        if (title) title.innerText = 'Register Account';
    });

    document.getElementById('showLogin')?.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('signupForm')?.parentElement?.classList?.add('d-none');
        document.getElementById('loginForm')?.parentElement?.classList?.remove('d-none');
        const title = document.getElementById('authTitle');
        if (title) title.innerText = 'Library Login';
    });

    // Login Submit
    document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const usernameInput = document.getElementById('loginUsername');
        const passwordInput = document.getElementById('loginPassword');
        if (!usernameInput || !passwordInput) return;

        const username = usernameInput.value;
        const password = passwordInput.value;

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
            console.error('Login error:', err);
            alert('Server connection error.');
        }
    });

    // Signup Submit
    document.getElementById('signupForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('signupUsername')?.value;
        const password = document.getElementById('signupPassword')?.value;
        const role = document.getElementById('signupRole')?.value || 'student';

        try {
            const res = await fetch(`${API_BASE}/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, role })
            });
            const data = await res.json();

            if (res.ok) {
                alert('Account created! Please login.');
                document.getElementById('showLogin')?.click();
            } else {
                alert(data.message || 'Signup failed');
            }
        } catch (err) {
            console.error('Signup error:', err);
            alert('Server connection error.');
        }
    });

    // Logout
    document.getElementById('logoutBtn')?.addEventListener('click', () => {
        localStorage.removeItem('user');
        location.reload();
    });

    // Sidebar Tab Navigation
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
    const authSection = document.getElementById('authSection');
    const dashboardSection = document.getElementById('dashboardSection');

    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            if (authSection) authSection.classList.add('d-none');
            if (dashboardSection) dashboardSection.classList.remove('d-none');
            
            const userDisplay = document.getElementById('loggedInUserDisplay');
            if (userDisplay) userDisplay.innerText = `${user.username} (${user.role})`;

            if (user.role !== 'admin') {
                document.querySelectorAll('.admin-only').forEach(el => el.classList.add('d-none'));
            }

            loadBooks();
            loadStudents();
            loadIssues();
            return;
        } catch (e) {
            localStorage.removeItem('user');
        }
    }
    
    if (authSection) authSection.classList.remove('d-none');
    if (dashboardSection) dashboardSection.classList.add('d-none');
}

function setupDataForms() {
    document.getElementById('bookForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await fetch(`${API_BASE}/books`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: document.getElementById('bookTitle')?.value,
                author: document.getElementById('bookAuthor')?.value,
                category: document.getElementById('bookCategory')?.value
            })
        });
        const modalEl = document.getElementById('addBookModal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl)?.hide();
        loadBooks();
    });

    document.getElementById('studentForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await fetch(`${API_BASE}/students`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                uid: document.getElementById('studentUid')?.value,
                name: document.getElementById('studentName')?.value,
                dept: document.getElementById('studentDept')?.value
            })
        });
        const modalEl = document.getElementById('addStudentModal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl)?.hide();
        loadStudents();
    });

    document.getElementById('issueForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await fetch(`${API_BASE}/issues`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bookId: document.getElementById('issueBookId')?.value,
                studentUid: document.getElementById('issueStudentUid')?.value,
                issueDate: document.getElementById('issueDate')?.value,
                dueDate: document.getElementById('dueDate')?.value
            })
        });
        const modalEl = document.getElementById('addIssueModal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl)?.hide();
        loadIssues();
    });
}

async function loadBooks() {
    try {
        const res = await fetch(`${API_BASE}/books`);
        const books = await res.json();
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const list = document.getElementById('bookList');
        if (!list) return;

        list.innerHTML = '';
        books.forEach(b => {
            let actionBtn = user?.role === 'admin' ? `<td><button onclick="deleteBook(${b.id})" class="btn btn-danger btn-sm">Delete</button></td>` : '';
            list.innerHTML += `<tr><td>${b.id}</td><td>${b.title}</td><td>${b.author}</td><td>${b.category}</td>${actionBtn}</tr>`;
        });
    } catch (err) { console.error(err); }
}

async function deleteBook(id) {
    await fetch(`${API_BASE}/books/${id}`, { method: 'DELETE' });
    loadBooks();
}

async function loadStudents() {
    try {
        const res = await fetch(`${API_BASE}/students`);
        const students = await res.json();
        const list = document.getElementById('studentList');
        if (!list) return;

        list.innerHTML = '';
        students.forEach(s => {
            list.innerHTML += `<tr><td>${s.uid}</td><td>${s.name}</td><td>${s.dept}</td><td><button onclick="deleteStudent('${s.uid}')" class="btn btn-danger btn-sm">Delete</button></td></tr>`;
        });
    } catch (err) { console.error(err); }
}

async function deleteStudent(uid) {
    await fetch(`${API_BASE}/students/${uid}`, { method: 'DELETE' });
    loadStudents();
}

async function loadIssues() {
    try {
        const res = await fetch(`${API_BASE}/issues`);
        const issues = await res.json();
        const list = document.getElementById('issueList');
        if (!list) return;

        list.innerHTML = '';
        issues.forEach(i => {
            list.innerHTML += `<tr><td>${i.issueId}</td><td>${i.bookId}</td><td>${i.studentUid}</td><td>${i.issueDate}</td><td>${i.dueDate}</td><td><button onclick="deleteIssue(${i.issueId})" class="btn btn-danger btn-sm">Return</button></td></tr>`;
        });
    } catch (err) { console.error(err); }
}

async function deleteIssue(issueId) {
    await fetch(`${API_BASE}/issues/${issueId}`, { method: 'DELETE' });
    loadIssues();
}