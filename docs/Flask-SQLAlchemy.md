# ORM - SQLAclhemy

__ORM (Object-Relational Mapping)__ is a programming technique that allows you to work with databases using an object-oriented approach, where database records are represented as objects in your code. It serves as a bridge between the object-oriented world of application code and the relational world of databases. ORM tools like SQLAlchemy abstract the complexities of database interactions and provide a higher-level, Pythonic interface for working with data.

SQLAlchemy is a popular Python library for building and interacting with databases using the ORM approach. It provides a high-level, object-oriented API for interacting with databases, making it easier to work with databases in a Pythonic way. In this tutorial, we'll cover the basics of SQLAlchemy with Flask, including how to set it up, define models, perform CRUD (Create, Read, Update, Delete) operations, and run queries.

**Prerequisites:**
1. Python installed (version 3.6 or higher)
2. Basic knowledge of SQL databases
3. Basic knowledge of Flask

**Installation:**
You can install SQLAlchemy using pip:

```bash
pip install Flask-SQLAlchemy
# The following would be used for DB Administration
pip install Flask-Migrate
```
My `requirements.txt` for Vrtual Environment on Mac is as below:
```
alembic==1.12.0
blinker==1.6.3
click==8.1.7
Flask==3.0.0
Flask-Alembic==2.0.1
Flask-Migrate==4.0.5
Flask-SQLAlchemy==3.1.1
greenlet==3.0.0
itsdangerous==2.1.2
Jinja2==3.1.2
Mako==1.2.4
MarkupSafe==2.1.3
SQLAlchemy==2.0.22
typing_extensions==4.8.0
Werkzeug==3.0.0
```

**1. Setting up SQLAlchemy:**

Before you can use SQLAlchemy, you need to create a SQLAlchemy engine, which manages the connection to your database. You'll also need to define a Session to manage transactions.

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# Required for DB Migration
from flask_migrate import Migrate
# SQLALCHEMY_DATABASE_URI is defined in 'flaskr/config.py'
from flaskr.config import SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()

def create_app(test_config=None):
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
  db.init_app(app)
  Migrate(app, db)
  # Import model classes. I have my models.py with 3 clasess in folder flaskr
  from flaskr.models import Author, Book, Store
  with app.app_context():
    from . import routes  # Import routes
  return app
```

**2. Defining Models:**

In SQLAlchemy, you define your database models as Python classes. Each class represents a table in the database. You can use SQLAlchemy data types to define columns.

```python
from flaskr import db

class Author(db.Model):
  __tablename__ = 'author'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30))
  email = db.Column(db.String(30), unique=True, nullable=False)
  books = db.relationship("Book", back_populates="author")
    
  def __init__(self, name, email):
    self.name = name
    self.email = email

  def __repr__(self):
    return f"<Author: {self.name} <email: {self.email}>>"
```

**3. Creating Tables:**

You need to create the tables in the database based on your model definitions. We'll cover the details in later section.

```python
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```
The above command should create the SQLite DB and create the required table(s)

**4. Performing CRUD Operations:**

**Creating (C):**

To add a new record to the database, you create a new instance of your model and add it to a session. After adding all the records you want to insert, you commit the session.

```python
# We'll use "flask shell" to interact with the DB
flask shell
Python 3.11.5 (main, Sep 11 2023, 08:19:27) [Clang 14.0.6 ] on darwin
App: flaskr
Instance: /Users/superman/Devel/bookstore_app/instance
# Import the model
>>> from flaskr.models import Author
# Create objects
>>> author1 = Author(name="Prakritish Sen Eshore", email="prakritish@example.com")
>>> author2 = Author(name="Umang Vanjara", email="umang@example.com")
>>> author3 = Author(name="Chandan Dutta", email="chandan@example.com")
# Add one object to DB
>>> db.session.add(author1)
# Add multiple objects at once to DB
>>> db.session.add_all([author2, author3])
# Commit the changes to DB
>>> db.session.commit()
>>> exit()
```

**Reading (R):**

To retrieve data, you can use queries. SQLAlchemy provides a query interface to perform SELECT operations.

```python
# Query for a specific user by Name
flask shell
Python 3.11.5 (main, Sep 11 2023, 08:19:27) [Clang 14.0.6 ] on darwin
App: flaskr
Instance: /Users/superman/Devel/bookstore_app/instance
>>> author = db.session.query(Author).filter_by(name="Prakritish Sen Eshore").first()
# Print the author object. The way it's represented while printing is 
# controlled by '__repr__' method of the model class.
>>> print(author)
<Author: Prakritish Sen Eshore <email: prakritish@example.com>>
>>> print(author.email)
prakritish@example.com
>>>
```

**Updating (U):**

To update data, retrieve the object you want to modify, change its attributes, and commit the changes.

```python
# Update user's name
flask shell
Python 3.11.5 (main, Sep 11 2023, 08:19:27) [Clang 14.0.6 ] on darwin
App: flaskr
Instance: /Users/superman/Devel/bookstore_app/instance
>>> author = db.session.query(Author).filter_by(email="chandan@example.com").first()
>>> print(author.name)
Chandan Dutta
>>> author.name = "Chandan Dutta Chowdhury"
>>> db.session.commit()
>>> updated_author = db.session.query(Author).filter_by(email="chandan@example.com").first()
>>> print(updated_author.name)
Chandan Dutta Chowdhury
```

**Deleting (D):**

To delete a record, retrieve it, and then call the `delete()` method on the session.

```python
flask shell
Python 3.11.5 (main, Sep 11 2023, 08:19:27) [Clang 14.0.6 ] on darwin
App: flaskr
Instance: /Users/superman/Devel/bookstore_app/instance
>>> author = db.session.query(Author).filter_by(id=3).first()
>>> author
<Author: Chandan Dutta Chowdhury <email: chandan@example.com>>
>>> db.session.delete(author)
>>> db.session.commit()
>>> author_list = db.session.query(Author).all()
>>> author_list
[<Author: Prakritish Sen Eshore <email: prakritish@example.com>>, <Author: Umang Vanjara <email: umang@example.com>>]
>>>
```

**5. Running Queries:**

You can run more complex queries using SQLAlchemy's query API. For example:

```python
# Query all authors
authors = db.session.query(Author).all()

# Filter authors by a email domain
authors_using_example_com = db.session.query(Author).filter(Author.email.contains("example.com")).all()

# Aggregation
from sqlalchemy import func
total_users = db.session.query(func.count(Author.id)).scalar()
```

**6. Closing the Session:**

Always remember to close the session when you're done with it to release resources and properly close the database connection.

```python
db.session.close()
```

**7. Relationships:**

___One to Many / Many to One___

In real-world applications, tables are often related to each other. SQLAlchemy allows you to define relationships between models. For example, if you have a `Author` and `Book` model, you can establish a one-to-many relationship:

```python
from sqlalchemy import ForeignKey
from flaskr import db

class Author(db.Model):
  __tablename__ = 'author'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30))
  email = db.Column(db.String(30), unique=True, nullable=False)
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
  author = db.relationship("Author", back_populates="books")

  def __init__(self, Book):
    self.name = Book

  def __repr__(self):
    return f"<Book: {self.name}>"
```

With this setup, you can easily access a book and the author of the book or a list of books published by an author.
But before, we get started we need to create the new table and update the relationship between the Author and Book.
```
# The following command would automatically update the SQLite DB for you.

flask db migrate -m "Adding Book's Table and creating relationship between Book and Author"

flask db upgrade
```
Let's populate the tables with Book Information
```
flask shell
Python 3.11.5 (main, Sep 11 2023, 08:19:27) [Clang 14.0.6 ] on darwin
App: flaskr
Instance: /Users/superman/Devel/bookstore_app/instance
>>> from flaskr.models import Author, Book
>>> author1 = db.session.query(Author).filter_by(name="Prakritish Sen Eshore").first()
>>> author2 = db.session.query(Author).filter_by(name="Umang Vanjara").first()
>>> print(author1, author2)
<Author: Prakritish Sen Eshore <email: prakritish@example.com>> <Author: Umang Vanjara <email: umang@example.com>>
>>> book1 = Book("Ansible Refresher")
>>> book2 = Book("Exploring SQLAlchemy")
>>> book3 = Book("Effective Communication")
>>> db.session.add_all([book1, book2, book3])
>>> book1.author = author1
>>> book2.author = author1
>>> book3.author = author2
>>> db.session.commit()
>>>
now exiting InteractiveConsole...
```
Let's query back and see if we can find the relationship between Book & Author
```python
# One to Many Relationship i.e., let's find all the books written by an Author
>>> author = db.session.query(Author).filter_by(name="Prakritish Sen Eshore").first()
>>> print(author)
<Author: Prakritish Sen Eshore <email: prakritish@example.com>>
>>> print(author.books)
[<Book: Ansible Refresher>, <Book: Exploring SQLAlchemy>]
# Many to One i.e., let's the find the Author of a Book
>>> book = db.session.query(Book).filter_by(name="Effective Communication").first()
>>> print(book)
<Book: Effective Communication>
>>> print(book.author)
<Author: Umang Vanjara <email: umang@example.com>>
>>>
```

___Many to Many___

Let's update our schema once again to explore many to many relationship. In this example we'll add a new table for **Shop**. A given book may be found in multiple shops and shops will have more than one book.
To create Many to Many relationship, we'll create an additional table to store the mapping.
```
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
``` 

As before, we'll update the DB to create the new tables.
```
flask db migrate -m "Adding Store and Mapping Table for Book and Store Relationship"

flask db upgradde
```

Let's add some data.
```
>>> from flaskr.models import Author, Book, Store
>>> store1 = Store("Amazon")
>>> store2 = Store("Flipkart")
>>> db.session.add_all([store1, store2])
>>> books = db.session.query(Book).all()
>>> print(books)
[<Book: Ansible Refresher>, <Book: Exploring SQLAlchemy>, <Book: Effective Communication>]
>>> for book in books:
...     store1.books.append(book)
...     if book.name == "Effective Communication":
...             continue
...     store2.books.append(book)
...
>>> db.session.commit()
>>>
```
Let's see if we can see the Many to Many relationships
```
>>> store1 = db.session.query(Store).filter_by(name="Amazon").first()
>>> print(store1)
<Store: Amazon>
>>> print(store1.books)
[<Book: Ansible Refresher>, <Book: Exploring SQLAlchemy>, <Book: Effective Communication>]
>>> store2 = db.session.query(Store).filter_by(name="Flipkart").first()
>>> print(store2)
<Store: Flipkart>
>>> print(store2.books)
[<Book: Ansible Refresher>, <Book: Exploring SQLAlchemy>]
>>> book = db.session.query(Book).filter_by(name="Exploring SQLAlchemy").first()
>>> print(book)
<Book: Exploring SQLAlchemy>
>>> print(book.stores)
[<Store: Amazon>, <Store: Flipkart>]
>>>
```

**8. Query Filters:**

You can use various filters to narrow down your queries:

```python
# Filter users with specific conditions
active_users = session.query(User).filter(User.is_active == True).all()
recent_users = session.query(User).filter(User.registered_date > '2023-01-01').all()

# Combining filters
from sqlalchemy import and_, or_
filtered_users = session.query(User).filter(or_(User.age < 25, User.is_student == True)).all()
```

**9. Sorting and Pagination:**

You can sort and paginate your queries easily:

```python
# Sort users by age in descending order
sorted_users = session.query(User).order_by(User.age.desc()).all()

# Pagination
page_number = 2
page_size = 10
offset = (page_number - 1) * page_size
users_on_page = session.query(User).offset(offset).limit(page_size).all()
```

**10. Advanced Queries:**

SQLAlchemy provides powerful tools for more complex queries, including subqueries, joins, and aggregation. Here's an example of a join between the `User` and `Post` models to get the author's username and their post count:

```python
from sqlalchemy import func

user_post_counts = session.query(User.username, func.count(Post.id)).\
    join(User.posts).\
    group_by(User.username).\
    all()
```

**11. Raw SQL Queries:**

While SQLAlchemy provides a powerful abstraction for working with databases, there might be situations where you need to execute raw SQL queries. SQLAlchemy allows you to execute raw SQL using the `text()` function and the `execute()` method. For example:

```python
from sqlalchemy import text

# Execute a raw SQL query
result = session.execute(text("SELECT username FROM users WHERE age > :age"), {"age": 30})
for row in result:
    print(row.username)
```

**12. Versioning and Auditing:**

In some applications, you may need to track changes to data over time or implement auditing. SQLAlchemy can be used to create versioning and auditing systems to keep track of historical data changes.

**13. Monitoring and Alerting:**

Implement database monitoring and alerting systems to detect and respond to performance issues or outages promptly. Tools like Prometheus and Grafana can help with this.

**14. Sharding and Replication:**

For high-traffic applications, you may need to consider database sharding and replication strategies to ensure scalability and fault tolerance.

**15. Error Handling:**

Properly handle exceptions that may arise during database operations. SQLAlchemy provides specific exception types that you can catch and handle gracefully, such as `sqlalchemy.exc.IntegrityError` for constraint violations.

**16. Security Best Practices:**

Ensure your database credentials and sensitive information are stored securely. Use environment variables or a configuration management system to keep this data safe. Apply proper access controls to your database to prevent unauthorized access.

**17. ORM vs. Raw SQL:**

While SQLAlchemy provides a convenient ORM, there may be cases where using raw SQL is more efficient, especially for complex queries or bulk inserts. Choose the approach that best suits your requirements.

**18. Cross-Database Compatibility:**

If you plan to support multiple database systems, be aware that not all features and SQL dialects are the same across different database engines. SQLAlchemy can abstract some differences, but you may need to write database-specific code for certain tasks.

**19. Data Migration Tools:**

Consider using data migration tools like Flask-Migrate for Flask applications or Alembic for general SQLAlchemy projects. These tools help manage changes to your database schema and make it easier to evolve your database over time.

**20. NoSQL Databases:**

While SQLAlchemy is primarily designed for relational databases, you can explore extensions and libraries that enable NoSQL database support (e.g., MongoDB or Cassandra) with SQLAlchemy.

**21. Schema Validation:**

Leverage SQLAlchemy tools and libraries for database schema validation and consistency checks to ensure your application's database matches the expected schema.

Remember, your specific project requirements and constraints may lead to different approaches, and it's essential to adapt your practices accordingly. Building and maintaining a successful database-backed application is an ongoing process that benefits from continuous improvement and staying informed about the latest developments in the field.


# SQLAlchemy Administration
Administrative tasks like initializing a database, updating the schema, and performing data migrations are essential for managing a database effectively. For our example, we'll be using `Flask-Migrate` for the DB Management. Here's a step-by-step guide on how to handle these administrative tasks:

**1. Initializing a Database:**

When starting a new project, you'll need to set up the database schema and tables. SQLAlchemy provides the capability to create and initialize a database schema.

First, ensure you have installed Flask-Migrate, which is a database migration tool often used with SQLAlchemy:

```bash
pip install Flask-Migrate
```

Next, create a directory for Flask-Migrate to store migration scripts:

```bash
flask db init
```

**2. Creating Initial Migration:**

Generate an initial migration to create the database schema:

```bash
flask db migrate -m "initial"
```

This command will create a migration script in the `versions` directory. You can customize this script to define the initial schema, create tables, and set up relationships.

**3. Applying Migrations:**

Apply the migration to create the database schema:

```bash
flask db upgrade
```

This command will execute the migration and create the initial schema in your SQLite database.

**4. Updating the Schema:**

As your application evolves, you may need to make changes to the database schema. To do this, create new migration scripts to reflect these changes.

**Creating a New Migration:**

Generate a new migration to capture the schema changes:

```bash
flask db migrate -m "Adding new table"
```

This creates a new migration script in the `versions` directory.

**Updating the Database:**

Apply the new migration to update the database schema:

```bash
flask db upgrade
```

This command will apply the changes defined in the new migration script to the database schema.

**5. Downgrading Migrations:**

Flask-Migrate also allows you to downgrade to a specific version or revert a migration to a previous state. This can be useful if you need to rollback changes.
```bash
flask db downgrade
```

**6. Version Control:**

To keep your database schema changes in version control, it's essential to store your Flask-Migrate migration scripts in a repository such as Git. This allows you to track and manage changes to your database schema over time.

By following these steps and using Flask-Migrate with Flask-SQLAlchemy, you can effectively manage database initialization, schema updates, and data migrations for your project. This approach helps maintain your database structure as your application evolves.

## Differences in administrative tasks for MySQL or PostgreSQL
The high-level administrative tasks for initializing a database, updating the schema, and performing data migrations are similar across various relational database management systems (RDBMS) like SQLite, MySQL, and PostgreSQL. However, there may be some specific considerations for each RDBMS.

Here's a brief overview of the tasks and potential differences for MySQL and PostgreSQL:

**1. Initializing a Database:**
   - The process for initializing a database is conceptually similar across different RDBMS. You need to create a database and set up tables.
   - The main difference is in the connection string (the database URL). You should specify the appropriate URL for MySQL or PostgreSQL in SQLAlchemy, which varies based on the RDBMS-specific drivers.

**2. Creating Initial Migration:**
   - The process of creating an initial migration using Flask-Migrate or a similar migration tool is essentially the same. You generate migration scripts based on the changes to the database schema.
   - The syntax for defining database-specific data types or constraints may differ between MySQL and PostgreSQL, and your migration scripts should reflect these differences.

**3. Applying Migrations:**
   - The commands for applying migrations using Flask-Migrate, such as `flask db upgrade`, are generally the same for MySQL and PostgreSQL.
   - However, there may be minor differences in the SQL generated by Flask-Migrate when applying migrations, as each RDBMS has its own SQL dialect.

**4. Downgrading Migrations:**
   - The process of downgrading migrations in Flask-Migrate is similar across RDBMS, but you should ensure that the downgrading scripts are correctly written for the specific RDBMS you're using.

**5. Data Migrations:**
   - Data migrations, such as transferring or transforming data, may have some database-specific considerations. For example, SQL queries used in data migrations might differ due to syntax variations between MySQL and PostgreSQL.

**6. Version Control:**
   - Storing migration scripts in version control (e.g., Git) is important for tracking database schema changes regardless of the RDBMS. The version control practices are the same for SQLite, MySQL, and PostgreSQL.

In summary, the core principles and tools for managing database administrative tasks are consistent across SQLite, MySQL, and PostgreSQL, but you should be aware of the specific nuances and differences in SQL dialects, data types, and constraints for each RDBMS. When working with SQLAlchemy, the database URL and certain database-specific aspects (e.g., sequences in PostgreSQL) may need to be considered in your migrations and schema updates.