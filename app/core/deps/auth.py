import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

from app.core.security.tokens import verify_token
from app.helpers.users import get_user_by_id
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    """
    middleware to get the current user based on the provided token.

    Parameters:
    - token (str): The JWT token provided by the client.
    - db (Session): The database session object from SQLAlchemy.

    Returns:
    - User: The user object if the token is valid and the user is verified.

    Raises:
    - HTTPException: If the token is invalid, expired, or the user is not verified.
    """

    # Define the exception to be raised when credentials are not valid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify the JWT token
        payload = verify_token(token, 'access')
        if payload is None:
            raise credentials_exception

        # Extract the email from the payload
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Extract the token type from the payload
        token_type: str = payload.get("type")
        if token_type != "access":
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    # Fetch the user from the database based on the email
    user = get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception

    # Return the user object
    return user
