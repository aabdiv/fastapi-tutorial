from fastapi import APIRouter, status, HTTPException

from app.database import SessionDep
from app.oauth2 import CurrentUserDep
import app.models as models
import app.schemas as schemas

router = APIRouter(
    prefix="/votes",
    tags=["Votes"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(current_user: CurrentUserDep, session: SessionDep, vote: schemas.Vote):
    
    if session.get(models.Post, vote.post_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post {vote.post_id} not found")

    vote_in_db = session.get(models.Vote, (current_user.id, vote.post_id))
    print(f"HERE _______: {vote_in_db}")


    if vote_in_db is None:
        if vote.dir == True:
            new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
            session.add(new_vote)
            session.commit()
            return {"message": "successfully voted"}
        
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="vote does not exist, nothing to retract")

    else:
        if vote.dir == False:
            session.delete(vote_in_db)
            session.commit()
            return {"message": "vote retracted"}
        
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="vote already exists")

