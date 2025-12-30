from fastapi import APIRouter, status, HTTPException, Response

from app.database import SessionDep
import app.models as models
import app.schemas as schemas
from app.utils import hash

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserPublic)
def create_user(user: schemas.UserCreate, session: SessionDep):
    
    hashed_password = hash(user.password)
    user.password = hashed_password
    
    new_user = models.User(**user.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserPublic)
def get_user(id: int, session: SessionDep):

    user = session.get(models.User, id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"user with id {id} not found")
    
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, session: SessionDep):

    deleted_user = session.get(models.User, id)
    if deleted_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} not found")

    session.delete(deleted_user)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


