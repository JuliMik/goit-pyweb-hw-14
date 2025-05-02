from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app import schemas, models, database
from app.schemas import ContactResponse, ContactCreate, UserResponse
from app.repository import contacts
from app.auth.security import get_current_user
from app.models import User
from fastapi_limiter.depends import RateLimiter
from app.repository.users import update_user_avatar
from app.services import cloudinary_config
import cloudinary.uploader


router = APIRouter(prefix="/contacts", tags=["Contacts"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/search", response_model=List[ContactResponse])
def search_contacts(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Search contacts by first name, last name, or email.

        :param first_name: Optional[str]: Contact's first name.
        :param last_name: Optional[str]: Contact's last name.
        :param email: Optional[str]: Contact's email.
        :param db: Session: SQLAlchemy session.
        :param current_user: User: Authenticated user.
        :return: List[ContactResponse]: List of matched contacts.
        """
    return contacts.search_contacts(first_name, last_name, email, db, current_user)


@router.post("/", response_model=ContactResponse, status_code=201, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def create_contact(
        contact: ContactCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Create a new contact for the authenticated user.

        :param contact: ContactCreate: Data for the new contact.
        :param db: Session: SQLAlchemy session.
        :param current_user: User: Authenticated user.
        :return: ContactResponse: The created contact.
        """
    return contacts.create_contact(db, contact, current_user)


@router.get("/{contact_id}", response_model=ContactResponse)
def read_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Retrieve a contact by ID.

        :param contact_id: int: ID of the contact.
        :param db: Session: SQLAlchemy session.
        :param current_user: User: Authenticated user.
        :return: ContactResponse: The requested contact.
        :raises HTTPException: If contact is not found.
        """
    contact = contacts.get_contact_by_id(contact_id, db, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/", response_model=List[ContactResponse])
def get_contacts(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Retrieve all contacts for the authenticated user.

        :param db: Session: SQLAlchemy session.
        :param current_user: User: Authenticated user.
        :return: List[ContactResponse]: List of user's contacts.
        """
    return contacts.get_all_contacts(db, current_user)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
        contact_id: int,
        contact: ContactCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Update an existing contact.

        :param contact_id: int: ID of the contact to update.
        :param contact: ContactCreate: New contact data.
        :param db: Session: SQLAlchemy session.
        :param current_user: User: Authenticated user.
        :return: ContactResponse: Updated contact data.
        :raises HTTPException: If contact is not found.
        """
    updated = contacts.update_contact(contact_id, contact, db, current_user)
    if updated is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated


@router.delete("/{contact_id}", response_model=schemas.ContactResponse)
def delete_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Delete a contact by ID.

        :param contact_id: int: ID of the contact to delete.
        :param db: Session: SQLAlchemy session.
        :param current_user: User: Authenticated user.
        :return: ContactResponse: Deleted contact data.
        :raises HTTPException: If contact is not found.
        """
    db_contact = contacts.get_contact_by_id(contact_id, db, current_user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(db_contact)
    db.commit()
    return db_contact


@router.get("/birthdays/", response_model=List[schemas.ContactResponse])
def upcoming_birthdays(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Retrieve contacts with birthdays in the next 7 days.

        :param db: Session: SQLAlchemy session.
        :param current_user: User: Authenticated user.
        :return: List[ContactResponse]: List of contacts with upcoming birthdays.
        """
    return contacts.get_upcoming_birthdays(db, current_user)


# Завантаження аватару
@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
        Upload and update the user's avatar using Cloudinary.

        :param file: UploadFile: The image file uploaded by the user.
        :param db: Session: SQLAlchemy session.
        :param current_user: User: Authenticated user.
        :return: UserResponse: Updated user object with avatar URL.
        """
    cloudinary.config(
        cloud_name='drvywa07y',
        api_key='269691335265889',
        api_secret='7GLVk7GAjdKsWNkPhv2roSM2Kpg',
        secure=True
    )

    file.file.seek(0)

    result = cloudinary.uploader.upload(file.file, folder="avatars", public_id=str(current_user.id))
    avatar_url = result.get("secure_url")
    user = update_user_avatar(db, current_user, avatar_url)

    return user
