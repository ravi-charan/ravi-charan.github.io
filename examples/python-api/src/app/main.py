from fastapi import FastAPI

app = FastAPI(title="Docker Learning API")


@app.get("/")
def home():
    return {"message": "The API is running in Docker"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
