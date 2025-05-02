from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Request

from app.schemas import UserCreate, UserResponse
from app.repository import users
from app.database import get_db
from app.auth.security import create_access_token, create_refresh_token, get_current_user, hash_password
from app import schemas, models
from app.services.auth import verify_email_token
from app.repository.users import update_user_email_confirmation
from app.services.mail import send_confirmation_email
from pydantic import EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
        Registers a new user if the email is not already used.

        :param user: UserCreate: The user registration data.
        :param db: Session: SQLAlchemy database session.
        :return: UserResponse: The created user object.
        :raises HTTPException: If the email is already in use.
        """
    created_user = users.create_user(user, db)
    if not created_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    return created_user


@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
        Authenticates a user and returns access and refresh tokens.

        :param user: UserCreate: The user's login credentials.
        :param db: Session: SQLAlchemy database session.
        :return: dict: Tokens and token type if successful.
        :raises HTTPException: If authentication fails.
        """
    db_user = users.authenticate_user(user.email, user.password, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """
        Retrieves the current authenticated user.

        :param current_user: User: The authenticated user retrieved via dependency injection.
        :return: UserResponse: The user object.
        """
    return current_user


@router.get('/confirm-email/{token}')
async def confirm_email(token: str, db: Session = Depends(get_db)):
    """
        Confirms a user's email address using a verification token.

        :param token: str: The email confirmation token.
        :param db: Session: SQLAlchemy database session.
        :return: dict: Success message upon confirmation.
        :raises HTTPException: If user is not found.
        """
    email = verify_email_token(token)
    user = update_user_email_confirmation(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Email successfully confirmed"}


@router.post("/register")
async def register_user(request: Request, email: EmailStr, username: str, password: str, db: Session = Depends(get_db)):
    """
        Registers a new user and sends a confirmation email.

        :param request: Request: The FastAPI request object for constructing host.
        :param email: EmailStr: The user's email address.
        :param username: str: The desired username.
        :param password: str: The plain text password.
        :param db: Session: SQLAlchemy database session.
        :return: dict: Message indicating user creation and email sent.
        :raises HTTPException: If the email is already registered.
        """
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    hashed_password = hash_password(password)
    new_user = models.User(email=email, username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()

    host = "http://localhost:8000"
    await send_confirmation_email(request, email=email, username=username, host=host)

    return {"message": "User created. Check your email to confirm."}
