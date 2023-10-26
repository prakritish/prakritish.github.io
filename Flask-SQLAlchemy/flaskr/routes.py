from flask import make_response, redirect, render_template, request, url_for, jsonify
from flask import current_app as app
from flaskr import db
from flaskr.models import *

@app.route("/status", methods=["GET"])
def status():
  return jsonify({"status":"ok"}), 200

@app.route("/books", methods=["GET"])
def get_books():
  books = db.session.query(Book).all()
  data = {
    "status": "ok",
    "count": len(books),
    "books": []
  }
  for book in books:
    book_data = {
      "name": book.name,
      "author": book.author.name,
      "store": []
    }
    for store in book.stores:
      book_data['store'].append(store.name)
    data['books'].append(book_data)
  return jsonify(data), 200

@app.route("/book", methods=["POST"])
def add_book():
  request_data = request.get_json()
  if not "name" in request_data:
    return jsonify({
      "status": False,
      "message": "Book Name is mandatory"
    }), 400
  book_name = request_data['name']
  author_name = author_email = ""
  if "author" in request_data:
    if "name" in request_data['author']:
      author_name = request_data['author']['name']
    if "email" in request_data['author']:
      author_email = request_data['author']['email']
  book = db.session.query(Books)       
    
  return jsonify({"status":"ok"}), 200
