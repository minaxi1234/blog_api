import time
import os
from fastapi import APIRouter, Depends, HTTPException, Request,status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.models.post import Post
from app. models.user import User
from typing import Optional
from app.core.dependencies import get_db, get_current_user, require_role
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles



router = APIRouter(
  prefix="/posts",
  tags=["Posts"]
)

UPLOAD_DIR = "uploads"


posts_cache = {
  "data": None,
  "timestamp": 0
}

post_detail_cache = {}
CACHE_EXPIRE_SECONDS = 30

def send_email_notification(email_to: str, post_title: str):
  print(f"Sending email to {email_to}: your post '{post_title}' was created!")

@router.post("/", response_model=PostResponse)
def create_post(
  post: PostCreate,
  background_tasks: BackgroundTasks,
  db:Session= Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  new_post = Post(
    title= post.title,
    content= post.content,
    author_id= current_user.id
  )
  db.add(new_post)
  db.commit()
  db.refresh(new_post)

  background_tasks.add_task(send_email_notification, current_user.email, new_post.title)

  return new_post

@router.get("/", response_model=list[PostResponse])
def list_posts(
  skip: int = 0,
  limit: int = 10,
  search: Optional[str] = Query(None),
  sort_by: Optional[str] = Query("id"),
  order: Optional[str] = Query("asc"),
  db: Session = Depends(get_db)
):
  
  now= time.time()
  if posts_cache["data"] and now -posts_cache["timestamp"] < CACHE_EXPIRE_SECONDS:
    return posts_cache["data"]
  
  query = db.query(Post)

  # search
  if search:
    query = query.filter(Post.title.contains(search))

  # sorting
  valid_sort_columns = ["id", "title", "created_at"]
  if sort_by not in valid_sort_columns:
    raise HTTPException(status_code=400, detail=f"Invalid sort_by value. Choose from {valid_sort_columns}")
  sort_column = getattr(Post, sort_by)
  if order == "desc":
    sort_column = sort_column.desc()
  else:
    sort_column = sort_column.asc()
  query = query.order_by(sort_column)
  
  posts = query.offset(skip).limit(limit).all()

  posts_cache["data"] = posts
  posts_cache["timestamp"] = now

  return posts

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id : int, db: Session = Depends(get_db),request: Request = None):
  now = time.time()
  
  cached = post_detail_cache.get(post_id)
  if cached and (now - cached["timestamp"]) < CACHE_EXPIRE_SECONDS:
        post = cached["data"]
        # if the response needs a public file URL, build it using the request
        if getattr(post, "file_path", None) and request:
            filename = os.path.basename(post.file_path)
            post.file_path = str(request.url_for("uploads", path=filename))
        return post

    # 2) Not in cache or expired -> fetch from DB
  post = db.query(Post).filter(Post.id == post_id).first()
  if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with {post_id} not found"
        )

    # Build file URL if needed
  if getattr(post, "file_path", None) and request:
        filename = os.path.basename(post.file_path)
        post.file_path = str(request.url_for("uploads", path=filename))

    # 3) Store in detail cache
  post_detail_cache[post_id] = {"data": post, "timestamp": now}

  return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
  post_id: int,
  post_update:PostUpdate,
  db: Session = Depends(get_db),
  current_user:  User = Depends(get_current_user)
):
  post = db.query(Post).filter(Post.id == post_id).first()

  if not post:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Post with id {post_id} not found"
    )
  if  post.author_id != current_user.id:
    raise HTTPException(
      status_code= status.HTTP_403_FORBIDDEN,
      detail="You do not have permission to update this post"
    )
  if post_update.title is not None:
    post.title = post_update.title
  if post_update.content is not None:
    post.content = post_update.content


  db.commit()
  db.refresh(post)
  return post

@router.delete("/{post_id}")
def delete_post(
  post_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  post = db.query(Post).filter(Post.id == post_id).first()

  if not post:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Post with id {post_id} not found"
    )
  if post.author_id != current_user.id:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="You do not have permission to delete this post"
    )
    
  db.delete(post)
  db.commit()
  return {"message": f"your post with {post_id} has been deleted"}

@router.get("/admin/secret/" )
def get_admin_secret(current_user: User = Depends(require_role("admin"))):
  return {"message": f"Hello {current_user.username}, you are an admin!"}

@router.post("/upload/{post_id}")
def upload_file(post_id: int, file:UploadFile = File(...),db:Session=Depends(get_db)):
  post= db.query(Post).filter(Post.id == post_id).first()
  if not post:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Post with id {post_id} not found"
    )
  
  file_path = os.path.join(UPLOAD_DIR, file.filename)
  with open(file_path, "wb") as buffer:
    buffer.write(file.file.read())

  post.file_path = file_path
  db.commit()
  db.refresh(post)
  return {"id": post.id, "title": post.title, "file_path": post.file_path}








