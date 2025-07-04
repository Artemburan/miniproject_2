from fastapi import FastAPI
import uvicorn

from users_routes import users_route


app = FastAPI()
app.include_router(users_route)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)