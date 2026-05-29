import uvicorn
from fastapi import FastAPI
from api.query import router

app = FastAPI(title="DataSense AI")

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
