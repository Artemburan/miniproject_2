from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Article, get_db, User
from users_routes import get_user
from pydantic import BaseModel


articles_route = APIRouter(prefix="/articles", tags=["Articles"])


class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: List[str]


class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str]
    published_at: str
    user_id: str


@articles_route.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(article_data: ArticleCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_user)):
    article = Article(
        title=article_data.title,
        content=article_data.content,
        tags=",".join(article_data.tags),
        user_id=user.id
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        tags=article.tags.split(","),
        published_at=str(article.published_at),
        user_id=article.user_id
    )


@articles_route.get("/", response_model=List[ArticleResponse])
async def get_all_articles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Article))
    articles = result.scalars().all()
    return [
        ArticleResponse(
            id=a.id,
            title=a.title,
            content=a.content,
            tags=a.tags.split(","),
            published_at=str(a.published_at),
            user_id=a.user_id
        )
        for a in articles
    ]


@articles_route.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Article).filter_by(id=article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Статтю не знайдено")
    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        tags=article.tags.split(","),
        published_at=str(article.published_at),
        user_id=article.user_id
    )


@articles_route.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_user)):
    result = await db.execute(select(Article).filter_by(id=article_id))
    article = result.scalar_one_or_none()
    if not article or article.user_id != user.id:
        raise HTTPException(status_code=403, detail="Немає доступу або статтю не знайдено")
    await db.delete(article)
    await db.commit()
