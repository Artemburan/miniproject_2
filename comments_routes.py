from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Comment, get_db, User, Article
from users_routes import get_user
from pydantic import BaseModel


comments_route = APIRouter(prefix="/comments", tags=["Comments"])


class CommentCreate(BaseModel):
    article_id: str
    content: str


class CommentResponse(BaseModel):
    id: str
    content: str
    create_at: str
    user_id: str
    article_id: str


@comments_route.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(comment_data: CommentCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_user)):
    # перевіримо чи існує стаття
    result = await db.execute(select(Article).filter_by(id=comment_data.article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статтю не знайдено")

    comment = Comment(
        content=comment_data.content,
        article_id=comment_data.article_id,
        user_id=user.id
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        create_at=str(comment.create_at),
        user_id=comment.user_id,
        article_id=comment.article_id
    )


@comments_route.get("/article/{article_id}", response_model=List[CommentResponse])
async def get_comments_for_article(article_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).filter_by(article_id=article_id))
    comments = result.scalars().all()
    return [
        CommentResponse(
            id=c.id,
            content=c.content,
            create_at=str(c.create_at),
            user_id=c.user_id,
            article_id=c.article_id
        ) for c in comments
    ]
