from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from typing import Annotated

from app.database import SessionDep
import app.models as models
import app.schemas as schemas
from app.utils import verify
from app.oauth2 import create_access_token, get_current_user

router = APIRouter(
    tags=["Authorization"]
)

@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):

    stmt = select(models.User).where(models.User.email == form_data.username)
    user = session.scalar(stmt)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    data = {"sub": str(user.id)}

    access_token = create_access_token(data)

    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/me")
def get_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return {"current_user": current_user}






