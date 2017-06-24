"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, send_file
from FlaskWeb import app

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/get_image', methods=['POST'])
def get_image():
    import book_cover_generator
    input_image = request.files.get('input_image')
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre').lower()

    return book_cover_generator.generate_cover(input_image, title, author, genre)
