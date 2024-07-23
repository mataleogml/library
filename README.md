# Library Manager

Library Manager is a web-based application for managing a library's book collection. It allows users to add new books, search for existing books, and edit book information.

## Features

- Add new books with details such as title, author, language, main subject, secondary subject, and ISBN
- Automatically generate Dewey Decimal Classification (DDC) codes based on selected subjects
- Search for books by title, author, or ISBN
- Edit existing book information
- Autocomplete suggestions for book titles and authors

## Technology Stack

- Backend: Python with Flask
- Frontend: HTML, CSS (Bulma), JavaScript (jQuery)
- Database: SQLite

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/mataleogml/library.git
   cd library
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the Flask server:
   ```
   python library_manager.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. Use the "Add a Book" tab to add new books to the library

4. Use the "Search Books" tab to find and edit existing books

## Project Structure

- `library_manager.py`: Main Flask application file
- `library.db`: SQLite database file
- `templates/`: Directory containing HTML templates
- `static/`: Directory containing static files like CSS and JavaScript