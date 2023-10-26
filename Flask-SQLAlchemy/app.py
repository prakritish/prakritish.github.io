from flask import Flask
from flaskr import create_app, db

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
    