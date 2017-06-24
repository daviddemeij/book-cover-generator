"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, send_file
from FlaskWeb import app

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
    )

@app.route('/get_image', methods=['POST'])
def get_image():
    import book_cover_generator
    input_image = request.files.get('input_image')
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre').lower()

    return book_cover_generator.generate_cover(input_image, title, author, genre)
