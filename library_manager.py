from flask import Flask, request, jsonify, render_template_string
import sqlite3
import re

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  author TEXT,
                  language TEXT,
                  subject TEXT,
                  ddc TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Simplified DDC classification
ddc_classes = {
    'Computer science, information & general works': '000',
    'Philosophy & psychology': '100',
    'Religion': '200',
    'Social sciences': '300',
    'Language': '400',
    'Science': '500',
    'Technology': '600',
    'Arts & recreation': '700',
    'Literature': '800',
    'History & geography': '900'
}

def generate_ddc(subject):
    for key, value in ddc_classes.items():
        if subject.lower() in key.lower():
            return value
    return '000'  # Default to general works if no match found

@app.route('/')
def home():
    return render_template_string('''
        <h1>Personal Library Manager</h1>
        <h2>Add a Book</h2>
        <form action="/add_book" method="post">
            Title: <input type="text" name="title"><br>
            Author: <input type="text" name="author"><br>
            Language: <input type="text" name="language"><br>
            Subject: <input type="text" name="subject"><br>
            <input type="submit" value="Add Book">
        </form>
        <h2>Search Books</h2>
        <form action="/search" method="get">
            Search: <input type="text" name="query">
            <input type="submit" value="Search">
        </form>
    ''')

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    language = request.form['language']
    subject = request.form['subject']
    ddc = generate_ddc(subject)

    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, language, subject, ddc) VALUES (?, ?, ?, ?, ?)",
              (title, author, language, subject, ddc))
    conn.commit()
    conn.close()

    return f"Book added successfully. DDC: {ddc}"

@app.route('/search')
def search():
    query = request.args.get('query', '')
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR subject LIKE ? OR ddc LIKE ?",
              ('%'+query+'%', '%'+query+'%', '%'+query+'%', '%'+query+'%'))
    results = c.fetchall()
    conn.close()

    return render_template_string('''
        <h2>Search Results</h2>
        <ul>
        {% for book in results %}
            <li>{{ book[1] }} by {{ book[2] }} ({{ book[3] }}) - DDC: {{ book[5] }}</li>
        {% endfor %}
        </ul>
        <a href="/">Back to Home</a>
    ''', results=results)

if __name__ == '__main__':
    app.run(debug=True)