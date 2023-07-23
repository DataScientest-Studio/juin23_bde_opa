from fastapi import FastAPI
import os

from opa.storage import storage


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
