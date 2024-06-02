from fastapi import FastAPI
from contextlib import asynccontextmanager

from database import create_tables, delete_tables
from operations.operation_router import router as roll_router
from pages.page_router import router as pages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("База готова к работе")
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)
app.include_router(roll_router)
app.include_router(pages_router)

