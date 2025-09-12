# run.py
"""Entry point for the app & Flask CLI."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
