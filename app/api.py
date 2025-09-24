# app/api.py
from fastapi import FastAPI

from app.routes import admin, auth, tasks

app = FastAPI(title="Todo API")

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(admin.router)

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
