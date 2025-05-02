from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Contact, User
from app.schemas import ContactCreate


def create_contact(db: Session, contact: ContactCreate, current_user: User):
    """
        Create a new contact associated with the current user.

        :param db: Session: SQLAlchemy session for database access
        :param contact: ContactCreate: The contact data from the request
        :param current_user: User: The currently authenticated user
        :return: The created contact object
        """
    db_contact = Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_all_contacts(db: Session, current_user: User):
    """
        Retrieve all contacts that belong to the current user.

        :param db: Session: SQLAlchemy session for database access
        :param current_user: User: The currently authenticated user
        :return: A list of the user's contacts
        """
    return db.query(Contact).filter(Contact.user_id == current_user.id).all()


def get_contact_by_id(contact_id: int, db: Session, current_user: User):
    """
        Retrieve a contact by its ID if it belongs to the current user.

        :param contact_id: int: ID of the contact to retrieve
        :param db: Session: SQLAlchemy session for database access
        :param current_user: User: The currently authenticated user
        :return: The contact object or None if not found
        """

    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()


def update_contact(contact_id: int, contact: ContactCreate, db: Session, current_user: User):
    """
        Update the details of a contact if it belongs to the user.

        :param contact_id: int: ID of the contact to update
        :param contact: ContactCreate: New contact data
        :param db: Session: SQLAlchemy session for database access
        :param current_user: User: The currently authenticated user
        :return: The updated contact object or None if not found
        """
    db_contact = get_contact_by_id(contact_id, db, current_user)
    if db_contact:
        for key, value in contact.model_dump().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
        return db_contact
    return None


def delete_contact(contact_id: int, db: Session, current_user: User):
    """
        Delete a contact if it belongs to the user.

        :param contact_id: int: ID of the contact to delete
        :param db: Session: SQLAlchemy session for database access
        :param current_user: User: The currently authenticated user
        :return: The deleted contact object or None if not found
        """
    db_contact = get_contact_by_id(contact_id, db, current_user)
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return db_contact
    return None


def search_contacts(first_name: str = None, last_name: str = None, email: str = None, db: Session = None,
                    current_user: User = None):
    """
        Search contacts by first name, last name, or email (partial matches allowed).

        :param first_name: str: First name to search by
        :param last_name: str: Last name to search by
        :param email: str: Email to search by
        :param db: Session: SQLAlchemy session for database access
        :param current_user: User: The currently authenticated user
        :return: A list of matching contacts
        """
    query = db.query(Contact).filter(Contact.user_id == current_user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    return query.all()


def get_upcoming_birthdays(db: Session, current_user: User):
    """
        Get contacts with birthdays in the next 7 days.

        :param db: Session: SQLAlchemy session for database access
        :param current_user: User: The currently authenticated user
        :return: A list of contacts with upcoming birthdays
        """
    today = datetime.today().date()
    end_date = today + timedelta(days=7)

    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).all()
    upcoming = []

    for contact in contacts:
        bday = contact.birth_date.replace(year=today.year)
        if today <= bday <= end_date:
            upcoming.append(contact)

    return upcoming
