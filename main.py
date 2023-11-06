from fastapi import FastAPI

from routers.document_controller import router

app = FastAPI()
app.include_router(router)
