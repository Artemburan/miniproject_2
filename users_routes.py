from typing import List, Optional, Annotated
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models import User, get_db
from pydantic_models import UserModel, UserModelResponse, TokenModel


users_route = APIRouter(prefix="/users", tags=["User"])


async def get_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/users/token/")), db: AsyncSession = Depends(get_db)) -> User:
    query = select(User).filter_by(token=token)
    result = await db.execute(query)
    user: Optional[User] = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неавторизований користувач")

    return user


@users_route.post("/", status_code=status.HTTP_201_CREATED)
async def sign_up(user_model: UserModel, db: AsyncSession = Depends(get_db)):
    query = select(User).filter_by(username=user_model.username)
    result = await db.execute(query)
    user: Optional[User] = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Такий користувач вже зареєстрований")

    user = User(**user_model.model_dump())
    db.add(user)
    await db.commit()


@users_route.post("/token/", status_code=status.HTTP_202_ACCEPTED, response_model=TokenModel)
async def sign_in(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    query = select(User).filter_by(username=form.username)
    result = await db.execute(query)
    user: Optional[User] = result.scalar_one_or_none()
    if not user or not user.is_verify_password(form.password) or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    token = uuid4().hex
    user.token = token
    await db.commit()
    return dict(access_token=token)


@users_route.get("/me/", status_code=status.HTTP_202_ACCEPTED, response_model=UserModelResponse)
async def get_me(user: User = Depends(get_user)):
    return user