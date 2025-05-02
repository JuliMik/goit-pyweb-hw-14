from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from app.auth.security import hash_password


def create_user(user: UserCreate, db: Session):
    """
        Creates a new user if the email is not already registered.

        :param user: UserCreate: The user registration data.
        :param db: Session: SQLAlchemy database session.
        :return: The created user object, or None if the email is already in use.
        """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return None  # Користувач з таким email вже існує
    new_user = User(email=user.email, username=user.username, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(email: str, password: str, db: Session):
    """
        Authenticates a user by email and password.

        :param email: str: The email of the user trying to log in.
        :param password: str: The plain text password provided by the user.
        :param db: Session: SQLAlchemy database session.
        :return: The authenticated user object or None if authentication fails.
        """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    from app.auth.security import verify_password
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Функція для підтвердження email користувача
def update_user_email_confirmation(db: Session, email: str):
    """
        Confirms a user's email by setting the confirmed flag to True.

        :param db: Session: SQLAlchemy database session.
        :param email: str: The email address to confirm.
        :return: The updated user object or None if user not found.
        """
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.confirmed = True
        db.commit()
        db.refresh(user)
        return user
    return None


# Функція для оновлення аватара користувача
def update_user_avatar(db: Session, user: User, avatar_url: str):
    """
        Updates the avatar URL for the given user.

        :param db: Session: SQLAlchemy database session.
        :param user: User: The user object whose avatar is to be updated.
        :param avatar_url: str: The new URL of the user's avatar.
        :return: The updated user object.
        :raises HTTPException: If the user is not found in the database.
        """
    user_db = db.query(User).filter(User.id == user.id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_db.avatar = avatar_url
    db.commit()
    db.refresh(user_db)
    return user_db