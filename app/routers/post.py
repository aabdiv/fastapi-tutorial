from fastapi import APIRouter, status, HTTPException, Response, Depends
from sqlalchemy import select, func
from typing import Annotated

from app.database import SessionDep
import app.models as models
import app.schemas as schemas
from app.utils import password_hash
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=list[schemas.PostPublicWithVotes])
def get_posts(
    current_user: Annotated[models.User, Depends(get_current_user)],
    session: SessionDep,
    limit: int = 10,
    skip: int = 0,
    search: str = ""
):

    stmt = select(
        models.Post,
        func.count(models.Vote.user_id).label("votes")
    ).join(
        models.Vote,
        models.Post.id == models.Vote.post_id,
        isouter=True
    ).where(
        models.Post.title.contains(search)
    ).group_by(models.Post.id).limit(limit).offset(skip)
    
    posts = session.execute(stmt).all()

    return posts


@router.get("/{id}", response_model=schemas.PostPublicWithVotes)
def get_post(current_user: Annotated[models.User, Depends(get_current_user)], id: int, session: SessionDep):

    if session.get(models.Post, id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post with id {id} not found")
    
    stmt = select(
        models.Post,
        func.count(models.Vote.user_id).label("votes")
    ).join(
        models.Vote,
        models.Post.id == models.Vote.post_id,
        isouter=True
    ).where(
        models.Post.id == id
    ).group_by(models.Post.id)

    post = session.execute(stmt).first()

    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostPublic)
async def create_posts(
    current_user: Annotated[models.User, Depends(get_current_user)],
    post: schemas.PostCreate, session: SessionDep
):

    new_post = models.Post(user_id=current_user.id, **post.model_dump())
    session.add(new_post)
    session.commit()
    session.refresh(new_post)

    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(current_user: Annotated[models.User, Depends(get_current_user)], id: int, session: SessionDep):

    deleted_post = session.get(models.Post, id)
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    
    if current_user.id != deleted_post.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User not authorized for requested action")
    
    session.delete(deleted_post)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostPublic)
def update_post(current_user: Annotated[models.User, Depends(get_current_user)], id: int, post: schemas.PostCreate, session: SessionDep):

    updated_post = session.get(models.Post, id)
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    
    if current_user.id != updated_post.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User not authorized for requested action")
    
    for column, value in post.model_dump().items():
        setattr(updated_post, column, value)
    session.commit()
    session.refresh(updated_post)

    return updated_post


