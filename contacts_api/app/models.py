from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from app.database import Base
from sqlalchemy.orm import relationship


# Модель для збереження контактів користувача
class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    birth_date = Column(Date)
    additional_info = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="contacts")


# Модель для збереження користувачів
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    contacts = relationship("Contact", back_populates="user")
    confirmed = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
