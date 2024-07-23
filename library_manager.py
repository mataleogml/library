from flask import Flask, request, jsonify, render_template_string, g
import sqlite3
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Database setup
DATABASE = 'library.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Drop the existing table
        cursor.execute('DROP TABLE IF EXISTS books')
        # Create the new table with all fields
        cursor.execute('''
            CREATE TABLE books
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             title TEXT NOT NULL,
             author TEXT NOT NULL,
             language TEXT NOT NULL,
             main_subject TEXT NOT NULL,
             secondary_subject TEXT NOT NULL,
             isbn TEXT UNIQUE,
             ddc TEXT)
        ''')
        db.commit()
        logging.info("Database initialized successfully")

def db_update_needed():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in cursor.fetchall()]
        needed_columns = ['title', 'author', 'language', 'main_subject', 'secondary_subject', 'isbn', 'ddc']
        return not all(col in columns for col in needed_columns)

# Check if database needs update and initialize if necessary
if db_update_needed():
    init_db()

# Initialize the database
init_db()

# DDC classification
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
        <title>Library Manager</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"></script>
        <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
        <style>
            .tab-content {
                display: none;
            }
            .tab-content.is-active {
                display: block;
            }
        </style>
    </head>
    <body>
    <section class="section">
        <div class="container">
            <h1 class="title">Library Manager</h1>
            
            <div class="tabs">
                <ul>
                    <li class="is-active"><a data-tab="add-book">Add a Book</a></li>
                    <li><a data-tab="search-books">Search Books</a></li>
                </ul>
            </div>

            <div id="add-book" class="tab-content is-active">
                <h2 class="subtitle">Add a Book</h2>
                <form id="addBookForm">
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

            <div id="search-books" class="tab-content">
                <h2 class="subtitle">Search Books</h2>
                <div class="field">
                    <div class="control">
                        <input class="input" type="text" id="searchInput" placeholder="Search for books...">
                    </div>
                </div>
                <div id="searchResults"></div>
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
            
            $(document).on('click', '.edit-book', function() {
    var bookId = $(this).data('id');
    $.get('/edit_book/' + bookId, function(book) {
        // Populate the form with book data
        $('#title').val(book.title);
        $('#author').val(book.author);
        $('input[name="language"]').val(book.language);
        $('#main_subject').val(book.main_subject).trigger('change');
        setTimeout(function() {
            $('#secondary_subject').val(book.secondary_subject);
        }, 100);
        $('input[name="isbn"]').val(book.isbn);
        
        // Change the form submission to update instead of add
        $('#addBookForm').off('submit').on('submit', function(e) {
            e.preventDefault();
            $.post('/edit_book/' + bookId, $(this).serialize(), function(response) {
                if(response.status === 'success') {
                    alert('Book updated successfully.');
                    // Reset the form and reload search results
                    $('#addBookForm')[0].reset();
                    $('#searchInput').trigger('input');
                } else {
                    alert('Error: ' + response.message);
                }
            });
        });
        
        // Switch to the Add Book tab
        $('.tabs li:first-child a').click();
    });
});
            
            
            // Tab functionality
            $('.tabs li').on('click', function() {
                var tab = $(this).find('a').attr('data-tab');
                
                $('.tabs li').removeClass('is-active');
                $(this).addClass('is-active');
                
                $('.tab-content').removeClass('is-active');
                $('#' + tab).addClass('is-active');
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

            $('#searchInput').on('input', function() {
    var query = $(this).val();
    if(query.length > 2) {
        $.get('/search?q=' + query, function(data) {
            var results = '<table class="table is-fullwidth">';
            results += '<thead><tr><th>Title</th><th>Author</th><th>Language</th><th>Main Subject</th><th>Secondary Subject</th><th>ISBN</th><th>DDC</th><th>Action</th></tr></thead><tbody>';
            data.forEach(function(book) {
                results += '<tr>';
                results += '<td>' + book.title + '</td>';
                results += '<td>' + book.author + '</td>';
                results += '<td>' + book.language + '</td>';
                results += '<td>' + book.main_subject + '</td>';
                results += '<td>' + book.secondary_subject + '</td>';
                results += '<td>' + book.isbn + '</td>';
                results += '<td>' + book.ddc + '</td>';
                results += '<td><button class="button is-small is-info edit-book" data-id="' + book.id + '">Edit</button></td>';
                results += '</tr>';
            });
            results += '</tbody></table>';
            $('#searchResults').html(results);
        });
    }
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
    
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO books (title, author, language, main_subject, secondary_subject, isbn, ddc) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (title, author, language, main_subject, secondary_subject, isbn, ddc))
        db.commit()
        return jsonify({'status': 'success', 'ddc': ddc})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'A book with this ISBN already exists.'})
    except Exception as e:
        logging.error(f"Error adding book: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while adding the book.'})
    
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        language = request.form['language']
        main_subject = request.form['main_subject']
        secondary_subject = request.form['secondary_subject']
        isbn = request.form['isbn']
        ddc = generate_ddc(main_subject, secondary_subject)
        
        try:
            cursor.execute('''
                UPDATE books 
                SET title=?, author=?, language=?, main_subject=?, secondary_subject=?, isbn=?, ddc=?
                WHERE id=?
            ''', (title, author, language, main_subject, secondary_subject, isbn, ddc, book_id))
            db.commit()
            return jsonify({'status': 'success', 'message': 'Book updated successfully'})
        except Exception as e:
            logging.error(f"Error updating book: {e}")
            return jsonify({'status': 'error', 'message': 'An error occurred while updating the book'})
    
    else:  # GET request
        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        book = cursor.fetchone()
        if book:
            return jsonify({
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'language': book[3],
                'main_subject': book[4],
                'secondary_subject': book[5],
                'isbn': book[6],
                'ddc': book[7]
            })
        else:
            return jsonify({'status': 'error', 'message': 'Book not found'})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title, author, language, main_subject, secondary_subject, isbn, ddc FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?", 
                       ('%'+query+'%', '%'+query+'%', '%'+query+'%'))
        books = [{'id': row[0], 'title': row[1], 'author': row[2], 'language': row[3], 'main_subject': row[4], 
                  'secondary_subject': row[5], 'isbn': row[6], 'ddc': row[7]} for row in cursor.fetchall()]
        return jsonify(books)
    except Exception as e:
        logging.error(f"Error searching books: {e}")
        return jsonify([])

@app.route('/get_titles')
def get_titles():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT title FROM books")
        titles = [row[0] for row in cursor.fetchall()]
        return jsonify(titles)
    except Exception as e:
        logging.error(f"Error getting titles: {e}")
        return jsonify([])

@app.route('/get_authors')
def get_authors():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT author FROM books")
        authors = [row[0] for row in cursor.fetchall()]
        return jsonify(authors)
    except Exception as e:
        logging.error(f"Error getting authors: {e}")
        return jsonify([])

@app.route('/get_secondary_subjects/<main_subject>')
def get_secondary_subjects(main_subject):
    return jsonify(ddc_classes[main_subject]['secondary'])

if __name__ == '__main__':
    app.run(debug=True)