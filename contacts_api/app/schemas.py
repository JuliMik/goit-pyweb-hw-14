from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class ContactCreate(BaseModel):
    """
        Schema for input data when creating a new contact.

        :param first_name: str: Contact's first name.
        :param last_name: str: Contact's last name.
        :param email: EmailStr: Contact's email address (EmailStr is a special type for email validation).
        :param phone_number: str: Contact's phone number.
        :param birth_date: date: Contact's birth date.
        :param additional_info: Optional[str]: Optional additional information about the contact.

        :return: ContactCreate: The validated input data for creating a contact.
        """
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birth_date: date
    additional_info: Optional[str] = None


class ContactResponse(ContactCreate):
    """
        Schema for the response when retrieving a contact.

        :param id: int: Contact's unique identifier.
        :param first_name: str: Contact's first name.
        :param last_name: str: Contact's last name.
        :param email: EmailStr: Contact's email address.
        :param phone_number: str: Contact's phone number.
        :param birth_date: date: Contact's birth date.
        :param additional_info: Optional[str]: Optional additional information about the contact.

        :return: ContactResponse: The contact data including its unique identifier.
        """
    id: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """
        Schema for input data when registering a new user.

        :param email: EmailStr: User's email address.
        :param username: str: User's username.
        :param password: str: User's password.

        :return: UserCreate: The validated input data for creating a user.
        """
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    """
        Schema for the user response.

        :param id: int: User's unique identifier.
        :param email: EmailStr: User's email address.
        :param username: str: User's username.

        :return: UserResponse: The user data including its unique identifier and email.
        """
    id: int
    email: EmailStr
    username: str

    class Config:
        from_attributes = True
        orm_mode = True


class Token(BaseModel):
    """
        Schema for authentication tokens (typically for JWT).

        :param access_token: str: The access token issued for authentication.
        :param token_type: str: The type of the token (usually "bearer").

        :return: Token: The authentication token data.
        """
    access_token: str
    token_type: str
