from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import os

app = FastAPI(title="YouTube Analyzer Test")

@app.get("/")
async def root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    else:
        return {"message": "YouTube Analyzer Test Server", "status": "running"}

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Server is working!"}

if __name__ == "__main__":
    print("Starting test server on http://127.0.0.1:8000")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="127.0.0.1", port=8000)