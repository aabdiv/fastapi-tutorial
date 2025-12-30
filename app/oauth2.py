import jwt
from jwt import InvalidTokenError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from app.config import settings
from app.database import SessionDep
import app.schemas as schemas
import app.models as models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    access_token = jwt.encode(payload=to_encode, key=SECRET, algorithm=ALGORITHM)

    return access_token


credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                      detail="Could not validate credentials",
                                      headers={"WWW-Authenticate": "Bearer"})


def validate_access_token(access_token: str):
    #signature
    try:
        payload = jwt.decode(access_token, SECRET, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise credentials_exception
    
    # payload integrity
    if "sub" not in payload or "exp" not in payload:
        raise credentials_exception
    
    # expiration
    expire = payload.get("exp")
    current_time = datetime.now(timezone.utc).timestamp()
    if current_time > expire:
        raise credentials_exception
    
    sub = payload.get("sub")
    access_token_data = schemas.TokenData(sub=sub)

    return access_token_data


def get_current_user(access_token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    
    access_token_data = validate_access_token(access_token)

    # user in DB
    user_id = int(access_token_data.sub)
    user = session.get(models.User, user_id)
    if user is None:
        raise credentials_exception
    
    return user


CurrentUserDep = Annotated[models.User, Depends(get_current_user)]