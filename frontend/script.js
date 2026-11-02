let books = JSON.parse(localStorage.getItem("lib_books_v2")) || [
    { id: 101, title: "Database System Concepts", author: "Abraham Silberschatz", category: "DBMS" },
    { id: 102, title: "Introduction to Algorithms", author: "Thomas H. Cormen", category: "DSA" },
    { id: 103, title: "Operating System Concepts", author: "Peter Baer Galvin", category: "OS" },
    { id: 104, title: "Computer Organization & Architecture", author: "William Stallings", category: "COA" }
];

let students = JSON.parse(localStorage.getItem("lib_students_v2")) || [
    { uid: "25BCS101", name: "Kumar Uttkarsh", dept: "B.E. CSE" },
    { uid: "25BCS102", name: "Aarav Sharma", dept: "B.E. CSE" },
    { uid: "25BEC105", name: "Priya Patel", dept: "B.E. ECE" }
];

let issues = JSON.parse(localStorage.getItem("lib_issues_v2")) || [
    { issueId: 501, bookId: 102, studentUid: "25BCS101", issueDate: "2026-10-20", dueDate: "2026-10-30" }
];

function saveData() {
    localStorage.setItem("lib_books_v2", JSON.stringify(books));
    localStorage.setItem("lib_students_v2", JSON.stringify(students));
    localStorage.setItem("lib_issues_v2", JSON.stringify(issues));
    renderAll();
}

function switchTab(tab) {
    ["dashboard", "books", "students", "issue"].forEach(t => {
        document.getElementById("view-" + t).style.display = (t === tab) ? "block" : "none";
        document.getElementById("nav-" + t).classList.toggle("active", t === tab);
    });
    const titles = {
        dashboard: "Library Management Dashboard",
        books: "Manage Book Catalog",
        students: "Student Directory & Registration",
        issue: "Issue & Return Circulation Desk"
    };
    document.getElementById("page-title").innerText = titles[tab];
    renderAll();
}

function isBookIssued(bookId) {
    return issues.some(i => i.bookId === bookId);
}

function isOverdue(dueDateStr) {
    const today = new Date().toISOString().split("T")[0];
    return dueDateStr < today;
}

function renderAll() {
    // 1. Update Top Stats
    document.getElementById("stat-books").innerText = books.length;
    document.getElementById("stat-students").innerText = students.length;
    document.getElementById("stat-issued").innerText = issues.length;
    const overdueCount = issues.filter(i => isOverdue(i.dueDate)).length;
    document.getElementById("stat-overdue").innerText = overdueCount;

    // 2. Render Dashboard Table
    const dashQuery = (document.getElementById("dash-search")?.value || "").toLowerCase();
    const dashTbody = document.getElementById("dash-book-list");
    dashTbody.innerHTML = "";
    books.filter(b => b.title.toLowerCase().includes(dashQuery) || b.author.toLowerCase().includes(dashQuery) || b.category.toLowerCase().includes(dashQuery))
        .forEach(b => {
            const issued = isBookIssued(b.id);
            dashTbody.innerHTML += `
                <tr>
                    <td>#${b.id}</td>
                    <td><strong>${b.title}</strong></td>
                    <td>${b.author}</td>
                    <td>${b.category}</td>
                    <td><span class="badge ${issued ? 'issued' : 'available'}">${issued ? 'Issued' : 'Available'}</span></td>
                </tr>`;
        });

    // 3. Render Manage Books Table
    const bookQuery = (document.getElementById("book-search")?.value || "").toLowerCase();
    const bookTbody = document.getElementById("book-list");
    bookTbody.innerHTML = "";
    books.filter(b => b.title.toLowerCase().includes(bookQuery) || b.author.toLowerCase().includes(bookQuery))
        .forEach(b => {
            const issued = isBookIssued(b.id);
            bookTbody.innerHTML += `
                <tr>
                    <td>#${b.id}</td>
                    <td><strong>${b.title}</strong></td>
                    <td>${b.author}</td>
                    <td>${b.category}</td>
                    <td><span class="badge ${issued ? 'issued' : 'available'}">${issued ? 'Issued' : 'Available'}</span></td>
                    <td>
                        <button class="action-btn delete-btn" onclick="deleteBook(${b.id})">Delete</button>
                    </td>
                </tr>`;
        });

    // 4. Render Students Table
    const stuTbody = document.getElementById("student-list");
    stuTbody.innerHTML = "";
    students.forEach(s => {
        const heldCount = issues.filter(i => i.studentUid === s.uid).length;
        stuTbody.innerHTML += `
            <tr>
                <td><strong>${s.uid}</strong></td>
                <td>${s.name}</td>
                <td>${s.dept}</td>
                <td>${heldCount} Book(s)</td>
                <td><button class="action-btn delete-btn" onclick="deleteStudent('${s.uid}')">Remove</button></td>
            </tr>`;
    });

    // 5. Populate Issue Dropdowns
    const bookSelect = document.getElementById("issue-book-select");
    bookSelect.innerHTML = '<option value="">-- Select Available Book --</option>';
    books.filter(b => !isBookIssued(b.id)).forEach(b => {
        bookSelect.innerHTML += `<option value="${b.id}">#${b.id} - ${b.title}</option>`;
    });

    const stuSelect = document.getElementById("issue-student-select");
    stuSelect.innerHTML = '<option value="">-- Select Student --</option>';
    students.forEach(s => {
        stuSelect.innerHTML += `<option value="${s.uid}">${s.uid} - ${s.name}</option>`;
    });

    // 6. Render Active Issues Table
    const issueTbody = document.getElementById("issue-list");
    issueTbody.innerHTML = "";
    issues.forEach(iss => {
        const book = books.find(b => b.id === iss.bookId) || { title: "Unknown Book" };
        const stu = students.find(s => s.uid === iss.studentUid) || { name: iss.studentUid };
        const overdue = isOverdue(iss.dueDate);
        issueTbody.innerHTML += `
            <tr>
                <td>#ISS-${iss.issueId}</td>
                <td><strong>${book.title}</strong></td>
                <td>${stu.name} (${iss.studentUid})</td>
                <td>${iss.issueDate}</td>
                <td>${iss.dueDate}</td>
                <td><span class="badge ${overdue ? 'overdue' : 'issued'}">${overdue ? 'Overdue' : 'Active'}</span></td>
                <td><button class="action-btn toggle-btn" onclick="returnBook(${iss.issueId})">✅ Mark Returned</button></td>
            </tr>`;
    });
}

// Add Book
document.getElementById("book-form").addEventListener("submit", e => {
    e.preventDefault();
    const title = document.getElementById("book-title").value.trim();
    const author = document.getElementById("book-author").value.trim();
    const category = document.getElementById("book-category").value.trim();
    const nextId = books.length ? Math.max(...books.map(b => b.id)) + 1 : 101;
    books.push({ id: nextId, title, author, category });
    e.target.reset();
    saveData();
});

// Add Student
document.getElementById("student-form").addEventListener("submit", e => {
    e.preventDefault();
    const uid = document.getElementById("stu-id").value.trim().toUpperCase();
    const name = document.getElementById("stu-name").value.trim();
    const dept = document.getElementById("stu-dept").value.trim();
    if (students.some(s => s.uid === uid)) {
        alert("Student with this UID already exists!");
        return;
    }
    students.push({ uid, name, dept });
    e.target.reset();
    saveData();
});

// Issue Book
document.getElementById("issue-form").addEventListener("submit", e => {
    e.preventDefault();
    const bookId = parseInt(document.getElementById("issue-book-select").value);
    const studentUid = document.getElementById("issue-student-select").value;
    const dueDate = document.getElementById("issue-due-date").value;
    const today = new Date().toISOString().split("T")[0];
    const nextIssueId = issues.length ? Math.max(...issues.map(i => i.issueId)) + 1 : 501;

    issues.push({ issueId: nextIssueId, bookId, studentUid, issueDate: today, dueDate });
    e.target.reset();
    saveData();
});

function returnBook(issueId) {
    issues = issues.filter(i => i.issueId !== issueId);
    saveData();
}

function deleteBook(id) {
    if (isBookIssued(id)) {
        alert("Cannot delete a book that is currently issued! Return it first.");
        return;
    }
    books = books.filter(b => b.id !== id);
    saveData();
}

function deleteStudent(uid) {
    if (issues.some(i => i.studentUid === uid)) {
        alert("This student currently holds an issued book! Return the book first.");
        return;
    }
    students = students.filter(s => s.uid !== uid);
    saveData();
}

// Set default due date input to +7 days from today
const defaultDue = new Date();
defaultDue.setDate(defaultDue.getDate() + 7);
document.getElementById("issue-due-date").value = defaultDue.toISOString().split("T")[0];

renderAll();
