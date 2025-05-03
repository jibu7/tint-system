import os
from app import create_app, db
from app.models import Formulation, ColorantDetail

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized.")

if __name__ == "__main__":
    app.run(debug=True)
