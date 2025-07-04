from typing import Optional, List
from uuid import uuid4
from datetime import datetime, timezone
from enum import Enum, auto
import asyncio

from sqlalchemy import ForeignKey, String, Text, Boolean, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
import bcrypt

from config import settings


engine = create_async_engine(settings.sqlalchemy_uri, echo=True)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Role(Enum):
    user = auto()
    admin = auto()


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default=None)
    bio: Mapped[Optional[str]] = mapped_column(Text(), nullable=True, default=None)
    role: Mapped[Role] = mapped_column(default=Role.user.name)
    token: Mapped[Optional[str]] = mapped_column(String(100), default=None, nullable=True)
    articles: Mapped[List["Article"]] = relationship()

    def __init__(self, *args, **kwargs):
        self.id = uuid4().hex
        super().__init__(*args, **kwargs)

    @property
    def password(self):
        return self.password_

    @password.setter
    def password(self, pwd: str):
        self.password_ = bcrypt.hashpw(password=pwd.encode(), salt=bcrypt.gensalt())

    def is_verify_password(self, pwd: str):
        return bcrypt.checkpw(pwd.encode(), self.password_.encode())


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text())
    user_id: Mapped[str] = mapped_column(String(100), ForeignKey(User.id, ondelete="cascade"))
    tags: Mapped[List[str]] = mapped_column(String(20))
    published_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now(timezone.utc))
    comments: Mapped[List["Comment"]] = relationship()

    def __init__(self, *args, **kwargs):
        self.id = uuid4().hex
        super().__init__(*args, **kwargs)

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), ForeignKey(User.id, ondelete="cascade"))
    content: Mapped[str] = mapped_column(Text())
    create_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now(timezone.utc))
    article_id: Mapped[str] = mapped_column(String(100), ForeignKey(Article.id, ondelete="cascade"))

    def __init__(self, *args, **kwargs):
        self.id = uuid4().hex
        super().__init__(*args, **kwargs)

async def create_db():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with Session() as session:
        yield session


if __name__ == "__main__":
    asyncio.run(create_db())