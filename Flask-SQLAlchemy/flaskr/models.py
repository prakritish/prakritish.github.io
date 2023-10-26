from flaskr import db

class Author(db.Model):
  __tablename__ = 'author'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30))
  email = db.Column(db.String(30), unique=True, nullable=False)
  # Relationship between Author and Book
  books = db.relationship("Book", back_populates="author")
    
  def __init__(self, name, email):
    self.name = name
    self.email = email

  def __repr__(self):
    return f"<Author: {self.name} <email: {self.email}>>"


class Book(db.Model):
  __tablename__ = 'book'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), unique=True, nullable=False)
  author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
  # Relationship between Book and Author
  author = db.relationship("Author", back_populates="books")
  # Relationship between Book and Store
  stores = db.relationship("Store", secondary="book_to_store_map", back_populates="books")

  def __init__(self, Book):
    self.name = Book

  def __repr__(self):
    return f"<Book: {self.name}>"


class Store(db.Model):
  __tablename__ = 'store'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), unique=True, nullable=False)
  # Relationship between Store and Book
  books = db.relationship("Book", secondary="book_to_store_map", back_populates="stores")

  def __init__(self, Book):
    self.name = Book

  def __repr__(self):
    return f"<Store: {self.name}>"


# Table for Many to Many Relationship Mapping between Book and Store
class BookToStoreMap(db.Model):
  __tablename__ = 'book_to_store_map'
  book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
  store_id = db.Column(db.Integer, db.ForeignKey('store.id'), primary_key=True)
