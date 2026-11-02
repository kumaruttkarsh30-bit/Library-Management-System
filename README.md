# 📚 LibraryHub - Library Management System (DBMS Project)

A full-stack Library Management System built to manage book catalogs, student records, and book issue/return transactions efficiently.

## 📁 Project Structure
- **frontend/**: Interactive dashboard (`index.html`, `style.css`, `script.js`) with real-time search, book addition, issue/return status toggling, and LocalStorage persistence.
- **database/**: Relational schema (`library.sql`) containing `Books`, `Students`, and `Issue_Records` tables with Primary/Foreign key constraints and JOIN queries.
- **backend/**: Python HTTP & SQLite API (`app.py`) serving library catalog endpoints.

## 🚀 Features
- **Dashboard Analytics**: Real-time count of Total Books, Total Students, Books Issued, and Overdue Books.
- **Catalog Management**: Add new books by title, author, and category, or delete outdated records.
- **Instant Search & Filter**: Search books dynamically by title or author name.
- **Issue / Return Workflow**: One-click toggle between Available and Issued states.
