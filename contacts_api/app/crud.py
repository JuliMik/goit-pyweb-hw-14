from sqlalchemy.orm import Session
from . import models, schemas


def create_contact(db: Session, contact: schemas.ContactCreate):
    """
        Creates a new contact in the database.

        :param db: Session: SQLAlchemy database session.
        :param contact: schemas.ContactCreate: Contact data to create.
        :return: models.Contact: The created contact object.
        """
    db_contact = models.Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birth_date=contact.birth_date,
        additional_info=contact.additional_info
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    """
        Retrieves a list of contacts with optional pagination.

        :param db: Session: SQLAlchemy database session.
        :param skip: int: Number of records to skip (default 0).
        :param limit: int: Maximum number of records to return (default 100).
        :return: List[models.Contact]: List of contact objects.
        """
    return db.query(models.Contact).offset(skip).limit(limit).all()
