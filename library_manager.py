from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import sqlite3
import json
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Database initialization function
def init_db():
    db_path = 'library.db'
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS books
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT,
                      author TEXT,
                      language TEXT,
                      main_subject TEXT,
                      secondary_subject TEXT,
                      isbn TEXT UNIQUE,
                      ddc TEXT)''')
        conn.commit()
        conn.close()
        logging.info(f"Database initialized successfully at {db_path}")
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
        raise

# Call init_db() when the application starts
with app.app_context():
    init_db()

# Simplified DDC classification with secondary subjects
ddc_classes = {
    'General works': {
        'code': '000',
        'secondary': ['Bibliographies', 'Library & information sciences', 'Encyclopedias']
    },
    'Philosophy & psychology': {
        'code': '100',
        'secondary': ['Metaphysics', 'Epistemology', 'Psychology']
    },
    'Religion': {
        'code': '200',
        'secondary': ['Bible', 'Christian theology', 'Islam']
    },
    'Social sciences': {
        'code': '300',
        'secondary': ['Sociology', 'Political science', 'Economics']
    },
    'Language': {
        'code': '400',
        'secondary': ['Linguistics', 'English', 'German']
    },
    'Science': {
        'code': '500',
        'secondary': ['Mathematics', 'Astronomy', 'Physics']
    },
    'Technology': {
        'code': '600',
        'secondary': ['Medicine', 'Engineering', 'Agriculture']
    },
    'Arts & recreation': {
        'code': '700',
        'secondary': ['Fine arts', 'Music', 'Sports']
    },
    'Literature': {
        'code': '800',
        'secondary': ['American literature', 'English literature', 'German literature']
    },
    'History & geography': {
        'code': '900',
        'secondary': ['Geography & travel', 'Biography', 'History of ancient world']
    }
}

def generate_ddc(main_subject, secondary_subject):
    for key, value in ddc_classes.items():
        if main_subject == key:
            return value['code']
    return '000'  # Default to general works if no match found

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Personal Library Manager</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"></script>
    <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
</head>
<body>
<section class="section">
    <div class="container">
        <h1 class="title">Personal Library Manager</h1>
        
        <div class="columns">
            <div class="column">
                <h2 class="subtitle">Add a Book</h2>
                <form action="/add_book" method="post" id="addBookForm">
                    <div class="field">
                        <label class="label">Title</label>
                        <div class="control">
                            <input class="input" type="text" name="title" id="title" required>
                        </div>
                    </div>
                    
                    <div class="field">
                        <label class="label">Author</label>
                        <div class="control">
                            <input class="input" type="text" name="author" id="author" required>
                        </div>
                    </div>
                    
                    <div class="field">
                        <label class="label">Language</label>
                        <div class="control">
                            <input class="input" type="text" name="language" required>
                        </div>
                    </div>
                    
                    <div class="field">
                        <label class="label">Main Subject</label>
                        <div class="control">
                            <div class="select">
                                <select name="main_subject" id="main_subject" required>
                                    <option value="">Select main subject</option>
                                    {% for subject in ddc_classes %}
                                        <option value="{{ subject }}">{{ subject }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="field">
                        <label class="label">Secondary Subject</label>
                        <div class="control">
                            <div class="select">
                                <select name="secondary_subject" id="secondary_subject" required>
                                    <option value="">Select secondary subject</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="field">
                        <label class="label">ISBN</label>
                        <div class="control">
                            <input class="input" type="text" name="isbn" required>
                        </div>
                    </div>
                    
                    <div class="field">
                        <div class="control">
                            <button class="button is-primary" type="submit">Add Book</button>
                        </div>
                    </div>
                </form>
            </div>
            
            <div class="column">
                <h2 class="subtitle">Search Books</h2>
                <form action="/search" method="get">
                    <div class="field">
                        <div class="control">
                            <input class="input" type="text" name="query" placeholder="Search...">
                        </div>
                    </div>
                    <div class="field">
                        <div class="control">
                            <button class="button is-info" type="submit">Search</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
</section>

<script>
$(document).ready(function() {
    $.getJSON('/get_titles', function(data) {
        $("#title").autocomplete({
            source: data
        });
    });
    
    $.getJSON('/get_authors', function(data) {
        $("#author").autocomplete({
            source: data
        });
    });
    
    $('#main_subject').change(function() {
        var main_subject = $(this).val();
        if(main_subject) {
            $.getJSON('/get_secondary_subjects/' + main_subject, function(data) {
                var options = '<option value="">Select secondary subject</option>';
                for(var i = 0; i < data.length; i++) {
                    options += '<option value="' + data[i] + '">' + data[i] + '</option>';
                }
                $('#secondary_subject').html(options);
            });
        } else {
            $('#secondary_subject').html('<option value="">Select secondary subject</option>');
        }
    });
    
    $('#addBookForm').submit(function(e) {
        e.preventDefault();
        $.post('/add_book', $(this).serialize(), function(response) {
            if(response.status === 'success') {
                alert('Book added successfully. DDC: ' + response.ddc);
                $('#addBookForm')[0].reset();
            } else {
                alert('Error: ' + response.message);
            }
        });
    });
});
</script>
</body>
</html>
    ''', ddc_classes=ddc_classes)

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    language = request.form['language']
    main_subject = request.form['main_subject']
    secondary_subject = request.form['secondary_subject']
    isbn = request.form['isbn']
    ddc = generate_ddc(main_subject, secondary_subject)

    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO books (title, author, language, main_subject, secondary_subject, isbn, ddc) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (title, author, language, main_subject, secondary_subject, isbn, ddc))
        conn.commit()
        return jsonify({'status': 'success', 'ddc': ddc})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'A book with this ISBN already exists.'})
    finally:
        conn.close()

@app.route('/search')
def search():
    query = request.args.get('query', '')
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR main_subject LIKE ? OR secondary_subject LIKE ? OR isbn LIKE ? OR ddc LIKE ?",
                  ('%'+query+'%', '%'+query+'%', '%'+query+'%', '%'+query+'%', '%'+query+'%', '%'+query+'%'))
        results = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"Database error in search: {e}")
        results = []

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Search Results - Personal Library Manager</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css">
</head>
<body>
<section class="section">
    <div class="container">
        <h1 class="title">Search Results</h1>
        <table class="table is-fullwidth">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Language</th>
                    <th>Main Subject</th>
                    <th>Secondary Subject</th>
                    <th>ISBN</th>
                    <th>DDC</th>
                </tr>
            </thead>
            <tbody>
            {% for book in results %}
                <tr>
                    <td>{{ book[1] }}</td>
                    <td>{{ book[2] }}</td>
                    <td>{{ book[3] }}</td>
                    <td>{{ book[4] }}</td>
                    <td>{{ book[5] }}</td>
                    <td>{{ book[6] }}</td>
                    <td>{{ book[7] }}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
        <a href="/" class="button is-link">Back to Home</a>
    </div>
</section>
</body>
</html>
    ''', results=results)

@app.route('/get_titles')
def get_titles():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT title FROM books")
    titles = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(titles)

@app.route('/get_authors')
def get_authors():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT author FROM books")
    authors = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(authors)

@app.route('/get_secondary_subjects/<main_subject>')
def get_secondary_subjects(main_subject):
    return jsonify(ddc_classes[main_subject]['secondary'])

if __name__ == '__main__':
    app.run(debug=True)