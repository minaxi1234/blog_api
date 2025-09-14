from fastapi import Depends, HTTPException, status,APIRouter
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.post import Post
from app.models.user import User
from app.models.comment import Comment
from app.schemas.comment import CommentCreate,CommentBase, CommentResponse

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
  payload: CommentCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  post = db.query(Post).filter(Post.id == payload.post_id).first()
  if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
 
  new_comment = Comment(
        content=payload.content,
        post_id=payload.post_id,
        author_id=current_user.id
    )
  print("Creating comment:", payload.content, payload.post_id, current_user.id)
  db.add(new_comment)
  db.commit()
  db.refresh(new_comment)
  return new_comment

from fastapi import Query

@router.get("/", response_model=list[CommentResponse])
def list_comments(
    skip: int = 0,
    limit: int = 10,
    search: str | None = Query(None),
    sort_by: str = Query("id"),
    order: str = Query("asc"),
    db: Session = Depends(get_db)
):
    query = db.query(Comment)

    if search:
        query = query.filter(Comment.content.contains(search))

    valid_sort_columns = ["id", "created_at"]
    if sort_by not in valid_sort_columns:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by. Choose from {valid_sort_columns}")
    sort_column = getattr(Comment, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()
    
    comments = query.order_by(sort_column).offset(skip).limit(limit).all()
    return comments
        
    

@router.get("/{comment_id}", response_model= CommentResponse)
def get_comment(comment_id: int, db: Session= Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    payload: CommentBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this comment")

    comment.content = payload.content
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(comment)
    db.commit()
    return






