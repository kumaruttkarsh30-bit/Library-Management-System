import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, addDoc, deleteDoc, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyBN56U6pB41707hxDc1qy-ljwuqzZ0I05A",
    authDomain: "libraryhub-bd652.firebaseapp.com",
    projectId: "libraryhub-bd652",
    storageBucket: "libraryhub-bd652.firebasestorage.app",
    messagingSenderId: "250263355113",
    appId: "1:250263355113:web:09fd2b5fcb71d040967a78"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

let books = [];
let students = [];
let issues = [];

// Real-time Listeners (Jaise hi kahin change hoga, sab jagah live dikhega)
onSnapshot(collection(db, "books"), (snapshot) => {
    books = snapshot.docs.map(doc => ({ firebaseId: doc.id, ...doc.data() }));
    renderAll();
});

onSnapshot(collection(db, "students"), (snapshot) => {
    students = snapshot.docs.map(doc => ({ firebaseId: doc.id, ...doc.data() }));
    renderAll();
});

onSnapshot(collection(db, "issues"), (snapshot) => {
    issues = snapshot.docs.map(doc => ({ firebaseId: doc.id, ...doc.data() }));
    renderAll();
});

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

window.switchTab = switchTab;

function isBookIssued(bookId) {
    return issues.some(i => i.bookId == bookId);
}

function isOverdue(dueDateStr) {
    const today = new Date().toISOString().split("T")[0];
    return dueDateStr < today;
}

function renderAll() {
    if (!document.getElementById("stat-books")) return;

    // 1. Update Top Stats
    document.getElementById("stat-books").innerText = books.length;
    document.getElementById("stat-students").innerText = students.length;
    document.getElementById("stat-issued").innerText = issues.length;
    const overdueCount = issues.filter(i => isOverdue(i.dueDate)).length;
    document.getElementById("stat-overdue").innerText = overdueCount;

    // 2. Render Dashboard Table
    const dashQuery = (document.getElementById("dash-search")?.value || "").toLowerCase();
    const dashTbody = document.getElementById("dash-book-list");
    if (dashTbody) {
        dashTbody.innerHTML = "";
        books.filter(b => (b.title || "").toLowerCase().includes(dashQuery) || (b.author || "").toLowerCase().includes(dashQuery) || (b.category || "").toLowerCase().includes(dashQuery))
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
    }

    // 3. Render Manage Books Table
    const bookQuery = (document.getElementById("book-search")?.value || "").toLowerCase();
    const bookTbody = document.getElementById("book-list");
    if (bookTbody) {
        bookTbody.innerHTML = "";
        books.filter(b => (b.title || "").toLowerCase().includes(bookQuery) || (b.author || "").toLowerCase().includes(bookQuery))
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
                            <button class="action-btn delete-btn" onclick="deleteBook('${b.firebaseId}', ${b.id})">Delete</button>
                        </td>
                    </tr>`;
            });
    }

    // 4. Render Students Table
    const stuTbody = document.getElementById("student-list");
    if (stuTbody) {
        stuTbody.innerHTML = "";
        students.forEach(s => {
            const heldCount = issues.filter(i => i.studentUid === s.uid).length;
            stuTbody.innerHTML += `
                <tr>
                    <td><strong>${s.uid}</strong></td>
                    <td>${s.name}</td>
                    <td>${s.dept}</td>
                    <td>${heldCount} Book(s)</td>
                    <td><button class="action-btn delete-btn" onclick="deleteStudent('${s.firebaseId}', '${s.uid}')">Remove</button></td>
                </tr>`;
        });
    }

    // 5. Populate Issue Dropdowns
    const bookSelect = document.getElementById("issue-book-select");
    if (bookSelect) {
        bookSelect.innerHTML = '<option value="">-- Select Available Book --</option>';
        books.filter(b => !isBookIssued(b.id)).forEach(b => {
            bookSelect.innerHTML += `<option value="${b.id}">#${b.id} - ${b.title}</option>`;
        });
    }

    const stuSelect = document.getElementById("issue-student-select");
    if (stuSelect) {
        stuSelect.innerHTML = '<option value="">-- Select Student --</option>';
        students.forEach(s => {
            stuSelect.innerHTML += `<option value="${s.uid}">${s.uid} - ${s.name}</option>`;
        });
    }

    // 6. Render Active Issues Table
    const issueTbody = document.getElementById("issue-list");
    if (issueTbody) {
        issueTbody.innerHTML = "";
        issues.forEach(iss => {
            const book = books.find(b => b.id == iss.bookId) || { title: "Unknown Book" };
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
                    <td><button class="action-btn toggle-btn" onclick="returnBook('${iss.firebaseId}')">✅ Mark Returned</button></td>
                </tr>`;
        });
    }
}

// Add Book to Firestore
document.getElementById("book-form")?.addEventListener("submit", async e => {
    e.preventDefault();
    const title = document.getElementById("book-title").value.trim();
    const author = document.getElementById("book-author").value.trim();
    const category = document.getElementById("book-category").value.trim();
    const nextId = books.length ? Math.max(...books.map(b => b.id || 100)) + 1 : 101;
    
    await addDoc(collection(db, "books"), { id: nextId, title, author, category });
    e.target.reset();
});

// Add Student to Firestore
document.getElementById("student-form")?.addEventListener("submit", async e => {
    e.preventDefault();
    const uid = document.getElementById("stu-id").value.trim().toUpperCase();
    const name = document.getElementById("stu-name").value.trim();
    const dept = document.getElementById("stu-dept").value.trim();
    if (students.some(s => s.uid === uid)) {
        alert("Student with this UID already exists!");
        return;
    }
    await addDoc(collection(db, "students"), { uid, name, dept });
    e.target.reset();
});

// Issue Book to Firestore
document.getElementById("issue-form")?.addEventListener("submit", async e => {
    e.preventDefault();
    const bookId = parseInt(document.getElementById("issue-book-select").value);
    const studentUid = document.getElementById("issue-student-select").value;
    const dueDate = document.getElementById("issue-due-date").value;
    const today = new Date().toISOString().split("T")[0];
    const nextIssueId = issues.length ? Math.max(...issues.map(i => i.issueId || 500)) + 1 : 501;

    await addDoc(collection(db, "issues"), { issueId: nextIssueId, bookId, studentUid, issueDate: today, dueDate });
    e.target.reset();
});

window.returnBook = async function(firebaseId) {
    await deleteDoc(doc(db, "issues", firebaseId));
};

window.deleteBook = async function(firebaseId, id) {
    if (isBookIssued(id)) {
        alert("Cannot delete a book that is currently issued! Return it first.");
        return;
    }
    await deleteDoc(doc(db, "books", firebaseId));
};

window.deleteStudent = async function(firebaseId, uid) {
    if (issues.some(i => i.studentUid === uid)) {
        alert("This student currently holds an issued book! Return the book first.");
        return;
    }
    await deleteDoc(doc(db, "students", firebaseId));
};

// Set default due date
const dueInput = document.getElementById("issue-due-date");
if (dueInput) {
    const defaultDue = new Date();
    defaultDue.setDate(defaultDue.getDate() + 7);
    dueInput.value = defaultDue.toISOString().split("T")[0];
}