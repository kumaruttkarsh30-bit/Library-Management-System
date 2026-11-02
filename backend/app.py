from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3
import os

DB_PATH = "library.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            issued INTEGER DEFAULT 0
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        sample_books = [
            (101, "Database System Concepts", "Abraham Silberschatz", "DBMS", 0),
            (102, "Introduction to Algorithms", "Thomas H. Cormen", "DSA", 1),
            (103, "Operating System Concepts", "Peter Baer Galvin", "OS", 0),
            (104, "Clean Code", "Robert C. Martin", "Software Eng", 0)
        ]
        cursor.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?)", sample_books)
    conn.commit()
    conn.close()

class LibraryAPI(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/api/books":
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, category, issued FROM books")
            rows = cursor.fetchall()
            conn.close()
            books = [{"id": r[0], "title": r[1], "author": r[2], "category": r[3], "issued": bool(r[4])} for r in rows]
            self._send_json(books)
        else:
            # Serve frontend static files (html, css, js)
            if self.path == "/" or self.path == "":
                filepath = "frontend/login.html"  # Pehle login page khulega
            else:
                filepath = "frontend" + self.path

            if os.path.exists(filepath) and os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    content = f.read()
                
                content_type = "text/html"
                if filepath.endswith(".css"):
                    content_type = "text/css"
                elif filepath.endswith(".js"):
                    content_type = "application/javascript"
                elif filepath.endswith(".json"):
                    content_type = "application/json"

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")

if __name__ == "__main__":
    init_db()
    server = HTTPServer(("0.0.0.0", 5000), LibraryAPI)
    print("LibraryHub Backend API running...")
    server.serve_forever() 