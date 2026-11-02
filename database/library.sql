-- Create Database
CREATE DATABASE IF NOT EXISTS LibraryDB;
USE LibraryDB;

-- 1. Books Table (Primary Key: book_id)
CREATE TABLE IF NOT EXISTS Books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    status ENUM('Available', 'Issued') DEFAULT 'Available'
) AUTO_INCREMENT = 101;

-- 2. Students Table (Primary Key: student_id)
CREATE TABLE IF NOT EXISTS Students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Issue Records Table (Foreign Keys referencing Books and Students)
CREATE TABLE IF NOT EXISTS Issue_Records (
    issue_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    student_id INT NOT NULL,
    issue_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);

-- Sample Data for Books
INSERT INTO Books (title, author, category, status) VALUES
('Database System Concepts', 'Abraham Silberschatz', 'DBMS', 'Available'),
('Introduction to Algorithms', 'Thomas H. Cormen', 'DSA', 'Issued'),
('Operating System Concepts', 'Peter Baer Galvin', 'OS', 'Available'),
('Clean Code', 'Robert C. Martin', 'Software Eng', 'Available');

-- Sample Data for Students
INSERT INTO Students (student_id, name, department, email) VALUES
(2501, 'Kumar Uttkarsh', 'CSE', 'uttkarsh@cu.edu.in'),
(2502, 'Aarav Sharma', 'CSE', 'aarav@cu.edu.in'),
(2503, 'Priya Verma', 'ECE', 'priya@cu.edu.in');

-- Sample Data for Issue Records
INSERT INTO Issue_Records (book_id, student_id, issue_date, return_date) VALUES
(102, 2501, '2026-10-25', NULL);

-- Useful DBMS Viva Queries (JOIN & Aggregation)
-- 1. View all currently issued books with student details:
SELECT i.issue_id, b.title, s.name AS issued_to, s.department, i.issue_date
FROM Issue_Records i
JOIN Books b ON i.book_id = b.book_id
JOIN Students s ON i.student_id = s.student_id
WHERE i.return_date IS NULL;

-- 2. Count total books by category:
SELECT category, COUNT(*) AS total_books FROM Books GROUP BY category;