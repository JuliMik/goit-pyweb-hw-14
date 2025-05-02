from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:567234@localhost:5432/contacts_db"

# Створення двигуна підключення
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Створення базового класу для моделей
Base = declarative_base()

# Створення сесії для роботи з базою даних
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Функція для отримання сесії
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
