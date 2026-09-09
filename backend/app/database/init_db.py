from app.database.database import Base, engine
from app.database.models import Rule


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()