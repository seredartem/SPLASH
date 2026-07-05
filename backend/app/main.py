from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine
from app.routers.auth import router as auth_router
from app.routers.classes import router as classes_router

app = FastAPI(title='Splash API')
app.include_router(auth_router)
app.include_router(classes_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get('/db-check')
async def db_check():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        return {"result": result.scalar()}
    
